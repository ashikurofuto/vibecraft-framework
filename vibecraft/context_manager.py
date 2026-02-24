"""
ContextManager: manages context.md, manifest.json, phase tracking,
and clipboard copy for new chat sessions.
"""

import json
import pyperclip
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()
TEMPLATES_DIR = Path(__file__).parent / "templates"


class ContextManager:
    def __init__(self, project_root: Path):
        self.root = project_root
        self.vibecraft_dir = project_root / ".vibecraft"
        self.docs_dir = project_root / "docs"
        self.manifest_path = self.vibecraft_dir / "manifest.json"

    # ------------------------------------------------------------------
    # Manifest
    # ------------------------------------------------------------------

    def load_manifest(self) -> dict:
        return json.loads(self.manifest_path.read_text())

    def save_manifest(self, manifest: dict):
        self.manifest_path.write_text(json.dumps(manifest, indent=2))

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

        # Advance current_phase if all implement phases done
        manifest["current_phase"] = self._next_phase(manifest)
        manifest["updated_at"] = datetime.utcnow().isoformat() + "Z"
        self.save_manifest(manifest)
        self._rebuild_context_md(manifest)

    def _next_phase(self, manifest: dict) -> str:
        completed = set(manifest["phases_completed"])
        for phase in manifest["phases"]:
            if phase not in completed:
                return phase
        return "done"

    # ------------------------------------------------------------------
    # Context.md
    # ------------------------------------------------------------------

    def build_and_copy(self, skill: str | None = None, phase: int | None = None):
        manifest = self.load_manifest()
        self._rebuild_context_md(manifest)

        context_content = (self.docs_dir / "context.md").read_text()

        # Optionally attach skill prompt
        extra = ""
        if skill:
            skill_path = self.vibecraft_dir / "skills" / f"{skill}_skill.yaml"
            if skill_path.exists():
                extra += f"\n\n---\n## Active Skill: {skill}\n"
                extra += f"```yaml\n{skill_path.read_text()}\n```"

        full_content = context_content + extra

        try:
            pyperclip.copy(full_content)
            console.print("[bold green]✓ Context copied to clipboard![/bold green]")
            console.print("[dim]Paste it at the start of your new Qwen chat.[/dim]")
        except Exception:
            console.print("[yellow]Clipboard unavailable. Context saved to docs/context.md[/yellow]")

    def _rebuild_context_md(self, manifest: dict):
        env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        tmpl = env.get_template("context.md.j2")

        # Gather ADRs if design exists
        adrs = self._extract_adrs()

        content = tmpl.render(
            **manifest,
            adrs=adrs,
            updated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        )
        (self.docs_dir / "context.md").write_text(content)

    def _extract_adrs(self) -> list[str]:
        arch_path = self.docs_dir / "design" / "architecture.md"
        if not arch_path.exists():
            return []
        adrs = []
        for line in arch_path.read_text().splitlines():
            if line.strip().upper().startswith("ADR-"):
                adrs.append(line.strip())
        return adrs[:10]  # max 10 ADRs in context

    # ------------------------------------------------------------------
    # Status display
    # ------------------------------------------------------------------

    def print_status(self):
        manifest = self.load_manifest()

        console.print(f"\n[bold cyan]Project:[/bold cyan] {manifest['project_name']}")
        console.print(f"[bold cyan]Type:[/bold cyan]    {', '.join(manifest['project_type'])}")
        console.print(f"[bold cyan]Phase:[/bold cyan]   {manifest['current_phase']}\n")

        table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        table.add_column("Phase", style="cyan")
        table.add_column("Status")
        table.add_column("Command")

        phases = manifest["phases"]
        completed = set(manifest["phases_completed"])
        current = manifest["current_phase"]

        for phase in phases:
            if phase in completed:
                status = "[green]✓ done[/green]"
                cmd = ""
            elif phase == current:
                status = "[yellow]→ current[/yellow]"
                cmd = f"[dim]vibecraft run {phase.replace('_', ' ')}[/dim]"
            else:
                status = "[dim]pending[/dim]"
                cmd = ""
            table.add_row(phase, status, cmd)

        console.print(table)

        console.print(f"\n[bold]Agents:[/bold] {', '.join(manifest['agents'])}")
        console.print(f"\n[dim]Stack: {manifest.get('stack', {})}[/dim]\n")
