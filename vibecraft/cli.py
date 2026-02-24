import click
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint
from pathlib import Path

from .bootstrapper import Bootstrapper
from .runner import SkillRunner
from .context_manager import ContextManager

console = Console()


@click.group()
def main():
    """
    ╦  ╦╦╔╗ ╔═╗╔═╗╦═╗╔═╗╔═╗╔╦╗
    ╚╗╔╝║╠╩╗║╣ ║  ╠╦╝╠═╣╠╣  ║
     ╚╝ ╩╚═╝╚═╝╚═╝╩╚═╩ ╩╚   ╩

    Craft your project from a research idea.
    """
    pass


@main.command()
@click.option("--research", "-r", required=True, type=click.Path(exists=True), help="Path to research.md")
@click.option("--stack", "-s", required=True, type=click.Path(exists=True), help="Path to stack.md")
@click.option("--output", "-o", default=".", help="Output directory (default: current dir)")
def init(research, stack, output):
    """Bootstrap a new Vibecraft project from research.md + stack.md."""

    console.print(Panel.fit(
        "[bold cyan]Vibecraft Init[/bold cyan]\n"
        f"Research: [green]{research}[/green]\n"
        f"Stack:    [green]{stack}[/green]",
        border_style="cyan"
    ))

    bootstrapper = Bootstrapper(
        research_path=Path(research),
        stack_path=Path(stack),
        output_dir=Path(output)
    )

    with console.status("[bold cyan]Analysing inputs and generating project..."):
        bootstrapper.run()

    console.print("\n[bold green]✓ Project initialized![/bold green]")
    console.print("\nNext steps:")
    console.print("  [cyan]vibecraft status[/cyan]              — see project state")
    console.print("  [cyan]vibecraft run research[/cyan]        — start research phase")
    console.print("  [cyan]vibecraft context[/cyan]             — copy context to clipboard\n")


@main.command()
@click.argument("skill_name")
@click.option("--phase", "-p", default=None, type=int, help="Phase number (for implement skill)")
def run(skill_name, phase):
    """Run a skill end-to-end: calls Qwen, streams output, gates on approval."""

    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project. Run vibecraft init first.[/red]")
        return

    runner = SkillRunner(project_root)
    runner.run(skill_name, phase=phase)


@main.command()
def status():
    """Show current project status and phase progress."""

    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project.[/red]")
        return

    cm = ContextManager(project_root)
    cm.print_status()


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


def _find_project_root() -> Path | None:
    """Walk up directory tree looking for .vibecraft/manifest.json"""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".vibecraft" / "manifest.json").exists():
            return parent
    return None
