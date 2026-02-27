"""Tests for ModularBootstrapper (re-exported from _bootstrapper.py)."""

import json
import pytest
from pathlib import Path
from vibecraft.modes.modular import ModularBootstrapper
from vibecraft.core.config import VibecraftConfig, ProjectMode


class TestModularBootstrapperInit:
    """Tests for ModularBootstrapper initialization."""

    def test_init_stores_project_root_and_config(self, tmp_path: Path) -> None:
        """Should store project_root and config."""
        config = VibecraftConfig(project_name="Test", mode=ProjectMode.MODULAR)
        bootstrapper = ModularBootstrapper(tmp_path, config)

        assert bootstrapper.project_root == tmp_path
        assert bootstrapper.config == config

    def test_init_accepts_kwargs(self, tmp_path: Path) -> None:
        """Should accept and store additional kwargs."""
        config = VibecraftConfig(project_name="Test", mode=ProjectMode.MODULAR)
        bootstrapper = ModularBootstrapper(
            tmp_path, config, custom_arg="value", another_arg=42
        )

        assert hasattr(bootstrapper, "_kwargs")
        assert bootstrapper._kwargs == {"custom_arg": "value", "another_arg": 42}


class TestModularBootstrapperRun:
    """Tests for ModularBootstrapper.run() method."""

    @pytest.fixture
    def bootstrapper(self, tmp_path: Path) -> ModularBootstrapper:
        """Create ModularBootstrapper for testing."""
        config = VibecraftConfig(project_name="Test Project", mode=ProjectMode.MODULAR)
        return ModularBootstrapper(tmp_path, config)

    def test_run_creates_modules_directory(self, bootstrapper: ModularBootstrapper) -> None:
        """Should create modules/ directory."""
        bootstrapper.run()

        modules_dir = bootstrapper.project_root / "modules"
        assert modules_dir.exists()
        assert modules_dir.is_dir()

    def test_run_creates_shared_directory(self, bootstrapper: ModularBootstrapper) -> None:
        """Should create shared/ directory."""
        bootstrapper.run()

        shared_dir = bootstrapper.project_root / "shared"
        assert shared_dir.exists()
        assert shared_dir.is_dir()

    def test_run_creates_integration_directory(self, bootstrapper: ModularBootstrapper) -> None:
        """Should create integration/ directory."""
        bootstrapper.run()

        integration_dir = bootstrapper.project_root / "integration"
        assert integration_dir.exists()
        assert integration_dir.is_dir()

    def test_run_creates_vibecraft_structure(self, bootstrapper: ModularBootstrapper) -> None:
        """Should create .vibecraft/ with subdirectories."""
        bootstrapper.run()

        vibecraft_dir = bootstrapper.project_root / ".vibecraft"
        assert vibecraft_dir.exists()
        assert (vibecraft_dir / "agents").exists()
        assert (vibecraft_dir / "skills").exists()
        assert (vibecraft_dir / "prompts").exists()
        assert (vibecraft_dir / "snapshots").exists()

    def test_run_creates_docs_structure(self, bootstrapper: ModularBootstrapper) -> None:
        """Should create docs/ with subdirectories."""
        bootstrapper.run()

        docs_dir = bootstrapper.project_root / "docs"
        assert docs_dir.exists()
        assert (docs_dir / "design").exists()
        assert (docs_dir / "plans").exists()

    def test_run_creates_src_tests_directory(self, bootstrapper: ModularBootstrapper) -> None:
        """Should create src/tests/ directory."""
        bootstrapper.run()

        src_tests_dir = bootstrapper.project_root / "src" / "tests"
        assert src_tests_dir.exists()

    def test_run_creates_modules_registry(self, bootstrapper: ModularBootstrapper) -> None:
        """Should create modules-registry.json."""
        bootstrapper.run()

        registry_path = bootstrapper.project_root / ".vibecraft" / "modules-registry.json"
        assert registry_path.exists()

    def test_run_modules_registry_has_correct_structure(self, bootstrapper: ModularBootstrapper) -> None:
        """Should create registry with correct initial structure."""
        bootstrapper.run()

        registry_path = bootstrapper.project_root / ".vibecraft" / "modules-registry.json"
        registry = json.loads(registry_path.read_text())

        assert "modules" in registry
        assert "dependencies" in registry
        assert "build_order" in registry
        assert registry["modules"] == []
        assert registry["dependencies"] == {}
        assert registry["build_order"] == []

    def test_run_creates_manifest(self, bootstrapper: ModularBootstrapper) -> None:
        """Should create manifest.json."""
        bootstrapper.run()

        manifest_path = bootstrapper.project_root / ".vibecraft" / "manifest.json"
        assert manifest_path.exists()

    def test_run_manifest_has_correct_structure(self, bootstrapper: ModularBootstrapper) -> None:
        """Should create manifest with correct structure."""
        bootstrapper.run()

        manifest_path = bootstrapper.project_root / ".vibecraft" / "manifest.json"
        manifest = json.loads(manifest_path.read_text())

        assert manifest["mode"] == "modular"
        assert "version" in manifest
        assert manifest["project_name"] == "Test Project"
        assert "project_type" in manifest
        assert "created_at" in manifest
        assert "stack" in manifest
        assert "agents" in manifest
        assert "skills" in manifest
        assert "current_phase" in manifest
        assert "phases" in manifest
        assert "phases_completed" in manifest

    def test_run_manifest_includes_timestamp(self, bootstrapper: ModularBootstrapper) -> None:
        """Should include ISO format timestamp in manifest."""
        bootstrapper.run()

        manifest_path = bootstrapper.project_root / ".vibecraft" / "manifest.json"
        manifest = json.loads(manifest_path.read_text())

        created_at = manifest["created_at"]
        assert "T" in created_at  # ISO format contains T separator
        assert created_at.endswith("Z")  # UTC timezone

    def test_run_manifest_project_type_list_handling(self, tmp_path: Path) -> None:
        """Should handle project_type as list correctly."""
        config = VibecraftConfig(
            project_name="Test",
            mode=ProjectMode.MODULAR,
            project_type=["web", "api", "cli"]
        )
        bootstrapper = ModularBootstrapper(tmp_path, config)
        bootstrapper.run()

        manifest_path = tmp_path / ".vibecraft" / "manifest.json"
        manifest = json.loads(manifest_path.read_text())

        assert manifest["project_type"] == ["web", "api", "cli"]


class TestModularBootstrapperValidate:
    """Tests for ModularBootstrapper.validate() method."""

    def test_validate_returns_empty_for_valid_config(self, tmp_path: Path) -> None:
        """Should return empty list for valid configuration."""
        config = VibecraftConfig(project_name="Valid Project", mode=ProjectMode.MODULAR)
        bootstrapper = ModularBootstrapper(tmp_path, config)

        errors = bootstrapper.validate()

        assert errors == []

    def test_validate_returns_error_for_empty_project_name(self, tmp_path: Path) -> None:
        """Should return error when project_name is empty."""
        # Use monkeypatch to bypass Pydantic validation for testing validate() method
        from vibecraft.core.config import VibecraftConfig
        
        # Create config with minimal valid name, then manually set to empty
        config = VibecraftConfig(project_name="Temp", mode=ProjectMode.MODULAR)
        config.project_name = ""  # Bypass validation for this test
        bootstrapper = ModularBootstrapper(tmp_path, config)

        errors = bootstrapper.validate()

        assert len(errors) == 1
        assert "Project name is required" in errors[0]

    def test_validate_creates_project_root_if_not_exists(self, tmp_path: Path) -> None:
        """Should create project_root if it doesn't exist."""
        new_root = tmp_path / "new_project"
        config = VibecraftConfig(project_name="Test", mode=ProjectMode.MODULAR)
        bootstrapper = ModularBootstrapper(new_root, config)

        errors = bootstrapper.validate()

        assert errors == []
        assert new_root.exists()

    def test_validate_returns_error_if_cannot_create_root(self, tmp_path: Path) -> None:
        """Should return error when cannot create project root."""
        # Try to create directory inside a file (should fail)
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")
        
        invalid_root = file_path / "invalid_dir"
        config = VibecraftConfig(project_name="Test", mode=ProjectMode.MODULAR)
        bootstrapper = ModularBootstrapper(invalid_root, config)

        errors = bootstrapper.validate()

        assert len(errors) == 1
        assert "Cannot create project root" in errors[0]
