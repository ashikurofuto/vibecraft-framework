"""
ModuleContextManager for Vibecraft Framework.

This module provides the ModuleContextManager class for managing
context.md files within module directories.

Example:
    >>> from vibecraft.modes.modular.context_manager import ModuleContextManager
    >>> from pathlib import Path
    >>>
    >>> cm = ModuleContextManager(Path("/project"))
    >>> context = cm.build_context("auth")
    >>> cm.update_context("auth", "## New Implementation Details")
"""

import json
from pathlib import Path
from typing import Any


class ModuleContextManager:
    """Manager for module context files.

    ModuleContextManager handles reading, writing, and updating
    context.md files within module directories.

    Attributes:
        project_root: Root directory of the project.

    Example:
        >>> cm = ModuleContextManager(Path("/project"))
        >>> cm.update_context("auth", "# Auth Module Context")
    """

    def __init__(self, project_root: Path) -> None:
        """Initialize the module context manager.

        Args:
            project_root: Root directory of the project.
        """
        self.project_root = project_root

    def _get_module_dir(self, module_name: str) -> Path:
        """Get the directory path for a module.

        Args:
            module_name: Name of the module.

        Returns:
            Path to the module directory.
        """
        return self.project_root / "modules" / module_name

    def _get_context_path(self, module_name: str) -> Path:
        """Get the path to a module's context.md file.

        Args:
            module_name: Name of the module.

        Returns:
            Path to the context.md file.
        """
        return self._get_module_dir(module_name) / "context.md"

    def build_context(self, module_name: str) -> str:
        """Build context string for a module.

        Reads the module's context.md file and returns its content.
        If the file doesn't exist, returns an empty string.

        Args:
            module_name: Name of the module.

        Returns:
            Context content as string, or empty string if not found.

        Example:
            >>> cm = ModuleContextManager(Path("/project"))
            >>> context = cm.build_context("auth")
        """
        context_path = self._get_context_path(module_name)
        if context_path.exists():
            return context_path.read_text(encoding="utf-8")
        return ""

    def update_context(self, module_name: str, content: str) -> None:
        """Update a module's context.md file.

        Creates the module directory and context.md file if they
        don't exist.

        Args:
            module_name: Name of the module.
            content: New content to write to context.md.

        Example:
            >>> cm = ModuleContextManager(Path("/project"))
            >>> cm.update_context("auth", "## Phase 1 Implementation")
        """
        module_dir = self._get_module_dir(module_name)
        module_dir.mkdir(parents=True, exist_ok=True)
        
        context_path = self._get_context_path(module_name)
        context_path.write_text(content, encoding="utf-8")

    def get_module_info(self, module_name: str) -> dict[str, Any] | None:
        """Get module information from .module.json.

        Args:
            module_name: Name of the module.

        Returns:
            Module info as dict, or None if module doesn't exist.

        Example:
            >>> cm = ModuleContextManager(Path("/project"))
            >>> info = cm.get_module_info("auth")
        """
        module_dir = self._get_module_dir(module_name)
        config_path = module_dir / ".module.json"

        if config_path.exists():
            return json.loads(config_path.read_text(encoding="utf-8"))
        return None

    def append_to_context(self, module_name: str, content: str) -> None:
        """Append content to a module's context.md file.

        Args:
            module_name: Name of the module.
            content: Content to append.

        Example:
            >>> cm = ModuleContextManager(Path("/project"))
            >>> cm.append_to_context("auth", "## New Section")
        """
        existing = self.build_context(module_name)
        # Add newline only if existing content doesn't end with one
        if existing and not existing.endswith("\n"):
            existing += "\n"
        self.update_context(module_name, existing + content)
