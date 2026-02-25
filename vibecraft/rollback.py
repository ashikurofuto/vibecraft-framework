"""
RollbackManager — restores project state from a snapshot.

Snapshots are created by SkillRunner._snapshot() before each skill run.
Each snapshot is a directory under .vibecraft/snapshots/<timestamp>_<skill>/.
"""

import shutil
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


class RollbackManager:
    def __init__(self, project_root: Path):
        self.root          = project_root
        self.snapshots_dir = project_root / ".vibecraft" / "snapshots"

    # ------------------------------------------------------------------

    def list_snapshots(self) -> list[Path]:
        if not self.snapshots_dir.exists():
            return []
        snapshots = sorted(
            [p for p in self.snapshots_dir.iterdir() if p.is_dir()],
            reverse=True,
        )
        return snapshots

    def print_snapshots(self):
        snapshots = self.list_snapshots()
        if not snapshots:
            console.print("[yellow]No snapshots found.[/yellow]")
            return

        table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        table.add_column("#",        style="dim",  width=4)
        table.add_column("Snapshot", style="cyan")
        table.add_column("Skill")
        table.add_column("Timestamp")

        for i, snap in enumerate(snapshots):
            parts = snap.name.split("_", 1)
            ts    = parts[0] if parts else "?"
            skill = parts[1] if len(parts) > 1 else "?"
            # Format timestamp: 20240115T103000 → 2024-01-15 10:30:00
            try:
                formatted = (
                    f"{ts[:4]}-{ts[4:6]}-{ts[6:8]} "
                    f"{ts[9:11]}:{ts[11:13]}:{ts[13:15]}"
                )
            except Exception:
                formatted = ts
            table.add_row(str(i), snap.name, skill, formatted)

        console.print(table)

    def rollback(self, target: str | None = None):
        """
        Restore docs/ and src/ from a snapshot.

        target: snapshot name, index number, or None (latest).
        """
        snapshots = self.list_snapshots()

        if not snapshots:
            console.print("[red]No snapshots available to roll back to.[/red]")
            return False

        # Resolve target snapshot
        if target is None:
            snap = snapshots[0]
        elif target.isdigit():
            idx = int(target)
            if idx >= len(snapshots):
                console.print(f"[red]Snapshot index {idx} out of range (0–{len(snapshots)-1}).[/red]")
                return False
            snap = snapshots[idx]
        else:
            matches = [s for s in snapshots if s.name == target or target in s.name]
            if not matches:
                console.print(f"[red]No snapshot matching '{target}'.[/red]")
                return False
            snap = matches[0]

        console.print(f"\n[cyan]Rolling back to:[/cyan] {snap.name}")

        # Confirm
        try:
            confirm = input("  This will overwrite docs/ and src/. Continue? [y/N]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Rollback cancelled.[/yellow]")
            return False

        if confirm not in ("y", "yes"):
            console.print("[yellow]Rollback cancelled.[/yellow]")
            return False

        # Restore
        restored = 0
        for subdir in ["docs", "src"]:
            snap_subdir = snap / subdir
            target_dir  = self.root / subdir
            if snap_subdir.exists():
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(snap_subdir, target_dir)
                console.print(f"  [green]✓[/green] Restored {subdir}/")
                restored += 1

        # Restore manifest.json for complete state restoration
        snap_manifest = snap / "manifest.json"
        if snap_manifest.exists():
            shutil.copy2(snap_manifest, self.root / ".vibecraft" / "manifest.json")
            console.print("  [green]✓[/green] Restored manifest.json")
            restored += 1

        if restored == 0:
            console.print("[yellow]Nothing was restored — snapshot appears empty.[/yellow]")
            return False

        console.print(f"\n[bold green]✓ Rollback complete.[/bold green]")
        console.print("[dim]Run 'vibecraft status' to see project state.[/dim]\n")
        return True
