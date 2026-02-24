"""
ContextManager: manages context.md, manifest.json, phase tracking,
and clipboard copy for new chat sessions.
"""

import json
import re
import pyperclip
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Maps skill names (stored in phases_completed) → logical phase names
_SKILL_TO_PHASE: dict[str, str] = {
    "research_skill": "research",
    "design_skill":   "design",
    "plan_skill":     "plan",
    "review_skill":   "review",
}


class ContextManager:
    def __init__(self, project_root: Path):
        self.root          = project_root
        self.vibecraft_dir = project_root / ".vibecraft"
        self.docs_dir      = project_root / "docs"
        self.manifest_path = self.vibecraft_dir / "manifest.json"

    # ------------------------------------------------------------------
    # Manifest
    # ------------------------------------------------------------------

    def load_manifest(self) -> dict:
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def save_manifest(self, manifest: dict):
        self.manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def complete_skill(self, skill_name: str, phase: int | None = None):
        """Called by runner after a skill finishes successfully."""
        manifest = self.load_manifest()
        key = f"{skill_name}_phase_{phase}" if phase else skill_name
        if key not in manifest["phases_completed"]:
            manifest["phases_completed"].append(key)
        manifest["current_phase"] = self._next_phase(manifest)
        manifest["updated_at"] = datetime.utcnow().isoformat() + "Z"
        self.save_manifest(manifest)
        self._rebuild_context_md(manifest)

    def complete_phase(self, phase: int):
        manifest = self.load_manifest()
        phase_name = f"implement_phase_{phase}"
        if phase_name not in manifest["phases_completed"]:
            manifest["phases_completed"].append(phase_name)
        manifest["current_phase"] = self._next_phase(manifest)
        manifest["updated_at"] = datetime.utcnow().isoformat() + "Z"
        self.save_manifest(manifest)
        self._rebuild_context_md(manifest)

    # ------------------------------------------------------------------
    # FIX: _next_phase — properly maps phases_completed entries to
    # logical phase names before comparing with phases list.
    # Previously "research_skill" ≠ "research" → phase never advanced.
    # ------------------------------------------------------------------

    def _next_phase(self, manifest: dict) -> str:
        completed_logical: set[str] = set()

        for entry in manifest.get("phases_completed", []):
            if entry.startswith("implement"):
                completed_logical.add("implement")
            elif entry in _SKILL_TO_PHASE:
                completed_logical.add(_SKILL_TO_PHASE[entry])
            else:
                # Fallback: entry might already be a raw phase name
                completed_logical.add(entry)

        for phase in manifest.get("phases", []):
            if phase not in completed_logical:
                return phase

        return "done"

    # ------------------------------------------------------------------
    # Context.md
    # ------------------------------------------------------------------

    def build_and_copy(self, skill: str | None = None, phase: int | None = None):
        manifest = self.load_manifest()
        self._rebuild_context_md(manifest)

        context_content = (self.docs_dir / "context.md").read_text(encoding="utf-8")

        extra = ""
        if skill:
            skill_path = self.vibecraft_dir / "skills" / f"{skill}_skill.yaml"
            if skill_path.exists():
                extra += f"\n\n---\n## Active Skill: {skill}\n"
                extra += f"```yaml\n{skill_path.read_text(encoding='utf-8')}\n```"
            else:
                console.print(f"[yellow]Skill not found: {skill}_skill.yaml[/yellow]")

        full_content = context_content + extra

        try:
            pyperclip.copy(full_content)
            console.print("[bold green]✓ Context copied to clipboard![/bold green]")
            console.print("[dim]Paste it at the start of your new LLM chat.[/dim]")
        except Exception as e:
            console.print(f"[yellow]Clipboard unavailable ({e}). Context saved to docs/context.md[/yellow]")

    def _rebuild_context_md(self, manifest: dict):
        env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        tmpl = env.get_template("context.md.j2")
        adrs = self._extract_adrs()

        content = tmpl.render(
            **manifest,
            adrs=adrs,
            updated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        )
        (self.docs_dir / "context.md").write_text(content, encoding="utf-8")

    # ------------------------------------------------------------------
    # FIX: _extract_adrs — robust regex that finds ADR lines regardless
    # of whether they start with ##, -, *, or nothing.
    # Previously: only matched lines where ADR- was the very first word,
    # missing all "## ADR-001: ..." style headings.
    # ------------------------------------------------------------------

    def _extract_adrs(self) -> list[str]:
        arch_path = self.docs_dir / "design" / "architecture.md"
        if not arch_path.exists():
            return []

        pattern = re.compile(r"ADR-\d+[:\s].+", re.IGNORECASE)
        adrs: list[str] = []

        for line in arch_path.read_text(encoding="utf-8").splitlines():
            if pattern.search(line):
                # Strip leading markdown symbols: #, *, -, spaces
                clean = re.sub(r"^[#*\-\s]+", "", line).strip()
                if clean:
                    adrs.append(clean)

        return adrs[:10]

    # ------------------------------------------------------------------
    # Status display
    # ------------------------------------------------------------------

    def print_status(self):
        manifest = self.load_manifest()

        console.print(f"\n[bold cyan]Project:[/bold cyan] {manifest['project_name']}")
        console.print(f"[bold cyan]Type:[/bold cyan]    {', '.join(manifest['project_type'])}")
        console.print(f"[bold cyan]Phase:[/bold cyan]   {manifest['current_phase']}")

        updated = manifest.get("updated_at", manifest.get("created_at", "—"))
        console.print(f"[bold cyan]Updated:[/bold cyan] {updated}\n")

        table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        table.add_column("Phase",   style="cyan")
        table.add_column("Status")
        table.add_column("Command")

        phases    = manifest["phases"]
        completed = self._completed_logical_phases(manifest)
        current   = manifest["current_phase"]

        for phase in phases:
            if phase in completed:
                status = "[green]✓ done[/green]"
                cmd    = ""
            elif phase == current:
                status = "[yellow]→ current[/yellow]"
                cmd    = f"[dim]vibecraft run {phase.replace('_', ' ')}[/dim]"
            else:
                status = "[dim]pending[/dim]"
                cmd    = ""
            table.add_row(phase, status, cmd)

        console.print(table)
        console.print(f"\n[bold]Agents:[/bold] {', '.join(manifest['agents'])}")
        console.print(f"\n[dim]Stack: {manifest.get('stack', {})}[/dim]\n")

    def _completed_logical_phases(self, manifest: dict) -> set[str]:
        """Same mapping as _next_phase, exposed for status display."""
        result: set[str] = set()
        for entry in manifest.get("phases_completed", []):
            if entry.startswith("implement"):
                result.add("implement")
            elif entry in _SKILL_TO_PHASE:
                result.add(_SKILL_TO_PHASE[entry])
            else:
                result.add(entry)
        return result
