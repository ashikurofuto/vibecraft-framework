"""
Plan Generator for Vibecraft Framework modular mode.

This module provides the PlanGenerator class for extracting module
information from research documents and generating development plans.
"""

import re
from pathlib import Path
from typing import Any


class PlanGenerator:
    """Generate development plans for modular projects.

    PlanGenerator extracts module information from research.md and
    generates a structured development plan with phases and build order.

    Attributes:
        project_root: Root directory of the project.

    Example:
        >>> from vibecraft.modes.modular.plan_generator import PlanGenerator
        >>> from pathlib import Path
        >>>
        >>> generator = PlanGenerator(Path("/project"))
        >>> modules = generator.extract_modules()
        >>> plan = generator.generate_plan()
    """

    def __init__(self, project_root: Path) -> None:
        """Initialize the plan generator.

        Args:
            project_root: Root directory of the project.
        """
        self.project_root = project_root

    def extract_modules(self) -> list[dict[str, Any]]:
        """Extract module information from research.md.

        This method parses the research.md file to identify modules
        and their descriptions.

        Returns:
            List of module dictionaries with name, description, and
            other extracted information.

        Example:
            >>> generator = PlanGenerator(Path("/project"))
            >>> modules = generator.extract_modules()
            >>> modules  # doctest: +SKIP
            [
                {"name": "auth", "description": "Authentication module"},
                {"name": "users", "description": "User management"}
            ]
        """
        research_path = self.project_root / "docs" / "research.md"

        if not research_path.exists():
            return []

        content = research_path.read_text(encoding="utf-8")
        modules: list[dict[str, Any]] = []

        # Look for module definitions in research.md
        # Expected format: "- module_name: Description"
        module_pattern = r"^\s*[-*]\s*(\w+)\s*:\s*(.+)$"

        for line in content.split("\n"):
            match = re.match(module_pattern, line)
            if match:
                module_name = match.group(1)
                description = match.group(2).strip()
                modules.append({
                    "name": module_name,
                    "description": description,
                    "status": "planned",
                    "dependencies": [],
                })

        return modules

    def generate_plan(self) -> str:
        """Generate a development plan markdown document.

        This method creates a development-plan.md file with the
        extracted modules and suggested phases.

        Returns:
            The generated plan as a markdown string.

        Example:
            >>> generator = PlanGenerator(Path("/project"))
            >>> plan = generator.generate_plan()
            >>> print(plan)  # doctest: +SKIP
            # Development Plan
            ...
        """
        # Extract modules
        modules = self.extract_modules()

        # Build the plan content
        plan_lines = [
            "# Development Plan",
            "",
            "## Overview",
            "",
            "This plan outlines the development phases for the project.",
            "",
            "## Modules",
            "",
        ]

        if modules:
            for module in modules:
                plan_lines.append(f"- **{module['name']}**: {module['description']}")
        else:
            plan_lines.append("No modules defined yet.")

        plan_lines.extend([
            "",
            "## Phases",
            "",
            "### Phase 1: Foundation",
            "",
            "1. Set up project structure",
            "2. Create base modules",
            "",
            "### Phase 2: Core Features",
            "",
            "1. Implement core functionality",
            "2. Add integrations",
            "",
            "### Phase 3: Polish",
            "",
            "1. Testing and refinement",
            "2. Documentation",
            "",
        ])

        plan_content = "\n".join(plan_lines)

        # Write the plan file
        self._write_plan(plan_content)

        return plan_content

    def _write_plan(self, content: str) -> None:
        """Write the plan to the docs/plans directory.

        Args:
            content: The plan content as markdown string.
        """
        plans_dir = self.project_root / "docs" / "plans"
        plans_dir.mkdir(parents=True, exist_ok=True)

        plan_file = plans_dir / "development-plan.md"
        plan_file.write_text(content, encoding="utf-8")
