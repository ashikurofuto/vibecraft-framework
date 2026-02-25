import click
from rich.console import Console
from rich.panel import Panel
from pathlib import Path

from .bootstrapper import Bootstrapper
from .runner import SkillRunner
from .context_manager import ContextManager
from .doctor import run_doctor
from .rollback import RollbackManager
from .exporter import Exporter

console = Console()


@click.group()
def main():
    """
    Vibecraft - Agent-driven development framework.
    Craft your project from a research idea.
    """
    pass


# ------------------------------------------------------------------ #
#  init                                                               #
# ------------------------------------------------------------------ #

@main.command()
@click.option("--research", "-r", required=True, type=click.Path(exists=True),
              help="Path to research.md")
@click.option("--stack",    "-s", required=True, type=click.Path(exists=True),
              help="Path to stack.md")
@click.option("--output",   "-o", default=".", help="Output directory (default: current dir)")
@click.option("--agents",   "-a", default=None, type=click.Path(),
              help="Optional path to agents.yaml for custom agent definitions")
@click.option("--force",    "-f", is_flag=True, default=False,
              help="Overwrite existing project without prompting")
def init(research, stack, output, agents, force):
    """Bootstrap a new Vibecraft project from research.md + stack.md."""

    console.print(f"[bold cyan]Vibecraft Init[/bold cyan]")
    console.print(f"Research: [green]{research}[/green]")
    console.print(f"Stack:    [green]{stack}[/green]")

    agents_path = Path(agents) if agents else None

    bootstrapper = Bootstrapper(
        research_path=Path(research),
        stack_path=Path(stack),
        output_dir=Path(output),
        custom_agents_path=agents_path,
        force=force,
    )

    with console.status("[bold cyan]Analysing inputs and generating project..."):
        bootstrapper.run()

    console.print("\n[bold green]✓ Project initialized![/bold green]")
    console.print("\nNext steps:")
    console.print("  [cyan]vibecraft doctor[/cyan]             — check environment")
    console.print("  [cyan]vibecraft status[/cyan]             — see project state")
    console.print("  [cyan]vibecraft run research[/cyan]       — start research phase")
    console.print("  [cyan]vibecraft run research --dry-run[/cyan]  — copy prompt, no LLM\n")


# ------------------------------------------------------------------ #
#  run                                                                #
# ------------------------------------------------------------------ #

@main.command()
@click.argument("skill_name")
@click.option("--phase", "-p", default=None, type=int,
              help="Phase number (for implement skill)")
def run(skill_name, phase):
    """Run a skill: builds prompt, copies to clipboard for manual LLM use.

    \b
    Examples:
      vibecraft run research
      vibecraft run implement --phase 1
    """

    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project. Run vibecraft init first.[/red]")
        return

    runner = SkillRunner(project_root)
    runner.run(skill_name, phase=phase)


# ------------------------------------------------------------------ #
#  status                                                             #
# ------------------------------------------------------------------ #

@main.command()
def status():
    """Show current project status and phase progress."""

    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project.[/red]")
        return

    cm = ContextManager(project_root)
    cm.print_status()


# ------------------------------------------------------------------ #
#  context                                                            #
# ------------------------------------------------------------------ #

@main.command()
@click.option("--skill", "-s", default=None, help="Skill to include in context")
@click.option("--phase", "-p", default=None, type=int, help="Phase number")
def context(skill, phase):
    """Rebuild context.md and copy it to clipboard for a new chat."""

    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project.[/red]")
        return

    cm = ContextManager(project_root)
    cm.build_and_copy(skill=skill, phase=phase)


# ------------------------------------------------------------------ #
#  complete                                                           #
# ------------------------------------------------------------------ #

@main.command()
@click.argument("phase", type=int)
def complete(phase):
    """Mark a phase as complete and update context.md."""

    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project.[/red]")
        return

    cm = ContextManager(project_root)
    cm.complete_phase(phase)
    console.print(f"[green]✓ Phase {phase} marked as complete.[/green]")
    console.print("[cyan]Run 'vibecraft context' to update your chat context.[/cyan]")


# ------------------------------------------------------------------ #
#  doctor                                                             #
# ------------------------------------------------------------------ #

@main.command()
def doctor():
    """Check environment, dependencies, and project structure."""

    project_root = _find_project_root()
    run_doctor(project_root=project_root)


# ------------------------------------------------------------------ #
#  rollback                                                           #
# ------------------------------------------------------------------ #

@main.command()
@click.argument("target", required=False, default=None)
def rollback(target):
    """Restore project to a previous snapshot.

    \b
    TARGET can be:
      (empty)     — restore latest snapshot
      0, 1, 2...  — restore snapshot by index (0 = latest)
      <name>      — restore snapshot by name or partial name

    \b
    Examples:
      vibecraft rollback               # restore latest
      vibecraft rollback 1             # restore second-latest
      vibecraft rollback design        # restore most recent 'design' snapshot
    """

    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project.[/red]")
        return

    rm = RollbackManager(project_root)

    if target is None:
        # Show list first, then restore latest
        console.print("\n[bold]Available snapshots:[/bold]")
        rm.print_snapshots()
        console.print()

    rm.rollback(target)


# ------------------------------------------------------------------ #
#  snapshots                                                          #
# ------------------------------------------------------------------ #

@main.command()
def snapshots():
    """List all available rollback snapshots."""

    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project.[/red]")
        return

    rm = RollbackManager(project_root)
    rm.print_snapshots()


# ------------------------------------------------------------------ #
#  export                                                             #
# ------------------------------------------------------------------ #

@main.command()
@click.option("--format", "-f", "fmt",
              type=click.Choice(["markdown", "zip"], case_sensitive=False),
              default="markdown",
              help="Export format: markdown (default) or zip")
def export(fmt):
    """Export project artifacts.

    \b
    Formats:
      markdown  — single docs/project_summary.md combining all documentation
      zip       — archive of docs/, src/, and manifest.json
    """

    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project.[/red]")
        return

    exporter = Exporter(project_root)

    if fmt == "markdown":
        exporter.export_markdown()
    elif fmt == "zip":
        exporter.export_zip()


# ------------------------------------------------------------------ #
#  Helper                                                             #
# ------------------------------------------------------------------ #

def _find_project_root() -> Path | None:
    """Walk up directory tree looking for .vibecraft/manifest.json"""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".vibecraft" / "manifest.json").exists():
            return parent
    return None
