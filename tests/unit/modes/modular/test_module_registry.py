"""
Unit tests for ModuleRegistry.
"""
import pytest
from pathlib import Path
import json
from datetime import datetime, timezone


class TestModuleRegistryInit:
    """Tests for ModuleRegistry initialization."""

    def test_init_creates_registry(self, tmp_path: Path) -> None:
        """Test ModuleRegistry creates registry file on init."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry_path = tmp_path / "modules-registry.json"
        registry = ModuleRegistry(registry_path)

        assert registry_path.exists()
        data = json.loads(registry_path.read_text())
        assert "modules" in data
        assert "dependencies" in data
        assert "build_order" in data

    def test_init_with_existing_registry(self, tmp_path: Path) -> None:
        """Test ModuleRegistry loads existing registry."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry_path = tmp_path / "modules-registry.json"
        initial_data = {
            "modules": [{"name": "existing", "path": "modules/existing"}],
            "dependencies": {},
            "build_order": []
        }
        registry_path.write_text(json.dumps(initial_data))

        registry = ModuleRegistry(registry_path)
        modules = registry.get_all()

        assert len(modules) == 1
        assert modules[0]["name"] == "existing"

    def test_init_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Test ModuleRegistry creates parent directories."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry_path = tmp_path / "subdir" / "nested" / "modules-registry.json"
        registry = ModuleRegistry(registry_path)

        assert registry_path.exists()
        assert registry_path.parent.exists()


class TestModuleRegistryCRUD:
    """Tests for ModuleRegistry CRUD operations."""

    def test_add_module_dict(self, tmp_path: Path) -> None:
        """Test adding module using dictionary format."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry = ModuleRegistry(tmp_path / "registry.json")
        registry.add_module(
            name="auth",
            path="modules/auth",
            description="Authentication module"
        )

        modules = registry.get_all()
        assert len(modules) == 1
        assert modules[0]["name"] == "auth"
        assert modules[0]["path"] == "modules/auth"

    def test_add_module_object(self, tmp_path: Path) -> None:
        """Test adding module using Module object."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry
        from vibecraft.core.config import Module

        registry = ModuleRegistry(tmp_path / "registry.json")
        module = Module(
            name="api",
            path="modules/api",
            description="API module",
            status="planned"  # Valid status
        )
        registry.add_module(module)

        modules = registry.get_all()
        assert len(modules) == 1
        assert modules[0]["name"] == "api"
        assert modules[0]["status"] == "planned"

    def test_add_module_with_dependencies(self, tmp_path: Path) -> None:
        """Test adding module with dependencies."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry = ModuleRegistry(tmp_path / "registry.json")
        registry.add_module(
            name="api",
            path="modules/api",
            description="API module",
            dependencies=["auth", "database"]
        )

        modules = registry.get_all()
        assert modules[0]["dependencies"] == ["auth", "database"]

    def test_add_duplicate_module(self, tmp_path: Path) -> None:
        """Test adding duplicate module is idempotent."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry = ModuleRegistry(tmp_path / "registry.json")
        registry.add_module(name="auth", path="modules/auth", description="Auth")
        registry.add_module(name="auth", path="modules/auth", description="Auth")

        modules = registry.get_all()
        assert len(modules) == 1  # Should not duplicate

    def test_get_by_name_exists(self, tmp_path: Path) -> None:
        """Test get_by_name returns module if exists."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry = ModuleRegistry(tmp_path / "registry.json")
        registry.add_module(name="auth", path="modules/auth", description="Auth")

        module = registry.get_by_name("auth")
        assert module is not None
        assert module["name"] == "auth"

    def test_get_by_name_not_found(self, tmp_path: Path) -> None:
        """Test get_by_name returns None if not found."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry = ModuleRegistry(tmp_path / "registry.json")
        module = registry.get_by_name("nonexistent")

        assert module is None

    def test_get_module_by_name_object(self, tmp_path: Path) -> None:
        """Test get_module_by_name returns Module object."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry
        from vibecraft.core.config import Module

        registry = ModuleRegistry(tmp_path / "registry.json")
        registry.add_module(name="auth", path="modules/auth", description="Auth")

        module = registry.get_module_by_name("auth")
        assert module is not None
        assert isinstance(module, Module)
        assert module.name == "auth"

    def test_has_module_true(self, tmp_path: Path) -> None:
        """Test has_module returns True for existing module."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry = ModuleRegistry(tmp_path / "registry.json")
        registry.add_module(name="auth", path="modules/auth", description="Auth")

        assert registry.has_module("auth") is True

    def test_has_module_false(self, tmp_path: Path) -> None:
        """Test has_module returns False for nonexistent module."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry = ModuleRegistry(tmp_path / "registry.json")

        assert registry.has_module("nonexistent") is False


class TestUpdateModule:
    """Tests for ModuleRegistry.update_module()."""

    def test_update_module_dict(self, tmp_path: Path) -> None:
        """Test updating module using dictionary format."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry = ModuleRegistry(tmp_path / "registry.json")
        registry.add_module(name="auth", path="modules/auth", description="Auth")
        registry.update_module("auth", status="active", description="Updated")

        module = registry.get_by_name("auth")
        assert module is not None
        assert module["status"] == "active"
        assert module["description"] == "Updated"

    def test_update_module_object(self, tmp_path: Path) -> None:
        """Test updating module using Module object."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry
        from vibecraft.core.config import Module

        registry = ModuleRegistry(tmp_path / "registry.json")
        registry.add_module(name="auth", path="modules/auth", description="Auth")

        updated_module = Module(
            name="auth",
            path="modules/auth",
            description="New description",
            status="completed",
            exports=["AuthService"]
        )
        registry.update_module(updated_module)

        module = registry.get_module_by_name("auth")
        assert module is not None
        assert module.status == "completed"
        assert module.exports == ["AuthService"]

    def test_update_nonexistent_module(self, tmp_path: Path) -> None:
        """Test updating nonexistent module raises error."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry
        from vibecraft.core.exceptions import ModuleError

        registry = ModuleRegistry(tmp_path / "registry.json")

        with pytest.raises(ModuleError, match="not found"):
            registry.update_module("nonexistent", status="active")


class TestRemoveModule:
    """Tests for ModuleRegistry.remove_module()."""

    def test_remove_module_success(self, tmp_path: Path) -> None:
        """Test removing module successfully."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry = ModuleRegistry(tmp_path / "registry.json")
        registry.add_module(name="auth", path="modules/auth", description="Auth")

        registry.remove_module("auth")

        assert registry.has_module("auth") is False

    def test_remove_nonexistent_module(self, tmp_path: Path) -> None:
        """Test removing nonexistent module raises error."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry
        from vibecraft.core.exceptions import ModuleError

        registry = ModuleRegistry(tmp_path / "registry.json")

        with pytest.raises(ModuleError, match="not found"):
            registry.remove_module("nonexistent")


class TestModuleRegistryCache:
    """Tests for ModuleRegistry caching behavior."""

    def test_cache_invalidation(self, tmp_path: Path) -> None:
        """Test cache invalidation forces reload from disk."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry_path = tmp_path / "registry.json"
        registry = ModuleRegistry(registry_path)
        registry.add_module(name="auth", path="modules/auth", description="Auth")

        # Modify file directly
        data = json.loads(registry_path.read_text())
        data["modules"].append({
            "name": "api",
            "path": "modules/api",
            "description": "API"
        })
        registry_path.write_text(json.dumps(data))

        # Should still see cached data
        modules = registry.get_all()
        assert len(modules) == 1

        # Invalidate cache
        registry.invalidate_cache()

        # Should now see updated data
        modules = registry.get_all()
        assert len(modules) == 2


class TestModuleRegistryEdgeCases:
    """Tests for ModuleRegistry edge cases."""

    def test_empty_registry_operations(self, tmp_path: Path) -> None:
        """Test operations on empty registry."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry = ModuleRegistry(tmp_path / "registry.json")

        assert registry.get_all() == []
        assert registry.get_all_modules() == []
        assert registry.get_by_name("anything") is None

    def test_module_with_empty_fields(self, tmp_path: Path) -> None:
        """Test module with empty optional fields."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry

        registry = ModuleRegistry(tmp_path / "registry.json")
        registry.add_module(
            name="minimal",
            path="modules/minimal",
            description="",
            dependencies=[],
            exports=[]
        )

        module = registry.get_by_name("minimal")
        assert module is not None
        assert module["dependencies"] == []
        assert module["exports"] == []

    def test_module_created_at_timestamp(self, tmp_path: Path) -> None:
        """Test module created_at is properly stored and retrieved."""
        from vibecraft.modes.modular.module_registry import ModuleRegistry
        from vibecraft.core.config import Module

        registry = ModuleRegistry(tmp_path / "registry.json")
        registry.add_module(name="auth", path="modules/auth", description="Auth")

        module = registry.get_module_by_name("auth")
        assert module is not None
        assert module.created_at is not None
        # Verify created_at is a datetime object
        assert isinstance(module.created_at, datetime)
