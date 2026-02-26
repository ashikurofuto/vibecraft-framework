"""
Tests for BaseBootstrapper abstract base class.

These tests verify that:
1. BaseBootstrapper cannot be instantiated directly (ABC)
2. Concrete implementations must implement abstract methods
"""

import pytest
from pathlib import Path

from vibecraft.core.base_bootstrapper import BaseBootstrapper
from vibecraft.core.config import VibecraftConfig, ProjectMode


class TestBaseBootstrapperABC:
    """Tests for BaseBootstrapper abstract base class."""

    def test_base_bootstrapper_cannot_instantiate(self):
        """ABC нельзя создать напрямую.

        BaseBootstrapper is an abstract base class and should raise
        TypeError when attempting to instantiate it directly.
        """
        # Arrange
        project_root = Path("/tmp/test")
        config = VibecraftConfig(
            mode=ProjectMode.SIMPLE,
            project_name="Test Project"
        )

        # Act & Assert
        with pytest.raises(TypeError, match="abstract class"):
            BaseBootstrapper(project_root, config)

    def test_concrete_bootstrapper_implementation(self):
        """Concrete implementation must implement abstract methods.

        A concrete subclass must implement both run() and validate()
        methods, otherwise it cannot be instantiated.
        """
        # Arrange - incomplete implementation
        class IncompleteBootstrapper(BaseBootstrapper):
            def run(self) -> None:
                pass
            # Missing validate() method

        project_root = Path("/tmp/test")
        config = VibecraftConfig(
            mode=ProjectMode.SIMPLE,
            project_name="Test Project"
        )

        # Act & Assert
        with pytest.raises(TypeError, match="abstract method"):
            IncompleteBootstrapper(project_root, config)

    def test_complete_bootstrapper_implementation(self, tmp_path: Path):
        """Complete implementation can be instantiated.

        A concrete subclass that implements all abstract methods
        should be instantiable.
        """
        # Arrange - complete implementation
        class CompleteBootstrapper(BaseBootstrapper):
            def run(self) -> None:
                pass

            def validate(self) -> list[str]:
                return []

        project_root = tmp_path
        config = VibecraftConfig(
            mode=ProjectMode.SIMPLE,
            project_name="Test Project"
        )

        # Act
        bootstrapper = CompleteBootstrapper(project_root, config)

        # Assert
        assert bootstrapper is not None
        assert bootstrapper.project_root == project_root
        assert bootstrapper.config == config

    def test_base_bootstrapper_has_abstract_methods(self):
        """BaseBootstrapper defines required abstract methods."""
        # Assert
        assert "run" in BaseBootstrapper.__abstractmethods__
        assert "validate" in BaseBootstrapper.__abstractmethods__
