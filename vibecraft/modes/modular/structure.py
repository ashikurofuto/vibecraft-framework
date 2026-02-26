"""
Modular structure generator for Vibecraft Framework.

This module provides functions for creating the directory structure
required for modular mode projects.
"""

from pathlib import Path


def create_modular_structure(project_root: Path) -> None:
    """Create the directory structure for a modular mode project.

    This function creates all necessary directories for a modular
    Vibecraft project, including:
    - modules/ — for module packages
    - shared/ — for shared code across modules
    - integration/ — for integration layer
    - .vibecraft/ — for framework metadata
    - docs/ — for project documentation
    - src/tests/ — for project tests

    Args:
        project_root: Root directory where the structure should be created.

    Example:
        >>> from pathlib import Path
        >>> from vibecraft.modes.modular.structure import create_modular_structure
        >>> create_modular_structure(Path("/my-project"))
    """
    # Core modular directories
    modules_dir = project_root / "modules"
    shared_dir = project_root / "shared"
    integration_dir = project_root / "integration"

    # .vibecraft structure
    vibecraft_dir = project_root / ".vibecraft"
    vibecraft_agents_dir = vibecraft_dir / "agents"
    vibecraft_skills_dir = vibecraft_dir / "skills"
    vibecraft_prompts_dir = vibecraft_dir / "prompts"
    vibecraft_snapshots_dir = vibecraft_dir / "snapshots"

    # Documentation structure
    docs_dir = project_root / "docs"
    docs_design_dir = docs_dir / "design"
    docs_plans_dir = docs_dir / "plans"

    # Tests structure
    src_tests_dir = project_root / "src" / "tests"

    # Create all directories
    modules_dir.mkdir(parents=True, exist_ok=True)
    shared_dir.mkdir(parents=True, exist_ok=True)
    integration_dir.mkdir(parents=True, exist_ok=True)

    vibecraft_dir.mkdir(parents=True, exist_ok=True)
    vibecraft_agents_dir.mkdir(exist_ok=True)
    vibecraft_skills_dir.mkdir(exist_ok=True)
    vibecraft_prompts_dir.mkdir(exist_ok=True)
    vibecraft_snapshots_dir.mkdir(exist_ok=True)

    docs_dir.mkdir(parents=True, exist_ok=True)
    docs_design_dir.mkdir(exist_ok=True)
    docs_plans_dir.mkdir(exist_ok=True)

    src_tests_dir.mkdir(parents=True, exist_ok=True)
