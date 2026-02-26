import os
import click
from rich.console import Console
from pathlib import Path

from .runner import SkillRunner
from .context_manager import ContextManager
from .doctor import run_doctor
from .rollback import RollbackManager
from .exporter import Exporter
from .core.factory import BootstrapperFactory
from .core.config import VibecraftConfig, ProjectMode
from .modes.modular.module_manager import ModuleManager
from .modes.modular.module_registry import ModuleRegistry
from .modes.modular.dependency_analyzer import DependencyAnalyzer

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
@click.option("--mode",     "-m", default="simple", type=click.Choice(["simple", "modular"]),
              help="Project mode: simple (default) or modular")
def init(research, stack, output, agents, force, mode):
    """Bootstrap a new Vibecraft project from research.md + stack.md."""

    console.print("[bold cyan]Vibecraft Init[/bold cyan]")
    console.print(f"Research: [green]{research}[/green]")
    console.print(f"Stack:    [green]{stack}[/green]")
    console.print(f"Mode:     [green]{mode}[/green]")

    agents_path = Path(agents) if agents else None
    output_path = Path(output)

    # Create config
    config = VibecraftConfig(
        project_name="New Project",
        mode=ProjectMode(mode),
    )

    # Use factory to create bootstrapper
    bootstrapper = BootstrapperFactory.create(
        mode=mode,
        project_root=output_path,
        config=config,
        research_path=Path(research),
        stack_path=Path(stack),
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
@click.option("--module", "-m", default=None, type=str,
              help="Module name for module-specific skill execution (modular mode)")
def run(skill_name, phase, module):
    """Run a skill: builds prompt, copies to clipboard for manual LLM use.

    \b
    Examples:
      vibecraft run research
      vibecraft run implement --phase 1
      vibecraft run implement --phase 1 --module auth
    """

    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project. Run vibecraft init first.[/red]")
        return

    # Use ModularRunner if module is specified or project is in modular mode
    manifest_path = project_root / ".vibecraft" / "manifest.json"
    if manifest_path.exists():
        import json
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        is_modular = manifest.get("mode") == "modular"
    else:
        is_modular = False

    if module or is_modular:
        from vibecraft.modes.modular.runner import ModularRunner
        runner = ModularRunner(project_root)
        runner.run(skill_name, module=module, phase=phase)
    else:
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
#  module                                                             #
# ------------------------------------------------------------------ #

@main.group()
def module():
    """Module management commands for modular mode."""
    pass


@module.command("create")
@click.argument("name")
@click.option("--description", "-d", default="", help="Module description")
@click.option("--depends-on", "-dep", default=None, help="Module dependencies (comma-separated: auth,tasks)")
def module_create(name, description, depends_on):
    """Create a new module.

    \b
    Examples:
      vibecraft module create auth -d "Authentication module"
      vibecraft module create api --depends-on auth,tasks
    """

    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project. Run vibecraft init first.[/red]")
        return

    manager = ModuleManager(project_root)

    # Parse comma-separated dependencies
    dependencies = []
    if depends_on:
        dependencies = [dep.strip() for dep in depends_on.split(",") if dep.strip()]

    try:
        manager.create_module(name, description or f"{name} module", dependencies)
        console.print(f"[green]✓ Module '{name}' created successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@module.command("list")
def module_list():
    """List all modules in the project."""
    
    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project.[/red]")
        return
    
    manager = ModuleManager(project_root)
    modules = manager.list_modules()
    
    if not modules:
        console.print("[yellow]No modules found. Create one with 'vibecraft module create <name>'[/yellow]")
        return
    
    # Print table header
    console.print("\n[bold]Modules:[/bold]")
    console.print("-" * 60)
    
    for module in modules:
        name = module.get("name", "unknown")
        description = module.get("description", "")
        status = module.get("status", "planned")
        deps = module.get("dependencies", [])
        deps_str = ", ".join(deps) if deps else "-"
        
        console.print(f"[cyan]{name}[/cyan]")
        console.print(f"  Description: {description}")
        console.print(f"  Status: {status}")
        console.print(f"  Dependencies: {deps_str}")
        console.print()


@module.command("init")
@click.argument("name")
def module_init(name):
    """Initialize module structure (research.md, stack.md, agents/, skills/).
    
    \b
    Example:
      vibecraft module init auth
    """
    
    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project.[/red]")
        return
    
    manager = ModuleManager(project_root)
    
    try:
        manager.init_module(name)
        console.print(f"[green]✓ Module '{name}' initialized![/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@module.command("status")
@click.argument("name")
def module_status(name):
    """Show detailed status of a module.
    
    \b
    Example:
      vibecraft module status auth
    """
    
    project_root = _find_project_root()
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project.[/red]")
        return
    
    manager = ModuleManager(project_root)
    
    try:
        status = manager.get_status(name)
        
        console.print(f"\n[bold]Module: {status.get('name', 'unknown')}[/bold]")
        console.print(f"Description: {status.get('description', 'N/A')}")
        console.print(f"Status: {status.get('status', 'unknown')}")
        
        deps = status.get("dependencies", [])
        if deps:
            console.print(f"Dependencies: {', '.join(deps)}")
        else:
            console.print("Dependencies: None")
        
        exports = status.get("exports", [])
        if exports:
            console.print(f"Exports: {', '.join(exports)}")
        else:
            console.print("Exports: None")
        
        phases = status.get("phases_completed", [])
        if phases:
            console.print(f"Phases completed: {', '.join(map(str, phases))}")
        else:
            console.print("Phases completed: None")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


# ------------------------------------------------------------------ #
#  integrate                                                          #
# ------------------------------------------------------------------ #

@main.group()
def integrate():
    """Module integration commands."""
    pass


@integrate.command("analyze")
@click.pass_context
def integrate_analyze(ctx):
    """Analyze module dependencies and show build order.

    This command:
    1. Validates all module dependencies exist
    2. Checks for circular dependencies
    3. Shows build order if no errors found
    """
    # Use project_root from context if provided (for testing)
    project_root = ctx.obj.get("project_root") if ctx.obj else None
    
    # Otherwise find project root automatically
    if not project_root:
        project_root = _find_project_root()
    
    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project.[/red]")
        return

    try:
        # Load registry
        registry_path = project_root / ".vibecraft" / "modules-registry.json"
        registry = ModuleRegistry(registry_path)

        # Get all modules
        modules = registry.get_all()

        if not modules:
            console.print("[yellow]No modules found. Create one with 'vibecraft module create <name>'[/yellow]")
            return

        console.print(f"\n[bold]Analyzing {len(modules)} module(s)...[/bold]\n")

        # Analyze dependencies
        from vibecraft.core.exceptions import MissingDependencyError, CyclicDependencyError
        
        analyzer = DependencyAnalyzer(registry)
        
        try:
            analyzer.validate_dependencies()
        except MissingDependencyError as e:
            console.print(f"[red]Dependency error: {e}[/red]")
            console.print("\n[red]Fix these errors before proceeding.[/red]")
            return
        except CyclicDependencyError as e:
            console.print(f"[red]Cycle detected: {e}[/red]")
            console.print("\n[red]Fix circular dependencies before proceeding.[/red]")
            return

        # No errors - show build order
        build_order = analyzer.get_build_order()

        console.print("[green]✓ All dependencies valid![/green]\n")
        console.print("[bold]Build order:[/bold]")
        for i, module_name in enumerate(build_order, 1):
            module = registry.get_module_by_name(module_name)
            deps = module.dependencies if module else []
            deps_str = f" (depends on: {', '.join(deps)})" if deps else ""
            console.print(f"  {i}. [cyan]{module_name}[/cyan]{deps_str}")

        console.print("\n[green]Ready for integration build.[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@integrate.command("build")
@click.pass_context
def integrate_build(ctx):
    """Build integration layer for all modules.

    This command:
    1. Validates all module dependencies
    2. Checks for circular dependencies
    3. Generates interfaces.py from module exports
    4. Generates connectors for dependencies
    """
    from vibecraft.modes.modular.integration_manager import IntegrationManager
    from vibecraft.core.exceptions import MissingDependencyError, CyclicDependencyError

    # Use project_root from context if provided (for testing)
    project_root = ctx.obj.get("project_root") if ctx.obj else None

    # Otherwise find project root automatically
    if not project_root:
        project_root = _find_project_root()

    if not project_root:
        console.print("[red]Error: Not inside a Vibecraft project.[/red]")
        raise click.Abort()

    try:
        manager = IntegrationManager(project_root)

        # First analyze dependencies
        errors = manager.analyze_dependencies()
        if errors:
            for error in errors:
                console.print(f"[red]Error: {error}[/red]")
            console.print("\n[red]Fix these errors before proceeding.[/red]")
            raise click.Abort()

        # Build integration layer
        manager.build_project()

        console.print("[green]✓ Integration build complete![/green]")
        console.print(f"\nGenerated files in: [cyan]{manager.integration_dir}[/cyan]")
        console.print("  - interfaces.py (module interfaces)")
        console.print("  - connectors/ (module connectors)")

    except MissingDependencyError as e:
        console.print(f"[red]Dependency error: {e}[/red]")
        console.print("\n[red]Fix missing dependencies before proceeding.[/red]")
        raise click.Abort()
    except CyclicDependencyError as e:
        console.print(f"[red]Cycle detected: {e}[/red]")
        console.print("\n[red]Fix circular dependencies before proceeding.[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


# ------------------------------------------------------------------ #
#  Helper                                                             #
# ------------------------------------------------------------------ #

def _find_project_root() -> Path | None:
    """Walk up directory tree looking for .vibecraft/manifest.json"""
    # First check environment variable (for testing)
    env_root = os.environ.get("VIBECRAFT_PROJECT_ROOT")
    if env_root:
        path = Path(env_root)
        if (path / ".vibecraft" / "manifest.json").exists():
            return path
    
    # Then walk up directory tree from cwd
    current = Path.cwd()
    for parent in [current, *current.parents]:
        manifest_path = parent / ".vibecraft" / "manifest.json"
        if manifest_path.exists():
            # Skip if this is the vibecraft framework itself (not a user project)
            if "vibecraft-framework" in str(parent) or parent.name == "vibecraft_v0.3":
                continue
            return parent
    return None
