"""
Abstract base class for all bootstrappers in Vibecraft Framework.

This module defines the interface that all bootstrapper implementations
must follow, ensuring consistency across simple and modular modes.

Example:
    >>> from vibecraft.core import BaseBootstrapper, VibecraftConfig, ProjectMode
    >>> from pathlib import Path
    >>>
    >>> class MyBootstrapper(BaseBootstrapper):
    ...     def run(self) -> None:
    ...         print("Running bootstrap")
    ...     def validate(self) -> list[str]:
    ...         return []
    >>>
    >>> config = VibecraftConfig(mode=ProjectMode.SIMPLE, project_name="test")
    >>> bootstrapper = MyBootstrapper(Path("."), config)
    >>> bootstrapper.run()
    Running bootstrap
"""

from abc import ABC, abstractmethod
from pathlib import Path

from .config import VibecraftConfig


class BaseBootstrapper(ABC):
    """Abstract base class for all bootstrappers.

    All bootstrapper implementations must inherit from this class
    and implement the required abstract methods.

    Attributes:
        project_root: Root directory of the project.
        config: Vibecraft configuration object.

    Example:
        >>> class SimpleBootstrapper(BaseBootstrapper):
        ...     def run(self) -> None:
        ...         # Implementation here
        ...         pass
        ...     def validate(self) -> list[str]:
        ...         # Validation logic here
        ...         return []
    """

    def __init__(self, project_root: Path, config: VibecraftConfig) -> None:
        """Initialize the bootstrapper.

        Args:
            project_root: Root directory of the project.
            config: Vibecraft configuration object.
        """
        self.project_root = project_root
        self.config = config

    @abstractmethod
    def run(self) -> None:
        """Execute the bootstrapping process.

        This method should perform all necessary steps to initialize
        the project structure, generate agents, skills, and configuration.

        Raises:
            VibecraftError: If bootstrapping fails.
        """
        pass

    @abstractmethod
    def validate(self) -> list[str]:
        """Validate inputs before running.

        This method should check that all required inputs are present
        and valid before attempting to bootstrap.

        Returns:
            List of error messages (empty if validation passes).
        """
        pass
