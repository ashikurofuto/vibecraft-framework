"""
Tests for BaseRunner abstract base class.

These tests verify that:
1. BaseRunner cannot be instantiated directly (ABC)
2. Concrete implementations must implement abstract methods
"""

import pytest
from pathlib import Path

from vibecraft.core.base_runner import BaseRunner


class TestBaseRunnerABC:
    """Tests for BaseRunner abstract base class."""

    def test_base_runner_cannot_instantiate(self):
        """ABC нельзя создать напрямую.

        BaseRunner is an abstract base class and should raise
        TypeError when attempting to instantiate it directly.
        """
        # Arrange
        project_root = Path("/tmp/test")

        # Act & Assert
        with pytest.raises(TypeError, match="abstract class"):
            BaseRunner(project_root)

    def test_concrete_runner_implementation(self):
        """Concrete implementation must implement abstract methods.

        A concrete subclass must implement the run() method,
        otherwise it cannot be instantiated.
        """
        # Arrange - incomplete implementation (no run method)
        class IncompleteRunner(BaseRunner):
            pass

        project_root = Path("/tmp/test")

        # Act & Assert
        with pytest.raises(TypeError, match="abstract method"):
            IncompleteRunner(project_root)

    def test_complete_runner_implementation(self, tmp_path: Path):
        """Complete implementation can be instantiated.

        A concrete subclass that implements all abstract methods
        should be instantiable.
        """
        # Arrange - complete implementation
        class CompleteRunner(BaseRunner):
            def run(self, skill_name: str, **kwargs) -> None:
                pass

        project_root = tmp_path

        # Act
        runner = CompleteRunner(project_root)

        # Assert
        assert runner is not None
        assert runner.project_root == project_root

    def test_base_runner_has_abstract_methods(self):
        """BaseRunner defines required abstract methods."""
        # Assert
        assert "run" in BaseRunner.__abstractmethods__
