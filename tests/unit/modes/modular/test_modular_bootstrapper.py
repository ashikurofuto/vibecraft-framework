"""
Tests for Vibecraft ModularBootstrapper.

Tests verify modular project bootstrapping creates correct structure.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime

from vibecraft.core.config import VibecraftConfig, ProjectMode, ProjectType
from vibecraft.modes.modular import ModularBootstrapper


class TestModularBootstrapper:
    """Tests for ModularBootstrapper class."""

    @pytest.fixture
    def config(self) -> VibecraftConfig:
        """Create modular mode configuration."""
        return VibecraftConfig(
            project_name="Test Modular Project",
            mode=ProjectMode.MODULAR,
        )

    @pytest.fixture
    def bootstrapper(self, tmp_path: Path, config: VibecraftConfig) -> ModularBootstrapper:
        """Create ModularBootstrapper instance."""
        project_root = tmp_path / "test-project"
        return ModularBootstrapper(project_root, config)

    def test_init_stores_project_root(self, tmp_path: Path, config: VibecraftConfig):
        """__init__ stores project_root attribute."""
        # Arrange
        project_root = tmp_path / "test-project"

        # Act
        bootstrapper = ModularBootstrapper(project_root, config)

        # Assert
        assert bootstrapper.project_root == project_root

    def test_init_stores_config(self, tmp_path: Path, config: VibecraftConfig):
        """__init__ stores config attribute."""
        # Arrange
        project_root = tmp_path / "test-project"

        # Act
        bootstrapper = ModularBootstrapper(project_root, config)

        # Assert
        assert bootstrapper.config == config

    def test_init_stores_kwargs(self, tmp_path: Path, config: VibecraftConfig):
        """__init__ stores extra kwargs in _kwargs."""
        # Arrange
        project_root = tmp_path / "test-project"

        # Act
        bootstrapper = ModularBootstrapper(
            project_root, config, extra_arg="value"
        )

        # Assert
        assert bootstrapper._kwargs == {"extra_arg": "value"}

    def test_run_creates_modules_directory(self, bootstrapper: ModularBootstrapper):
        """run() creates modules/ directory."""
        # Act
        bootstrapper.run()

        # Assert
        assert (bootstrapper.project_root / "modules").is_dir()

    def test_run_creates_shared_directory(self, bootstrapper: ModularBootstrapper):
        """run() creates shared/ directory."""
        # Act
        bootstrapper.run()

        # Assert
        assert (bootstrapper.project_root / "shared").is_dir()

    def test_run_creates_integration_directory(self, bootstrapper: ModularBootstrapper):
        """run() creates integration/ directory."""
        # Act
        bootstrapper.run()

        # Assert
        assert (bootstrapper.project_root / "integration").is_dir()

    def test_run_creates_vibecraft_structure(self, bootstrapper: ModularBootstrapper):
        """run() creates .vibecraft/ with agents/, skills/, prompts/, snapshots/."""
        # Act
        bootstrapper.run()

        # Assert
        vc_dir = bootstrapper.project_root / ".vibecraft"
        assert vc_dir.is_dir()
        assert (vc_dir / "agents").is_dir()
        assert (vc_dir / "skills").is_dir()
        assert (vc_dir / "prompts").is_dir()
        assert (vc_dir / "snapshots").is_dir()

    def test_run_creates_docs_structure(self, bootstrapper: ModularBootstrapper):
        """run() creates docs/ with design/ and plans/."""
        # Act
        bootstrapper.run()

        # Assert
        docs_dir = bootstrapper.project_root / "docs"
        assert docs_dir.is_dir()
        assert (docs_dir / "design").is_dir()
        assert (docs_dir / "plans").is_dir()

    def test_run_creates_src_tests_directory(self, bootstrapper: ModularBootstrapper):
        """run() creates src/tests/ directory."""
        # Act
        bootstrapper.run()

        # Assert
        assert (bootstrapper.project_root / "src" / "tests").is_dir()

    def test_run_creates_modules_registry(self, bootstrapper: ModularBootstrapper):
        """run() creates .vibecraft/modules-registry.json."""
        # Act
        bootstrapper.run()

        # Assert
        registry_path = bootstrapper.project_root / ".vibecraft" / "modules-registry.json"
        assert registry_path.exists()

    def test_run_modules_registry_has_correct_structure(
        self, bootstrapper: ModularBootstrapper
    ):
        """run() creates registry with modules, dependencies, build_order."""
        # Act
        bootstrapper.run()

        # Assert
        registry_path = bootstrapper.project_root / ".vibecraft" / "modules-registry.json"
        registry = json.loads(registry_path.read_text())

        assert "modules" in registry
        assert "dependencies" in registry
        assert "build_order" in registry
        assert registry["modules"] == []
        assert registry["dependencies"] == {}
        assert registry["build_order"] == []

    def test_run_creates_manifest(self, bootstrapper: ModularBootstrapper):
        """run() creates .vibecraft/manifest.json."""
        # Act
        bootstrapper.run()

        # Assert
        manifest_path = bootstrapper.project_root / ".vibecraft" / "manifest.json"
        assert manifest_path.exists()

    def test_run_manifest_has_correct_structure(
        self, bootstrapper: ModularBootstrapper
    ):
        """run() creates manifest with required fields."""
        # Act
        bootstrapper.run()

        # Assert
        manifest_path = bootstrapper.project_root / ".vibecraft" / "manifest.json"
        manifest = json.loads(manifest_path.read_text())

        assert manifest["mode"] == "modular"
        assert manifest["version"] == "0.4.0"
        assert manifest["project_name"] == "Test Modular Project"
        assert manifest["current_phase"] == "research"
        assert manifest["phases"] == [
            "research", "design", "plan", "implement", "review"
        ]
        assert manifest["phases_completed"] == []

    def test_run_manifest_includes_timestamp(
        self, bootstrapper: ModularBootstrapper
    ):
        """run() includes created_at timestamp in manifest."""
        # Act
        bootstrapper.run()

        # Assert
        manifest_path = bootstrapper.project_root / ".vibecraft" / "manifest.json"
        manifest = json.loads(manifest_path.read_text())

        assert "created_at" in manifest
        # Should be ISO format with Z suffix
        assert manifest["created_at"].endswith("Z")

    def test_validate_returns_empty_for_valid_config(
        self, bootstrapper: ModularBootstrapper
    ):
        """validate() returns empty list when config is valid."""
        # Arrange - project root exists
        bootstrapper.project_root.mkdir(parents=True, exist_ok=True)

        # Act
        result = bootstrapper.validate()

        # Assert
        assert result == []

    def test_create_manifest_project_type_list_handling(
        self, tmp_path: Path
    ):
        """_create_manifest handles both list and single project_type."""
        # Arrange - single project type (not list)
        config = VibecraftConfig(
            project_name="Test",
            project_type=ProjectType.API,
        )
        project_root = tmp_path / "test"
        project_root.mkdir()
        bootstrapper = ModularBootstrapper(project_root, config)
        # Create .vibecraft directory (normally done by run())
        (project_root / ".vibecraft").mkdir()

        # Act
        bootstrapper._create_manifest()

        # Assert
        manifest_path = project_root / ".vibecraft" / "manifest.json"
        manifest = json.loads(manifest_path.read_text())

        # project_type should be converted to list
        assert isinstance(manifest["project_type"], list)
