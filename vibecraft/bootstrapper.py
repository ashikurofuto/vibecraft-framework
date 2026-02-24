"""
Bootstrapper: reads research.md + stack.md, generates the full project structure.
Uses Jinja2 templates for agents, skills, context.md and manifest.json.
"""

import json
import shutil
import yaml
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from rich.console import Console

console = Console()

TEMPLATES_DIR = Path(__file__).parent / "templates"

CORE_AGENTS = [
    "researcher",
    "architect",
    "planner",
    "plan_reviewer",
    "tdd_writer",
    "implementer",
    "code_reviewer",
]

CONDITIONAL_AGENTS: dict[str, list[str]] = {
    "game":        ["performance_optimizer", "game_designer"],
    "multiplayer": ["security_auditor"],
    "web":         ["security_auditor", "ux_reviewer"],
    "api":         ["security_auditor", "api_designer"],
    "cli":         [],
    "mobile":      ["ux_reviewer"],
    "database":    ["migration_agent"],
}

SKILLS = [
    "research_skill",
    "design_skill",
    "plan_skill",
    "implement_skill",
    "review_skill",
]

# Minimum meaningful content lengths
_MIN_RESEARCH_LEN = 50
_MIN_STACK_LEN    = 20


class Bootstrapper:
    def __init__(
        self,
        research_path: Path,
        stack_path: Path,
        output_dir: Path,
        custom_agents_path: Path | None = None,
    ):
        self.research_path       = research_path
        self.stack_path          = stack_path
        self.output_dir          = output_dir.resolve()
        self.custom_agents_path  = custom_agents_path

        self.research_content = research_path.read_text(encoding="utf-8")
        self.stack_content    = stack_path.read_text(encoding="utf-8")

        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def run(self):
        # Validate before doing anything
        self._validate_inputs()

        ctx = self._build_context()
        self._create_dirs(ctx)
        self._copy_inputs(ctx)
        self._generate_agents(ctx)
        self._generate_skills(ctx)
        self._generate_context_md(ctx)
        self._generate_manifest(ctx)
        self._print_summary(ctx)

    # ------------------------------------------------------------------
    # FIX: input validation — prevents silent creation of broken projects
    # ------------------------------------------------------------------

    def _validate_inputs(self):
        errors: list[str] = []

        research_stripped = self.research_content.strip()
        stack_stripped    = self.stack_content.strip()

        if len(research_stripped) < _MIN_RESEARCH_LEN:
            errors.append(
                f"research.md is too short ({len(research_stripped)} chars). "
                f"Minimum {_MIN_RESEARCH_LEN} chars required."
            )

        if len(stack_stripped) < _MIN_STACK_LEN:
            errors.append(
                f"stack.md is too short ({len(stack_stripped)} chars). "
                f"Minimum {_MIN_STACK_LEN} chars required."
            )

        if not self._extract_project_name():
            errors.append(
                "Cannot find a project name in research.md. "
                "Add a top-level heading (# My Project) or a 'Project: ...' line."
            )

        if errors:
            console.print("\n[bold red]✗ Validation failed:[/bold red]")
            for e in errors:
                console.print(f"  [red]• {e}[/red]")
            raise SystemExit(1)

    # ------------------------------------------------------------------
    # Context extraction
    # ------------------------------------------------------------------

    def _build_context(self) -> dict:
        project_name = self._extract_project_name()
        project_type = self._detect_project_type()
        stack_info   = self._parse_stack()
        agents       = self._resolve_agents(project_type)

        return {
            "project_name":    project_name,
            "project_type":    project_type,
            "research_content": self.research_content,
            "stack_content":   self.stack_content,
            "stack":           stack_info,
            "agents":          agents,
            "skills":          SKILLS,
            "created_at":      datetime.utcnow().isoformat() + "Z",
            "current_phase":   "research",
            "phases": [
                "research",
                "design",
                "plan",
                "implement",
                "review",
            ],
            "phases_completed": [],
        }

    def _extract_project_name(self) -> str:
        for line in self.research_content.splitlines():
            line = line.strip()
            if line.startswith("#"):
                return line.lstrip("#").strip()
            if line.lower().startswith("project:"):
                return line.split(":", 1)[1].strip()
        return self.research_path.stem.replace("_", " ").title()

    def _detect_project_type(self) -> list[str]:
        combined = (self.research_content + self.stack_content).lower()
        found = [kw for kw in CONDITIONAL_AGENTS if kw in combined]
        return found or ["generic"]

    def _parse_stack(self) -> dict:
        result: dict[str, str] = {}
        for line in self.stack_content.splitlines():
            line = line.strip().lstrip("*-").strip()
            if ":" in line:
                key, _, value = line.partition(":")
                key   = key.strip().lower().replace(" ", "_")
                value = value.strip()
                if key and value:
                    result[key] = value
        return result

    # ------------------------------------------------------------------
    # FIX: custom agents — load from optional agents.yaml file
    # Allows users to define project-specific agents without editing code.
    # ------------------------------------------------------------------

    def _resolve_agents(self, project_types: list[str]) -> list[str]:
        agents = list(CORE_AGENTS)

        # Built-in conditional agents
        for ptype in project_types:
            for extra in CONDITIONAL_AGENTS.get(ptype, []):
                if extra not in agents:
                    agents.append(extra)

        # User-defined custom agents
        if self.custom_agents_path and self.custom_agents_path.exists():
            agents = self._load_custom_agents(agents)

        return agents

    def _load_custom_agents(self, agents: list[str]) -> list[str]:
        try:
            data = yaml.safe_load(
                self.custom_agents_path.read_text(encoding="utf-8")
            )
        except Exception as e:
            console.print(f"[yellow]  ⚠ Could not load custom agents: {e}[/yellow]")
            return agents

        if not isinstance(data, list):
            console.print("[yellow]  ⚠ agents.yaml must be a list of agent definitions[/yellow]")
            return agents

        combined = (self.research_content + self.stack_content).lower()

        for entry in data:
            if not isinstance(entry, dict):
                continue
            name     = entry.get("name", "").strip()
            triggers = entry.get("triggers", [])
            if not name:
                continue
            # Add if no triggers (always include) or any trigger matches
            if not triggers or any(t.lower() in combined for t in triggers):
                if name not in agents:
                    agents.append(name)
                    console.print(f"  [dim]→ custom agent: {name}[/dim]")

        return agents

    # ------------------------------------------------------------------
    # File generation
    # ------------------------------------------------------------------

    def _create_dirs(self, ctx: dict):
        root = self.output_dir
        dirs = [
            root / ".vibecraft" / "agents",
            root / ".vibecraft" / "skills",
            root / ".vibecraft" / "prompts",   # versioned prompt history
            root / ".vibecraft" / "snapshots",  # rollback snapshots
            root / "docs" / "design",
            root / "docs" / "plans",
            root / "src" / "tests",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def _copy_inputs(self, ctx: dict):
        docs = self.output_dir / "docs"
        shutil.copy(self.research_path, docs / "research.md")
        shutil.copy(self.stack_path,    docs / "stack.md")
        console.print("  [dim]→ docs/research.md[/dim]")
        console.print("  [dim]→ docs/stack.md[/dim]")

        # Copy custom agents config if provided
        if self.custom_agents_path and self.custom_agents_path.exists():
            shutil.copy(
                self.custom_agents_path,
                self.output_dir / ".vibecraft" / "custom_agents.yaml",
            )
            console.print("  [dim]→ .vibecraft/custom_agents.yaml[/dim]")

    def _generate_agents(self, ctx: dict):
        agents_dir = self.output_dir / ".vibecraft" / "agents"
        for agent_name in ctx["agents"]:
            template_file = f"agents/{agent_name}.md.j2"
            fallback_file = "agents/base_agent.md.j2"
            try:
                tmpl = self.env.get_template(template_file)
            except Exception:
                tmpl = self.env.get_template(fallback_file)

            content  = tmpl.render(**ctx, agent_name=agent_name)
            out_path = agents_dir / f"{agent_name}.md"
            out_path.write_text(content, encoding="utf-8")
            console.print(f"  [dim]→ .vibecraft/agents/{agent_name}.md[/dim]")

    def _generate_skills(self, ctx: dict):
        skills_dir = self.output_dir / ".vibecraft" / "skills"
        for skill_name in ctx["skills"]:
            tmpl    = self.env.get_template(f"skills/{skill_name}.yaml.j2")
            content = tmpl.render(**ctx)
            out_path = skills_dir / f"{skill_name}.yaml"
            out_path.write_text(content, encoding="utf-8")
            console.print(f"  [dim]→ .vibecraft/skills/{skill_name}.yaml[/dim]")

    def _generate_context_md(self, ctx: dict):
        tmpl     = self.env.get_template("context.md.j2")
        content  = tmpl.render(**ctx)
        out_path = self.output_dir / "docs" / "context.md"
        out_path.write_text(content, encoding="utf-8")
        console.print("  [dim]→ docs/context.md[/dim]")

    def _generate_manifest(self, ctx: dict):
        manifest = {
            "project_name":     ctx["project_name"],
            "project_type":     ctx["project_type"],
            "created_at":       ctx["created_at"],
            "stack":            ctx["stack"],
            "agents":           ctx["agents"],
            "skills":           ctx["skills"],
            "current_phase":    ctx["current_phase"],
            "phases":           ctx["phases"],
            "phases_completed": [],
        }
        out_path = self.output_dir / ".vibecraft" / "manifest.json"
        out_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        console.print("  [dim]→ .vibecraft/manifest.json[/dim]")

    def _print_summary(self, ctx: dict):
        console.print(f"\n  Project: [bold]{ctx['project_name']}[/bold]")
        console.print(f"  Type:    {', '.join(ctx['project_type'])}")
        console.print(f"  Agents:  {len(ctx['agents'])} generated")
        console.print(f"  Skills:  {len(ctx['skills'])} generated")
