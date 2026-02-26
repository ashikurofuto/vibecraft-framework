"""
Unit tests for ModuleManager.
"""
import pytest
from pathlib import Path
import json
from datetime import datetime, timezone


class TestModuleManagerInit:
    """Tests for ModuleManager initialization."""

    def test_init_creates_modules_dir(self, tmp_path: Path) -> None:
        """Test ModuleManager creates modules directory on init."""
        from vibecraft.modes.modular.module_manager import ModuleManager

        manager = ModuleManager(tmp_path)

        assert (tmp_path / "modules").exists()
        assert (tmp_path / "modules").is_dir()

    def test_init_with_existing_modules_dir(self, tmp_path: Path) -> None:
        """Test ModuleManager works with existing modules directory."""
        from vibecraft.modes.modular.module_manager import ModuleManager

        # Create modules dir beforehand
        modules_dir = tmp_path / "modules"
        modules_dir.mkdir()

        manager = ModuleManager(tmp_path)

        assert manager.modules_dir == modules_dir


class TestCreateModule:
    """Tests for ModuleManager.create_module()."""

    def test_create_module_success(self, tmp_path: Path) -> None:
        """Test creating a new module successfully."""
        from vibecraft.modes.modular.module_manager import ModuleManager

        manager = ModuleManager(tmp_path)
        result = manager.create_module(
            name="auth",
            description="Authentication module"
        )

        assert result["name"] == "auth"
        assert result["description"] == "Authentication module"
        assert result["status"] == "planned"
        assert result["dependencies"] == []
        assert "created_at" in result

        # Check module directory created
        module_dir = tmp_path / "modules" / "auth"
        assert module_dir.exists()
        assert (module_dir / ".module.json").exists()

    def test_create_module_with_dependencies(self, tmp_path: Path) -> None:
        """Test creating a module with dependencies."""
        from vibecraft.modes.modular.module_manager import ModuleManager

        manager = ModuleManager(tmp_path)
        result = manager.create_module(
            name="api",
            description="API module",
            dependencies=["auth", "database"]
        )

        assert result["dependencies"] == ["auth", "database"]

    def test_create_module_invalid_name(self, tmp_path: Path) -> None:
        """Test creating module with invalid name raises error."""
        from vibecraft.modes.modular.module_manager import ModuleManager
        from vibecraft.core.exceptions import ModuleError

        manager = ModuleManager(tmp_path)

        with pytest.raises(ModuleError):
            manager.create_module(
                name="invalid-name!",  # Contains special chars
                description="Bad name"
            )

    def test_create_module_already_exists(self, tmp_path: Path) -> None:
        """Test creating duplicate module raises error."""
        from vibecraft.modes.modular.module_manager import ModuleManager
        from vibecraft.core.exceptions import ModuleError

        manager = ModuleManager(tmp_path)
        manager.create_module(name="auth", description="Auth module")

        with pytest.raises(ModuleError, match="already exists"):
            manager.create_module(name="auth", description="Duplicate")

    def test_create_module_path_traversal_security(self, tmp_path: Path) -> None:
        """Test path traversal attack prevention."""
        from vibecraft.modes.modular.module_manager import ModuleManager
        from vibecraft.core.exceptions import ModuleError

        manager = ModuleManager(tmp_path)

        with pytest.raises(ModuleError):
            manager.create_module(
                name="../../../etc/passwd",
                description="Malicious path"
            )


class TestListModules:
    """Tests for ModuleManager.list_modules()."""

    def test_list_modules_empty(self, tmp_path: Path) -> None:
        """Test listing modules when none exist."""
        from vibecraft.modes.modular.module_manager import ModuleManager

        manager = ModuleManager(tmp_path)
        modules = manager.list_modules()

        assert modules == []

    def test_list_modules_with_one_module(self, tmp_path: Path) -> None:
        """Test listing modules with one module."""
        from vibecraft.modes.modular.module_manager import ModuleManager

        manager = ModuleManager(tmp_path)
        manager.create_module(name="auth", description="Auth module")

        modules = manager.list_modules()

        assert len(modules) == 1
        assert modules[0]["name"] == "auth"

    def test_list_modules_with_multiple_modules(self, tmp_path: Path) -> None:
        """Test listing modules with multiple modules."""
        from vibecraft.modes.modular.module_manager import ModuleManager

        manager = ModuleManager(tmp_path)
        manager.create_module(name="auth", description="Auth module")
        manager.create_module(name="api", description="API module")
        manager.create_module(name="database", description="Database module")

        modules = manager.list_modules()

        assert len(modules) == 3
        names = {m["name"] for m in modules}
        assert names == {"auth", "api", "database"}

    def test_list_modules_no_modules_dir(self, tmp_path: Path) -> None:
        """Test listing modules when modules dir doesn't exist."""
        from vibecraft.modes.modular.module_manager import ModuleManager

        # Remove modules dir if it exists (ModuleManager.__init__ creates it)
        import shutil
        modules_dir = tmp_path / "modules"
        if modules_dir.exists():
            shutil.rmtree(modules_dir)

        manager = ModuleManager(tmp_path)
        modules = manager.list_modules()

        assert modules == []


class TestGetStatus:
    """Tests for ModuleManager.get_status()."""

    def test_get_status_success(self, tmp_path: Path) -> None:
        """Test getting status of existing module."""
        from vibecraft.modes.modular.module_manager import ModuleManager

        manager = ModuleManager(tmp_path)
        manager.create_module(name="auth", description="Auth module")

        status = manager.get_status("auth")

        assert status["name"] == "auth"
        assert status["status"] == "planned"

    def test_get_status_nonexistent_module(self, tmp_path: Path) -> None:
        """Test getting status of nonexistent module raises error."""
        from vibecraft.modes.modular.module_manager import ModuleManager
        from vibecraft.core.exceptions import ModuleError

        manager = ModuleManager(tmp_path)

        with pytest.raises(ModuleError, match="not found"):
            manager.get_status("nonexistent")

    def test_get_status_no_module_json(self, tmp_path: Path) -> None:
        """Test getting status when .module.json is missing."""
        from vibecraft.modes.modular.module_manager import ModuleManager
        from vibecraft.core.exceptions import ModuleError

        manager = ModuleManager(tmp_path)

        # Create module dir without .module.json
        module_dir = tmp_path / "modules" / "broken"
        module_dir.mkdir()

        with pytest.raises(ModuleError, match="no .module.json"):
            manager.get_status("broken")


class TestInitModule:
    """Tests for ModuleManager.init_module()."""

    def test_init_module_creates_structure(self, tmp_path: Path) -> None:
        """Test init_module creates module structure."""
        from vibecraft.modes.modular.module_manager import ModuleManager

        manager = ModuleManager(tmp_path)
        manager.create_module(name="auth", description="Auth module")
        manager.init_module("auth")

        module_dir = tmp_path / "modules" / "auth"

        assert (module_dir / "research.md").exists()
        assert (module_dir / "stack.md").exists()
        assert (module_dir / "agents").is_dir()
        assert (module_dir / "skills").is_dir()

    def test_init_module_nonexistent(self, tmp_path: Path) -> None:
        """Test init_module on nonexistent module raises error."""
        from vibecraft.modes.modular.module_manager import ModuleManager
        from vibecraft.core.exceptions import ModuleError

        manager = ModuleManager(tmp_path)

        with pytest.raises(ModuleError, match="not found"):
            manager.init_module("nonexistent")

    def test_init_module_preserves_existing_files(self, tmp_path: Path) -> None:
        """Test init_module doesn't overwrite existing files."""
        from vibecraft.modes.modular.module_manager import ModuleManager

        manager = ModuleManager(tmp_path)
        manager.create_module(name="auth", description="Auth module")

        # Create custom research.md
        research_file = tmp_path / "modules" / "auth" / "research.md"
        custom_content = "# Custom Research\n\nMy content"
        research_file.write_text(custom_content)

        manager.init_module("auth")

        # Should preserve existing content
        assert research_file.read_text() == custom_content


class TestModuleRegistryIntegration:
    """Tests for ModuleManager integration with ModuleRegistry."""

    def test_create_module_updates_registry(self, tmp_path: Path) -> None:
        """Test creating module updates modules-registry.json."""
        from vibecraft.modes.modular.module_manager import ModuleManager

        manager = ModuleManager(tmp_path)
        manager.create_module(
            name="auth",
            description="Authentication module",
            dependencies=["database"]
        )

        registry_path = tmp_path / ".vibecraft" / "modules-registry.json"
        assert registry_path.exists()

        registry_data = json.loads(registry_path.read_text())
        assert len(registry_data["modules"]) == 1
        assert registry_data["modules"][0]["name"] == "auth"
        assert registry_data["modules"][0]["dependencies"] == ["database"]

    def test_create_multiple_modules_registry(self, tmp_path: Path) -> None:
        """Test creating multiple modules updates registry correctly."""
        from vibecraft.modes.modular.module_manager import ModuleManager

        manager = ModuleManager(tmp_path)
        manager.create_module(name="auth", description="Auth")
        manager.create_module(name="api", description="API")

        registry_data = json.loads(
            (tmp_path / ".vibecraft" / "modules-registry.json").read_text()
        )

        assert len(registry_data["modules"]) == 2
        names = {m["name"] for m in registry_data["modules"]}
        assert names == {"auth", "api"}
