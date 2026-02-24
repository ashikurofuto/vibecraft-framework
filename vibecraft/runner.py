"""
SkillRunner v0.2

Flow per skill step:
  1. Build prompt (skill config + agent md + context files)
  2. Call Qwen via adapter (streams output live)
  3. Save output to target path
  4. If gate: human_approval → show output, ask y/n/edit/retry
  5. On fail → loop back with max_retries
  6. Update manifest after skill completes
"""

import os
import subprocess
from pathlib import Path

import yaml

from .adapters.qwen_adapter import QwenAdapter
from .context_manager import ContextManager

CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"


def _c(color: str, text: str) -> str:
    return f"{color}{text}{RESET}"


def _hr(width: int = 60) -> str:
    return "─" * width


class SkillRunner:
    def __init__(self, project_root: Path):
        self.root        = project_root
        self.vc_dir      = project_root / ".vibecraft"
        self.docs_dir    = project_root / "docs"
        self.src_dir     = project_root / "src"
        self.adapter     = QwenAdapter(stream=True)
        self.ctx_manager = ContextManager(project_root)

    # ------------------------------------------------------------------ #
    #  Public                                                              #
    # ------------------------------------------------------------------ #

    def run(self, skill_name: str, phase: int | None = None):
        skill = self._load_skill(skill_name)
        if skill is None:
            return

        print(_c(BOLD + CYAN, f"\n{'═'*60}"))
        print(_c(BOLD + CYAN, f"  Vibecraft ▸ {skill.get('name', skill_name)}"))
        if phase:
            print(_c(CYAN, f"  Phase {phase}"))
        print(_c(BOLD + CYAN, f"{'═'*60}\n"))

        steps = skill.get("steps", [])

        for idx, step in enumerate(steps):
            ok = self._run_step(
                step=step,
                step_number=idx + 1,
                total_steps=len(steps),
                skill=skill,
                phase=phase,
            )
            if not ok:
                print(_c(YELLOW, "\n  Skill aborted.\n"))
                return

        self.ctx_manager.complete_skill(skill_name, phase)
        print(_c(BOLD + GREEN, f"\n  ✓ Skill '{skill_name}' complete.\n"))
        print(_c(DIM, "  Run 'vibecraft status' to see updated progress.\n"))

    # ------------------------------------------------------------------ #
    #  Step execution                                                      #
    # ------------------------------------------------------------------ #

    def _run_step(
        self,
        step: dict,
        step_number: int,
        total_steps: int,
        skill: dict,
        phase: int | None,
        retry_count: int = 0,
    ) -> bool:
        name   = step.get("name", step.get("agent", f"step_{step_number}"))
        agent  = step.get("agent", "")
        gate   = step.get("gate")
        output = step.get("output", "")
        max_retries = (
            step.get("on_fail", {}).get("max_retries", 3)
            if isinstance(step.get("on_fail"), dict) else 3
        )

        print(_c(BOLD, f"  Step {step_number}/{total_steps}: {name}"))
        print(_c(DIM,  f"  Agent: {agent}\n  {_hr()}"))

        prompt = self._build_step_prompt(step, skill, phase)

        # Save prompt for reference/debugging
        prompt_path = self.vc_dir / f"last_prompt_{name}.md"
        prompt_path.write_text(prompt)
        print(_c(DIM, f"  Prompt → .vibecraft/last_prompt_{name}.md\n"))

        # Call Qwen
        print(_c(CYAN, f"  ▶ Running {agent}...\n"))
        print(_c(DIM, _hr()))

        try:
            response = self.adapter.call(prompt)
        except RuntimeError as e:
            print(_c(RED, f"\n  ✗ Qwen error: {e}\n"))
            return self._handle_error(step, step_number, total_steps, skill, phase, retry_count, max_retries)

        print(_c(DIM, f"\n  {_hr()}"))

        # Save output
        output_path = self._resolve_output_path(output, phase)
        if output_path:
            self._save_output(response, output_path, step)

        # Gate
        if gate == "human_approval":
            return self._human_gate(
                step=step, step_number=step_number, total_steps=total_steps,
                skill=skill, phase=phase, response=response,
                output_path=output_path, retry_count=retry_count, max_retries=max_retries,
            )

        return True

    # ------------------------------------------------------------------ #
    #  Human gate                                                          #
    # ------------------------------------------------------------------ #

    def _human_gate(
        self,
        step: dict,
        step_number: int,
        total_steps: int,
        skill: dict,
        phase: int | None,
        response: str,
        output_path: Path | None,
        retry_count: int,
        max_retries: int,
    ) -> bool:
        print(f"\n{_c(BOLD + YELLOW, '  ⚠  GATE — Human approval required')}")
        print(_c(DIM, _hr()))

        # Show what was generated
        if output_path:
            if output_path.is_dir():
                files = [f for f in output_path.rglob("*") if f.is_file()]
                print(_c(CYAN, f"\n  Generated {len(files)} file(s):"))
                for f in files:
                    print(f"    {_c(DIM, str(f.relative_to(self.root)))}")
            elif output_path.is_file():
                print(_c(CYAN, f"\n  Generated: {output_path.relative_to(self.root)}"))

        print(f"\n  {_c(BOLD, '[y]')} Approve  — continue")
        print(f"  {_c(BOLD, '[n]')} Reject   — abort skill")
        print(f"  {_c(BOLD, '[e]')} Edit     — open in $EDITOR, then continue")
        print(f"  {_c(BOLD, '[r]')} Retry    — re-run this step  "
              f"{_c(DIM, f'({retry_count}/{max_retries} retries used)')}\n")

        while True:
            try:
                raw = input(_c(BOLD, "  Decision [y/n/e/r]: ")).strip().lower()
            except (KeyboardInterrupt, EOFError):
                print()
                return False

            if raw in ("y", "yes", ""):
                print(_c(GREEN, "\n  ✓ Approved — continuing.\n"))
                return True

            elif raw in ("n", "no"):
                print(_c(RED, "\n  ✗ Rejected — aborting skill.\n"))
                return False

            elif raw in ("e", "edit"):
                self._open_in_editor(output_path)
                print(_c(GREEN, "\n  ✓ Edit saved — continuing.\n"))
                return True

            elif raw in ("r", "retry"):
                if retry_count >= max_retries:
                    print(_c(RED, f"\n  Max retries ({max_retries}) reached.\n"))
                    force = input(_c(YELLOW, "  Force approve anyway? [y/n]: ")).strip().lower()
                    return force in ("y", "yes")

                print(_c(YELLOW, f"\n  Retrying ({retry_count + 1}/{max_retries})...\n"))
                return self._run_step(
                    step=step, step_number=step_number, total_steps=total_steps,
                    skill=skill, phase=phase, retry_count=retry_count + 1,
                )

            else:
                print(_c(DIM, "  Enter y, n, e, or r."))

    # ------------------------------------------------------------------ #
    #  Prompt building                                                     #
    # ------------------------------------------------------------------ #

    def _build_step_prompt(self, step: dict, skill: dict, phase: int | None) -> str:
        parts = []
        agent_name  = step.get("agent", "")
        description = step.get("description", "")

        parts.append(f"# Vibecraft — {skill.get('name', 'Skill')} / {step.get('name', agent_name)}\n")

        # Agent system prompt
        agent_path = self.vc_dir / "agents" / f"{agent_name}.md"
        if agent_path.exists():
            parts.append("---\n## Your Role\n")
            parts.append(agent_path.read_text())

        # Project context
        context_path = self.docs_dir / "context.md"
        if context_path.exists():
            parts.append("\n---\n## Project Context\n")
            parts.append(context_path.read_text())

        # Stack (always)
        stack_path = self.docs_dir / "stack.md"
        if stack_path.exists():
            parts.append("\n---\n## Stack\n")
            parts.append(stack_path.read_text())

        # Research — early phase agents
        if agent_name in ("researcher", "architect", "planner"):
            research_path = self.docs_dir / "research.md"
            if research_path.exists():
                parts.append("\n---\n## Research\n")
                parts.append(research_path.read_text())

        # Architecture — implementation and review agents
        if agent_name in ("implementer", "tdd_writer", "code_reviewer", "plan_reviewer"):
            arch_path = self.docs_dir / "design" / "architecture.md"
            if arch_path.exists():
                parts.append("\n---\n## Architecture\n")
                parts.append(arch_path.read_text())

        # Phase plan
        if phase is not None:
            plan_path = self.docs_dir / "plans" / f"phase_{phase}.md"
            if plan_path.exists():
                parts.append(f"\n---\n## Plan: Phase {phase}\n")
                parts.append(plan_path.read_text())

            # Existing tests for implementer — attach as read-only
            if agent_name == "implementer":
                tests_dir = self.src_dir / "tests" / f"phase_{phase}"
                if tests_dir.exists():
                    parts.append("\n---\n## Existing Tests — DO NOT MODIFY\n")
                    for tf in sorted(tests_dir.rglob("*")):
                        if tf.is_file():
                            parts.append(f"\n### {tf.name}\n```\n{tf.read_text()}\n```\n")

        # Reads — other referenced files
        reads = step.get("reads", [])
        if isinstance(reads, str):
            reads = [reads]
        for r in reads:
            rp = self.root / r
            if rp.is_file():
                parts.append(f"\n---\n## Reference: {r}\n{rp.read_text()}")

        # Constraints
        constraints = skill.get("constraints", [])
        if constraints:
            parts.append("\n---\n## Constraints — strictly follow these\n")
            for c in constraints:
                parts.append(f"- {c}")

        # Task
        if description:
            parts.append(f"\n---\n## Your Task\n{description}")

        # Output path instruction
        output = step.get("output", "")
        if output:
            resolved = self._resolve_output_path(output, phase)
            parts.append(f"\n\n**Save your output to:** `{resolved}`")

        return "\n".join(parts)

    # ------------------------------------------------------------------ #
    #  Output saving                                                       #
    # ------------------------------------------------------------------ #

    def _resolve_output_path(self, output_str: str, phase: int | None) -> Path | None:
        if not output_str:
            return None
        if phase is not None:
            output_str = output_str.replace("{{phase}}", str(phase))
        return self.root / output_str

    def _save_output(self, response: str, output_path: Path, step: dict):
        constraint = step.get("constraint", {})
        immutable  = constraint.get("immutable") if isinstance(constraint, dict) else None

        if output_path.suffix == "":
            # Directory output
            output_path.mkdir(parents=True, exist_ok=True)
            target = output_path / "output.md"
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            target = output_path

        # Immutability guard
        if immutable:
            immutable_path = self.root / immutable
            if immutable_path.exists() and self._is_inside(target, immutable_path):
                print(_c(RED, f"\n  ✗ BLOCKED — {target} is inside immutable path: {immutable}\n"))
                return

        target.write_text(response, encoding="utf-8")
        print(_c(DIM, f"  Saved → {target.relative_to(self.root)}"))

    def _is_inside(self, path: Path, parent: Path) -> bool:
        try:
            path.resolve().relative_to(parent.resolve())
            return True
        except ValueError:
            return False

    # ------------------------------------------------------------------ #
    #  Editor                                                              #
    # ------------------------------------------------------------------ #

    def _open_in_editor(self, path: Path | None):
        editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "nano"))
        if path is None:
            return

        target = path if path.is_file() else (path / "output.md")
        if not target.exists():
            print(_c(YELLOW, f"  File not found: {target}"))
            return

        print(_c(DIM, f"  Opening in {editor}..."))
        subprocess.run([editor, str(target)])

    # ------------------------------------------------------------------ #
    #  Error / retry                                                       #
    # ------------------------------------------------------------------ #

    def _handle_error(self, step, step_number, total_steps, skill, phase, retry_count, max_retries) -> bool:
        if retry_count >= max_retries:
            print(_c(RED, "  Max retries reached. Aborting."))
            return False
        raw = input(_c(YELLOW, f"  Retry? [y/n] ({retry_count}/{max_retries}): ")).strip().lower()
        if raw in ("y", "yes", ""):
            return self._run_step(
                step=step, step_number=step_number, total_steps=total_steps,
                skill=skill, phase=phase, retry_count=retry_count + 1,
            )
        return False

    # ------------------------------------------------------------------ #
    #  Skill loading                                                       #
    # ------------------------------------------------------------------ #

    def _load_skill(self, skill_name: str) -> dict | None:
        for name in (f"{skill_name}_skill.yaml", f"{skill_name}.yaml"):
            p = self.vc_dir / "skills" / name
            if p.exists():
                return yaml.safe_load(p.read_text())

        print(_c(RED, f"\n  Skill not found: '{skill_name}'\n"))
        skills = list((self.vc_dir / "skills").glob("*.yaml"))
        if skills:
            print("  Available:")
            for s in skills:
                print(f"    {_c(CYAN, s.stem)}")
        return None
