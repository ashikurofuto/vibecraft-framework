"""
ModularRunner for Vibecraft Framework.

This module provides the ModularRunner class for executing skills
in modular mode projects with module-aware functionality.
"""

import json
from pathlib import Path
from typing import Any

from vibecraft.core.base_runner import BaseRunner
from vibecraft.modes.simple.runner import SimpleRunner


class ModularRunner(BaseRunner):
    """Runner for modular mode projects.

    ModularRunner extends BaseRunner to provide module-aware skill
    execution. It can run skills in the context of specific modules
    or globally across the entire project.

    Example:
        >>> from vibecraft.modes.modular.runner import ModularRunner
        >>> from pathlib import Path
        >>>
        >>> runner = ModularRunner(Path("/project"))
        >>> runner.run("research")  # Global skill
        >>> runner.run("implement", module="auth")  # Module-specific skill
    """

    def __init__(self, project_root: Path, module: str | None = None) -> None:
        """Initialize the modular runner.

        Args:
            project_root: Root directory of the project.
            module: Optional module name for module-specific execution.

        Example:
            >>> runner = ModularRunner(Path("/project"), module="auth")
        """
        super().__init__(project_root)
        self._module: str | None = module
        self._module_context: str | None = None
        self._kwargs: dict[str, Any] = {}

    def run(self, skill_name: str, module: str | None = None, **kwargs: Any) -> None:
        """Execute a skill in modular mode.

        This method runs the specified skill, optionally within the context
        of a specific module.

        Args:
            skill_name: Name of the skill to execute (e.g., "research", "design").
            module: Optional module name for module-specific execution.
            **kwargs: Additional arguments for the skill.

        Raises:
            VibecraftError: If skill execution fails.

        Example:
            >>> runner = ModularRunner(Path("/project"))
            >>> runner.run("research")
            >>> runner.run("implement", module="auth", phase=1)
        """
        # Store module context for potential use
        self._module = module
        self._kwargs = kwargs

        if module:
            # Module-specific skill execution
            self._run_module_skill(skill_name, module, **kwargs)
        else:
            # Global skill execution
            self._run_global_skill(skill_name, **kwargs)

    def _run_global_skill(self, skill_name: str, **kwargs: Any) -> None:
        """Execute a global skill across the entire project.

        For modular mode, global skills use the project root context.

        Args:
            skill_name: Name of the skill to execute.
            **kwargs: Additional arguments for the skill.
        """
        # Use SimpleRunner for global skills at project level
        runner = SimpleRunner(self.project_root)
        runner.run(skill_name, **kwargs)

    def _run_module_skill(self, skill_name: str, module: str, **kwargs: Any) -> None:
        """Execute a skill within a specific module context.

        This delegates to SimpleRunner with the module directory as root.

        Args:
            skill_name: Name of the skill to execute.
            module: Name of the module to execute the skill in.
            **kwargs: Additional arguments for the skill.

        Raises:
            ModuleError: If module doesn't exist.
        """
        from vibecraft.core.exceptions import ModuleError

        # Verify module exists
        module_dir = self.project_root / "modules" / module
        if not module_dir.exists():
            raise ModuleError(f"Module '{module}' not found")

        # Load module configuration to check if it's initialized
        config = self._load_module_config(module)
        if not config:
            raise ModuleError(
                f"Module '{module}' is not initialized. "
                f"Run 'vibecraft init' in the module directory first."
            )

        # Use SimpleRunner with module directory as root
        runner = SimpleRunner(module_dir)
        runner.run(skill_name, **kwargs)

        # Update module registry with phase completion
        if skill_name == "implement" and "phase" in kwargs:
            self._update_module_phase(module, kwargs["phase"])

    def _update_module_phase(self, module: str, phase: int) -> None:
        """Update module's phases_completed in registry.

        Args:
            module: Module name.
            phase: Phase number completed.
        """
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry_path = self.project_root / ".vibecraft" / "modules-registry.json"
        if registry_path.exists():
            registry = ModuleRegistry(registry_path)
            module_data = registry.get_by_name(module)
            if module_data:
                phase_key = f"implement_phase_{phase}"
                if "phases_completed" not in module_data:
                    module_data["phases_completed"] = []
                if phase_key not in module_data["phases_completed"]:
                    module_data["phases_completed"].append(phase_key)
                registry.update_module(module, phases_completed=module_data["phases_completed"])

    def _load_module_context(self, module_name: str) -> str | None:
        """Load context from a module's context.md file.

        Args:
            module_name: Name of the module to load context from.

        Returns:
            Module context content as string, or None if not found.

        Example:
            >>> runner = ModularRunner(Path("/project"))
            >>> context = runner._load_module_context("auth")
        """
        context_path = self.project_root / "modules" / module_name / "context.md"
        if context_path.exists():
            return context_path.read_text(encoding="utf-8")
        return None

    def _load_module_config(self, module_name: str) -> dict[str, Any] | None:
        """Load configuration from a module's .module.json file.

        Args:
            module_name: Name of the module to load config from.

        Returns:
            Module configuration as dict, or None if not found.

        Example:
            >>> runner = ModularRunner(Path("/project"))
            >>> config = runner._load_module_config("auth")
        """
        config_path = self.project_root / "modules" / module_name / ".module.json"
        if config_path.exists():
            return json.loads(config_path.read_text(encoding="utf-8"))
        return None

    def _resolve_output_path(self, output_str: str, module: str) -> Path:
        """Resolve output path within a module's directory.

        Creates parent directories if they don't exist.
        Validates against path traversal attacks.

        Args:
            output_str: Relative path for the output file.
            module: Name of the module.

        Returns:
            Full path to the output file within the module directory.

        Raises:
            ValueError: If path contains traversal patterns.

        Example:
            >>> runner = ModularRunner(Path("/project"))
            >>> path = runner._resolve_output_path("src/auth.py", "auth")
        """
        # Security: reject path traversal attempts
        if ".." in output_str or output_str.startswith("/"):
            raise ValueError(f"Invalid output path: {output_str}")

        module_dir = self.project_root / "modules" / module
        output_path = module_dir / output_str

        # Resolve and verify path stays within module directory
        output_path = output_path.resolve()
        module_dir_resolved = module_dir.resolve()

        if not str(output_path).startswith(str(module_dir_resolved)):
            raise ValueError(f"Path traversal detected: {output_str}")

        # Create parent directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        return output_path
