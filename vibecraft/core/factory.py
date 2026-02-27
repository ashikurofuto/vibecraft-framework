"""
BootstrapperFactory for creating mode-specific bootstrappers.

This module implements the Factory Pattern for creating appropriate
bootstrapper instances based on the project mode.

Example:
    >>> from vibecraft.core.factory import BootstrapperFactory
    >>> from vibecraft.core.config import VibecraftConfig, ProjectMode
    >>> from pathlib import Path
    >>>
    >>> config = VibecraftConfig(project_name="test", mode=ProjectMode.SIMPLE)
    >>> bootstrapper = BootstrapperFactory.create(
    ...     mode=ProjectMode.SIMPLE,
    ...     project_root=Path("."),
    ...     config=config
    ... )
"""

from pathlib import Path
from typing import Any

from .base_bootstrapper import BaseBootstrapper
from .config import ProjectMode, VibecraftConfig


class BootstrapperFactory:
    """Factory for creating mode-specific bootstrappers.

    This factory centralizes the creation of bootstrapper instances,
    making it easy to add new modes without modifying client code.

    Example:
        >>> config = VibecraftConfig(project_name="test")
        >>> bootstrapper = BootstrapperFactory.create(
        ...     mode="simple",
        ...     project_root=Path("/project"),
        ...     config=config
        ... )
    """

    @staticmethod
    def create(
        mode: ProjectMode | str,
        project_root: Path,
        config: VibecraftConfig,
        **kwargs: Any
    ) -> BaseBootstrapper:
        """Create appropriate bootstrapper for the specified mode.

        Args:
            mode: Project mode (SIMPLE or MODULAR). Can be string or enum.
            project_root: Root directory of the project.
            config: Vibecraft configuration object.
            **kwargs: Additional arguments passed to bootstrapper constructor.

        Returns:
            An instance of the appropriate bootstrapper class.

        Raises:
            ValueError: If mode is unknown or invalid.

        Example:
            >>> config = VibecraftConfig(project_name="test")
            >>> bs = BootstrapperFactory.create(
            ...     mode=ProjectMode.SIMPLE,
            ...     project_root=Path("."),
            ...     config=config
            ... )
        """
        # Convert string to enum if needed
        if isinstance(mode, str):
            try:
                mode = ProjectMode(mode.lower())
            except ValueError:
                raise ValueError(f"Unknown mode: '{mode}'")

        if mode == ProjectMode.SIMPLE:
            # Import here to avoid circular dependencies
            from vibecraft.modes.simple.bootstrapper import SimpleBootstrapper

            # Extract only the arguments that SimpleBootstrapper expects
            research_path = kwargs.get('research_path', project_root / "docs" / "research.md")
            stack_path = kwargs.get('stack_path', project_root / "docs" / "stack.md")
            custom_agents_path = kwargs.get('custom_agents_path', None)
            force = kwargs.get('force', False)

            # Build kwargs for SimpleBootstrapper (new API with project_root)
            simple_kwargs = {
                'project_root': project_root,
                'config': config,
                'research_path': research_path,
                'stack_path': stack_path,
            }
            if custom_agents_path is not None:
                simple_kwargs['custom_agents_path'] = custom_agents_path
            if force:
                simple_kwargs['force'] = force

            return SimpleBootstrapper(**simple_kwargs)
        elif mode == ProjectMode.MODULAR:
            # For modular mode, import from modes.modular package
            from vibecraft.modes.modular import ModularBootstrapper
            return ModularBootstrapper(
                project_root=project_root,
                config=config,
                **kwargs
            )
        else:
            raise ValueError(f"Unknown mode: {mode}")
