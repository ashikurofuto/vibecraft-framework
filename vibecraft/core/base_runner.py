"""
Abstract base class for all runners in Vibecraft Framework.

This module defines the interface that all runner implementations
must follow, ensuring consistency across simple and modular modes.

Example:
    >>> from vibecraft.core import BaseRunner
    >>> from pathlib import Path
    >>>
    >>> class MyRunner(BaseRunner):
    ...     def run(self, skill_name: str, **kwargs) -> None:
    ...         print(f"Running skill: {skill_name}")
    >>>
    >>> runner = MyRunner(Path("."))
    >>> runner.run("research")
    Running skill: research
"""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseRunner(ABC):
    """Abstract base class for all runners.

    All runner implementations must inherit from this class
    and implement the required abstract methods.

    Attributes:
        project_root: Root directory of the project.

    Example:
        >>> class SimpleRunner(BaseRunner):
        ...     def run(self, skill_name: str, **kwargs) -> None:
        ...         # Implementation here
        ...         pass
    """

    def __init__(self, project_root: Path) -> None:
        """Initialize the runner.

        Args:
            project_root: Root directory of the project.
        """
        self.project_root = project_root

    @abstractmethod
    def run(self, skill_name: str, **kwargs) -> None:
        """Execute a skill.

        This method should perform all necessary steps to run
        the specified skill, including building prompts, calling
        agents, and updating project state.

        Args:
            skill_name: Name of the skill to execute.
            **kwargs: Additional arguments for the skill.

        Raises:
            VibecraftError: If skill execution fails.
        """
        pass
