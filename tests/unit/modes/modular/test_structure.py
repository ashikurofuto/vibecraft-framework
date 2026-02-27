"""
Tests for Vibecraft modular structure creation.

Tests verify create_modular_structure creates correct directory layout.
"""

import pytest
from pathlib import Path
from vibecraft.modes.modular.structure import create_modular_structure


class TestCreateModularStructure:
    """Tests for create_modular_structure function."""

    def test_creates_modules_directory(self, tmp_path: Path):
        """Function creates modules/ directory."""
        # Arrange
        project_root = tmp_path / "test-project"
        project_root.mkdir()

        # Act
        create_modular_structure(project_root)

        # Assert
        assert (project_root / "modules").is_dir()

    def test_creates_shared_directory(self, tmp_path: Path):
        """Function creates shared/ directory."""
        # Arrange
        project_root = tmp_path / "test-project"
        project_root.mkdir()

        # Act
        create_modular_structure(project_root)

        # Assert
        assert (project_root / "shared").is_dir()

    def test_creates_integration_directory(self, tmp_path: Path):
        """Function creates integration/ directory."""
        # Arrange
        project_root = tmp_path / "test-project"
        project_root.mkdir()

        # Act
        create_modular_structure(project_root)

        # Assert
        assert (project_root / "integration").is_dir()

    def test_creates_vibecraft_directory(self, tmp_path: Path):
        """Function creates .vibecraft/ directory."""
        # Arrange
        project_root = tmp_path / "test-project"
        project_root.mkdir()

        # Act
        create_modular_structure(project_root)

        # Assert
        assert (project_root / ".vibecraft").is_dir()

    def test_creates_vibecraft_subdirectories(self, tmp_path: Path):
        """Function creates .vibecraft/agents/, skills/, prompts/, snapshots/."""
        # Arrange
        project_root = tmp_path / "test-project"
        project_root.mkdir()

        # Act
        create_modular_structure(project_root)

        # Assert
        assert (project_root / ".vibecraft" / "agents").is_dir()
        assert (project_root / ".vibecraft" / "skills").is_dir()
        assert (project_root / ".vibecraft" / "prompts").is_dir()
        assert (project_root / ".vibecraft" / "snapshots").is_dir()

    def test_creates_docs_directory(self, tmp_path: Path):
        """Function creates docs/ directory."""
        # Arrange
        project_root = tmp_path / "test-project"
        project_root.mkdir()

        # Act
        create_modular_structure(project_root)

        # Assert
        assert (project_root / "docs").is_dir()

    def test_creates_docs_subdirectories(self, tmp_path: Path):
        """Function creates docs/design/ and docs/plans/."""
        # Arrange
        project_root = tmp_path / "test-project"
        project_root.mkdir()

        # Act
        create_modular_structure(project_root)

        # Assert
        assert (project_root / "docs" / "design").is_dir()
        assert (project_root / "docs" / "plans").is_dir()

    def test_creates_src_tests_directory(self, tmp_path: Path):
        """Function creates src/tests/ directory."""
        # Arrange
        project_root = tmp_path / "test-project"
        project_root.mkdir()

        # Act
        create_modular_structure(project_root)

        # Assert
        assert (project_root / "src" / "tests").is_dir()

    def test_creates_all_directories_in_single_call(self, tmp_path: Path):
        """Function creates complete directory tree in one call."""
        # Arrange
        project_root = tmp_path / "test-project"
        project_root.mkdir()

        # Act
        create_modular_structure(project_root)

        # Assert - verify all expected directories exist
        expected_dirs = [
            "modules",
            "shared",
            "integration",
            ".vibecraft",
            ".vibecraft/agents",
            ".vibecraft/skills",
            ".vibecraft/prompts",
            ".vibecraft/snapshots",
            "docs",
            "docs/design",
            "docs/plans",
            "src/tests",
        ]

        for dir_path in expected_dirs:
            full_path = project_root / dir_path
            assert full_path.is_dir(), f"Missing directory: {dir_path}"

    def test_works_on_existing_directory_structure(self, tmp_path: Path):
        """Function does not fail when directories already exist."""
        # Arrange
        project_root = tmp_path / "test-project"
        project_root.mkdir()
        # Pre-create some directories
        (project_root / "modules").mkdir()
        (project_root / "docs").mkdir()

        # Act - should not raise
        create_modular_structure(project_root)

        # Assert - directories still exist
        assert (project_root / "modules").is_dir()
        assert (project_root / "docs").is_dir()
        assert (project_root / "integration").is_dir()

    def test_creates_parent_directories_when_needed(self, tmp_path: Path):
        """Function creates parent directories with parents=True."""
        # Arrange
        project_root = tmp_path / "deep" / "nested" / "project"

        # Act
        create_modular_structure(project_root)

        # Assert - parent dirs created automatically
        assert project_root.is_dir()
        assert (project_root / "modules").is_dir()
        assert (project_root / "src" / "tests").is_dir()
