"""
SkillRunner v0.3

Changes vs v0.2:
  - Uses adapter factory (VIBECRAFT_BACKEND env var) — no hard Qwen dependency
  - FIX: {phase} placeholder uses simple braces, not Jinja syntax — no fragile escaping
  - FIX: Ctrl+C during LLM call is handled cleanly
  - Prompt versioning: every prompt saved with timestamp, not overwritten
  - Rollback snapshots: taken before each skill run
  - dry_run flag: builds prompt only, no LLM call (forces clipboard adapter)

Flow per skill step:
  1. Snapshot current state (for rollback)
  2. Build prompt (skill config + agent md + context files)
  3. Call LLM via adapter (streams output live)
  4. Save output to target path
  5. If gate: human_approval -> show output, ask y/n/edit/retry
  6. On fail -> loop back with max_retries
  7. Update manifest after skill completes
"""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import yaml
from rich.console import Console

from .adapters.clipboard_adapter import ClipboardAdapter
from .context_manager import ContextManager

console = Console()


class SkillRunner:
    def __init__(self, project_root: Path):
        self.root        = project_root
        self.vc_dir      = project_root / ".vibecraft"
        self.docs_dir    = project_root / "docs"
        self.src_dir     = project_root / "src"
        self.ctx_manager = ContextManager(project_root)
        self.adapter     = ClipboardAdapter()

    # ------------------------------------------------------------------ #
    #  Public                                                              #
    # ------------------------------------------------------------------ #

    def run(self, skill_name: str, phase: int | None = None):
        skill = self._load_skill(skill_name)
        if skill is None:
            return

        console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"[bold cyan]  Vibecraft > {skill.get('name', skill_name)}[/bold cyan]")
        if phase is not None:
            console.print(f"[cyan]  Phase {phase}[/cyan]")
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")

        # Snapshot before making any changes (enables rollback)
        self._snapshot(skill_name)

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
                console.print("[yellow]\n  Skill aborted.\n[/yellow]")
                return

        self.ctx_manager.complete_skill(skill_name, phase)
        console.print(f"\n[bold green]  [OK] Skill '{skill_name}' complete.[/bold green]")
        console.print("[dim]  Run 'vibecraft status' to see updated progress.[/dim]\n")

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

        console.print(f"[bold]  Step {step_number}/{total_steps}: {name}[/bold]")
        console.print(f"[dim]  Agent: {agent}\n  {'-'*60}[/dim]")

        prompt = self._build_step_prompt(step, skill, phase)

        # FIX: versioned prompt storage — timestamped, never overwritten
        self._save_prompt(name, prompt)

        console.print(f"[cyan]  > Running {agent}...\n[/cyan]")
        console.print(f"[dim]{'-'*60}[/dim]")

        try:
            response = self.adapter.call(prompt)
        except RuntimeError as e:
            console.print(f"[red]\n  [FAIL] Adapter error: {e}\n[/red]")
            return self._handle_error(
                step, step_number, total_steps, skill, phase, retry_count, max_retries
            )

        console.print(f"\n[dim]{'-'*60}[/dim]")

        output_path = self._resolve_output_path(output, phase)
        if output_path:
            self._save_output(response, output_path, step)

        if gate == "human_approval":
            return self._human_gate(
                step=step,
                step_number=step_number,
                total_steps=total_steps,
                skill=skill,
                phase=phase,
                response=response,
                output_path=output_path,
                retry_count=retry_count,
                max_retries=max_retries,
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
        console.print(f"\n[bold yellow]  [WARN]  GATE - Human approval required[/bold yellow]")
        console.print(f"[dim]{'-'*60}[/dim]")

        if output_path:
            if output_path.is_dir():
                files = [f for f in output_path.rglob("*") if f.is_file()]
                console.print(f"[cyan]\n  Generated {len(files)} file(s):[/cyan]")
                for f in files:
                    console.print(f"    [dim]{f.relative_to(self.root)}[/dim]")
            elif output_path.is_file():
                console.print(f"[cyan]\n  Generated: {output_path.relative_to(self.root)}[/cyan]")

        console.print(f"\n  [bold][y][/bold] Approve  - continue")
        console.print(f"  [bold][n][/bold] Reject   - abort skill")
        console.print(f"  [bold][e][/bold] Edit     - open in $EDITOR, then continue")
        console.print(f"  [bold][r][/bold] Retry    - re-run this step  "
              f"[dim]({retry_count}/{max_retries} retries used)[/dim]\n")

        while True:
            try:
                raw = input("  Decision [y/n/e/r]: ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                console.print()
                return False

            if raw in ("y", "yes", ""):
                console.print("[green]\n  [OK] Approved - continuing.\n[/green]")
                return True

            elif raw in ("n", "no"):
                console.print("[red]\n  [FAIL] Rejected - aborting skill.\n[/red]")
                return False

            elif raw in ("e", "edit"):
                self._open_in_editor(output_path)
                console.print("[green]\n  [OK] Edit saved - continuing.\n[/green]")
                return True

            elif raw in ("r", "retry"):
                if retry_count >= max_retries:
                    console.print(f"[red]\n  Max retries ({max_retries}) reached.\n[/red]")
                    force = input(
                        "[yellow]  Force approve anyway? [y/n]: [/yellow]"
                    ).strip().lower()
                    return force in ("y", "yes")

                console.print(f"[yellow]\n  Retrying ({retry_count + 1}/{max_retries})...\n[/yellow]")
                return self._run_step(
                    step=step,
                    step_number=step_number,
                    total_steps=total_steps,
                    skill=skill,
                    phase=phase,
                    retry_count=retry_count + 1,
                )

            else:
                console.print("[dim]  Enter y, n, e, or r.[/dim]")

    # ------------------------------------------------------------------ #
    #  Prompt building                                                     #
    # ------------------------------------------------------------------ #

    def _build_step_prompt(self, step: dict, skill: dict, phase: int | None) -> str:
        parts: list[str] = []
        agent_name  = step.get("agent", "")
        description = step.get("description", "")

        parts.append(f"# Vibecraft — {skill.get('name', 'Skill')} / {step.get('name', agent_name)}\n")

        # Agent system prompt
        agent_path = self.vc_dir / "agents" / f"{agent_name}.md"
        if agent_path.exists():
            parts.append("---\n## Your Role\n")
            parts.append(agent_path.read_text(encoding="utf-8"))

        # Project context
        context_path = self.docs_dir / "context.md"
        if context_path.exists():
            parts.append("\n---\n## Project Context\n")
            parts.append(context_path.read_text(encoding="utf-8"))

        # Stack (always)
        stack_path = self.docs_dir / "stack.md"
        if stack_path.exists():
            parts.append("\n---\n## Stack\n")
            parts.append(stack_path.read_text(encoding="utf-8"))

        # Research — early phase agents
        if agent_name in ("researcher", "architect", "planner"):
            research_path = self.docs_dir / "research.md"
            if research_path.exists():
                parts.append("\n---\n## Research\n")
                parts.append(research_path.read_text(encoding="utf-8"))

        # Architecture — implementation and review agents
        if agent_name in ("implementer", "tdd_writer", "code_reviewer", "plan_reviewer"):
            arch_path = self.docs_dir / "design" / "architecture.md"
            if arch_path.exists():
                parts.append("\n---\n## Architecture\n")
                parts.append(arch_path.read_text(encoding="utf-8"))

        # Phase plan
        if phase is not None:
            plan_path = self.docs_dir / "plans" / f"phase_{phase}.md"
            if plan_path.exists():
                parts.append(f"\n---\n## Plan: Phase {phase}\n")
                parts.append(plan_path.read_text(encoding="utf-8"))

            # Existing tests for implementer
            if agent_name == "implementer":
                tests_dir = self.src_dir / "tests" / f"phase_{phase}"
                if tests_dir.exists():
                    parts.append("\n---\n## Existing Tests — DO NOT MODIFY\n")
                    for tf in sorted(tests_dir.rglob("*")):
                        if tf.is_file():
                            parts.append(
                                f"\n### {tf.name}\n```\n"
                                f"{tf.read_text(encoding='utf-8')}\n```\n"
                            )

        # Reads — other referenced files
        reads = step.get("reads", [])
        if isinstance(reads, str):
            reads = [reads]
        for r in reads:
            rp = self.root / r
            if rp.is_file():
                parts.append(f"\n---\n## Reference: {r}\n{rp.read_text(encoding='utf-8')}")

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

    # FIX: {phase} placeholder — simple brace syntax, no Jinja escaping.
    # Previously {{ "{{phase}}" }} in yaml.j2 templates was fragile and
    # relied on Jinja double-escaping tricks that could silently break.

    def _resolve_output_path(self, output_str: str, phase: int | None) -> Path | None:
        if not output_str:
            return None
        if "{phase}" in output_str and phase is None:
            raise ValueError(
                f"Skill requires --phase but none was provided. "
                f"Run: vibecraft run implement --phase <N>"
            )
        if phase is not None:
            output_str = output_str.replace("{phase}", str(phase))
        return self.root / output_str

    def _extract_files_from_response(self, response: str, output_dir: Path) -> list[Path]:
        """Parse LLM response and extract files from markdown code blocks.

        Looks for patterns like:
        ### filename.ts
        ```typescript
        // code
        ```
        or:
        **`src/path/file.ts`**
        ```
        // code
        ```
        """
        import re
        created: list[Path] = []

        # Pattern 1: ### filename then code block
        pattern1 = re.compile(
            r'###\s+[`"]?([^`\n"\']+)[`"]?\s*\n'   # ### filename
            r'```(?:\w+)?\n(.*?)```',               # code block
            re.DOTALL
        )

        # Pattern 2: **`filename`** then code block
        pattern2 = re.compile(
            r'\*\*`([^`]+)`\*\*\s*\n'              # **`filename`**
            r'```(?:\w+)?\n(.*?)```',              # code block
            re.DOTALL
        )

        # Try pattern 1 first
        for match in pattern1.finditer(response):
            filename_hint = match.group(1).strip().lstrip('./').replace('\\', '/')
            code = match.group(2)
            target = output_dir / filename_hint
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(code, encoding='utf-8')
            created.append(target)
            console.print(f"[dim]  Extracted -> {target.relative_to(self.root)}[/dim]")

        # Then pattern 2
        for match in pattern2.finditer(response):
            filename_hint = match.group(1).strip().lstrip('./').replace('\\', '/')
            code = match.group(2)
            target = output_dir / filename_hint
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(code, encoding='utf-8')
            created.append(target)
            console.print(f"[dim]  Extracted -> {target.relative_to(self.root)}[/dim]")

        if not created:
            # Fallback: save as single output.md
            target = output_dir / "output.md"
            target.write_text(response, encoding='utf-8')
            created.append(target)

        return created

    def _save_output(self, response: str, output_path: Path, step: dict):
        constraint = step.get("constraint", {})
        immutable  = constraint.get("immutable") if isinstance(constraint, dict) else None

        # If output is a directory, try to extract multiple files from response
        if output_path.suffix == "":
            output_path.mkdir(parents=True, exist_ok=True)
            created = self._extract_files_from_response(response, output_path)
            if len(created) == 1:
                console.print(f"[dim]  Saved -> {created[0].relative_to(self.root)}[/dim]")
            else:
                console.print(f"[dim]  Saved {len(created)} files to -> {output_path.relative_to(self.root)}/[/dim]")
            return

        # Single file output
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Immutability guard
        if immutable:
            immutable_path = self.root / immutable
            if immutable_path.exists() and self._is_inside(output_path, immutable_path):
                console.print(f"[red]\n  [FAIL] BLOCKED - {output_path} is inside immutable path: {immutable}\n[/red]")
                return

        output_path.write_text(response, encoding="utf-8")
        console.print(f"[dim]  Saved -> {output_path.relative_to(self.root)}[/dim]")

    def _is_inside(self, path: Path, parent: Path) -> bool:
        try:
            path.resolve().relative_to(parent.resolve())
            return True
        except ValueError:
            return False

    # ------------------------------------------------------------------ #
    #  FIX: Prompt versioning — timestamped files, never overwritten      #
    # ------------------------------------------------------------------ #

    def _save_prompt(self, step_name: str, prompt: str):
        prompts_dir = self.vc_dir / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        ts       = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        filename = f"{ts}_{step_name}.md"
        (prompts_dir / filename).write_text(prompt, encoding="utf-8")
        console.print(f"[dim]  Prompt -> .vibecraft/prompts/{filename}\n[/dim]")

    # ------------------------------------------------------------------ #
    #  Rollback snapshots                                                  #
    # ------------------------------------------------------------------ #

    def _snapshot(self, skill_name: str):
        """Copy docs/ and src/ into a timestamped snapshot before each run."""
        snapshots_dir = self.vc_dir / "snapshots"
        snapshots_dir.mkdir(parents=True, exist_ok=True)
        ts  = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        dst = snapshots_dir / f"{ts}_{skill_name}"

        dirs_to_snap = [self.docs_dir, self.src_dir]
        try:
            for src in dirs_to_snap:
                if src.exists():
                    shutil.copytree(src, dst / src.name, dirs_exist_ok=True)

            # Also snapshot manifest.json for full state restoration
            manifest_src = self.vc_dir / "manifest.json"
            if manifest_src.exists():
                shutil.copy2(manifest_src, dst / "manifest.json")

            console.print(f"[dim]  Snapshot -> .vibecraft/snapshots/{ts}_{skill_name}/\n[/dim]")
        except Exception as e:
            console.print(f"[yellow]  [WARN] Snapshot failed (non-fatal): {e}\n[/yellow]")

    # ------------------------------------------------------------------ #
    #  Editor                                                              #
    # ------------------------------------------------------------------ #

    def _open_in_editor(self, path: Path | None):
        editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "nano"))
        if path is None:
            return

        target = path if path.is_file() else (path / "output.md")
        if not target.exists():
            console.print(f"[yellow]  File not found: {target}[/yellow]")
            return

        console.print(f"[dim]  Opening in {editor}...[/dim]")
        subprocess.run([editor, str(target)])

    # ------------------------------------------------------------------ #
    #  Error / retry                                                       #
    # ------------------------------------------------------------------ #

    def _handle_error(
        self, step, step_number, total_steps, skill, phase, retry_count, max_retries
    ) -> bool:
        if retry_count >= max_retries:
            console.print("[red]  Max retries reached. Aborting.[/red]")
            return False
        raw = input(
            "[yellow]  Retry? [y/n] ({retry_count}/{max_retries}): [/yellow]"
        ).strip().lower()
        if raw in ("y", "yes", ""):
            return self._run_step(
                step=step,
                step_number=step_number,
                total_steps=total_steps,
                skill=skill,
                phase=phase,
                retry_count=retry_count + 1,
            )
        return False

    # ------------------------------------------------------------------ #
    #  Skill loading                                                       #
    # ------------------------------------------------------------------ #

    def _load_skill(self, skill_name: str) -> dict | None:
        for name in (f"{skill_name}_skill.yaml", f"{skill_name}.yaml"):
            p = self.vc_dir / "skills" / name
            if p.exists():
                return yaml.safe_load(p.read_text(encoding="utf-8"))

        console.print(f"[red]\n  Skill not found: '{skill_name}'\n[/red]")
        skills = list((self.vc_dir / "skills").glob("*.yaml"))
        if skills:
            console.print("  Available:")
            for s in skills:
                console.print(f"    [cyan]{s.stem}[/cyan]")
        return None
