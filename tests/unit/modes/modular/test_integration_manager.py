"""
Unit tests for IntegrationManager.
"""
import pytest
from pathlib import Path
import json


class TestIntegrationManagerInit:
    """Tests for IntegrationManager initialization."""

    def test_init_basic(self, tmp_path: Path) -> None:
        """Test IntegrationManager basic initialization."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        manager = IntegrationManager(tmp_path)

        assert manager.project_root == tmp_path
        assert manager.integration_dir == tmp_path / "integration"
        assert manager.registry_path == tmp_path / ".vibecraft" / "modules-registry.json"

    def test_init_creates_no_dirs(self, tmp_path: Path) -> None:
        """Test IntegrationManager does not create dirs on init."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        manager = IntegrationManager(tmp_path)

        # Should not create integration dir until build
        assert not (tmp_path / "integration").exists()


class TestAnalyzeDependencies:
    """Tests for IntegrationManager.analyze_dependencies()."""

    def test_analyze_empty_registry(self, tmp_path: Path) -> None:
        """Test analyze_dependencies with empty registry."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        # Create empty registry
        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        errors = manager.analyze_dependencies()

        assert errors == []

    def test_analyze_no_registry(self, tmp_path: Path) -> None:
        """Test analyze_dependencies when registry doesn't exist."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        manager = IntegrationManager(tmp_path)
        errors = manager.analyze_dependencies()

        assert errors == []  # Should handle gracefully

    def test_analyze_valid_dependencies(self, tmp_path: Path) -> None:
        """Test analyze_dependencies with valid module dependencies."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        # Create registry with valid deps
        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [
                {"name": "database", "dependencies": []},
                {"name": "auth", "dependencies": ["database"]},
                {"name": "api", "dependencies": ["auth", "database"]}
            ],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        errors = manager.analyze_dependencies()

        assert errors == []

    def test_analyze_missing_dependency(self, tmp_path: Path) -> None:
        """Test analyze_dependencies detects missing dependencies."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [
                {"name": "api", "dependencies": ["nonexistent"]}
            ],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        errors = manager.analyze_dependencies()

        assert len(errors) > 0
        assert "nonexistent" in " ".join(errors)

    def test_analyze_circular_dependencies(self, tmp_path: Path) -> None:
        """Test analyze_dependencies detects circular dependencies."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [
                {"name": "a", "dependencies": ["b"]},
                {"name": "b", "dependencies": ["c"]},
                {"name": "c", "dependencies": ["a"]}  # Circular!
            ],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        errors = manager.analyze_dependencies()

        assert len(errors) > 0
        assert "Circular" in " ".join(errors) or "cycle" in " ".join(errors).lower()


class TestGetBuildOrder:
    """Tests for IntegrationManager.get_build_order()."""

    def test_build_order_empty(self, tmp_path: Path) -> None:
        """Test get_build_order with empty registry."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        order = manager.get_build_order()

        assert order == []

    def test_build_order_no_deps(self, tmp_path: Path) -> None:
        """Test get_build_order with modules having no dependencies."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [
                {"name": "auth", "dependencies": []},
                {"name": "api", "dependencies": []},
                {"name": "database", "dependencies": []}
            ],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        order = manager.get_build_order()

        # All modules should be in order
        assert len(order) == 3
        assert set(order) == {"auth", "api", "database"}

    def test_build_order_with_deps(self, tmp_path: Path) -> None:
        """Test get_build_order respects dependencies."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [
                {"name": "database", "dependencies": []},
                {"name": "auth", "dependencies": ["database"]},
                {"name": "api", "dependencies": ["auth", "database"]}
            ],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        order = manager.get_build_order()

        # database should come before auth, auth before api
        assert order.index("database") < order.index("auth")
        assert order.index("auth") < order.index("api")


class TestBuildProject:
    """Tests for IntegrationManager.build_project()."""

    def test_build_creates_integration_dir(self, tmp_path: Path) -> None:
        """Test build_project creates integration directory."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        manager.build_project()

        assert (tmp_path / "integration").exists()

    def test_build_generates_interfaces(self, tmp_path: Path) -> None:
        """Test build_project generates interfaces.py."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [
                {
                    "name": "auth",
                    "dependencies": [],
                    "exports": ["AuthService", "User"]
                }
            ],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        manager.build_project()

        interfaces_file = tmp_path / "integration" / "interfaces.py"
        assert interfaces_file.exists()

        content = interfaces_file.read_text()
        assert "AuthService" in content
        assert "User" in content
        assert "Protocol" in content

    def test_build_generates_connectors(self, tmp_path: Path) -> None:
        """Test build_project generates connectors."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [
                {
                    "name": "auth",
                    "dependencies": [],
                    "exports": ["AuthService"]
                },
                {
                    "name": "api",
                    "dependencies": ["auth"],
                    "exports": ["APIHandler"]
                }
            ],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        manager.build_project()

        connectors_dir = tmp_path / "integration" / "connectors"
        assert connectors_dir.exists()
        assert (connectors_dir / "__init__.py").exists()

        # Should have connector for api module
        connector_files = list(connectors_dir.glob("*_connector.py"))
        assert len(connector_files) > 0

    def test_build_fails_on_missing_dependency(self, tmp_path: Path) -> None:
        """Test build_project fails when dependency is missing."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager
        from vibecraft.core.exceptions import MissingDependencyError

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [
                {"name": "api", "dependencies": ["nonexistent"]}
            ],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)

        with pytest.raises(MissingDependencyError):
            manager.build_project()

    def test_build_fails_on_circular_dependency(self, tmp_path: Path) -> None:
        """Test build_project fails when circular dependency exists."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager
        from vibecraft.core.exceptions import CyclicDependencyError

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [
                {"name": "a", "dependencies": ["b"]},
                {"name": "b", "dependencies": ["a"]}
            ],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)

        with pytest.raises(CyclicDependencyError):
            manager.build_project()


class TestGenerateInterfaces:
    """Tests for IntegrationManager.generate_interfaces()."""

    def test_generate_interfaces_empty(self, tmp_path: Path) -> None:
        """Test generate_interfaces with empty registry."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        manager.generate_interfaces()

        interfaces_file = tmp_path / "integration" / "interfaces.py"
        assert interfaces_file.exists()

        content = interfaces_file.read_text()
        assert "Protocol" in content

    def test_generate_interfaces_multiple_modules(self, tmp_path: Path) -> None:
        """Test generate_interfaces with multiple modules."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [
                {"name": "auth", "exports": ["AuthService"]},
                {"name": "api", "exports": ["APIHandler", "Request"]},
                {"name": "database", "exports": ["Repository"]}
            ],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        manager.generate_interfaces()

        content = (tmp_path / "integration" / "interfaces.py").read_text()

        assert "AuthService" in content
        assert "APIHandler" in content
        assert "Request" in content
        assert "Repository" in content


class TestGenerateConnectors:
    """Tests for IntegrationManager.generate_connectors()."""

    def test_generate_connectors_empty(self, tmp_path: Path) -> None:
        """Test generate_connectors with empty registry."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        manager.generate_connectors()

        connectors_dir = tmp_path / "integration" / "connectors"
        assert connectors_dir.exists()
        assert (connectors_dir / "__init__.py").exists()

    def test_generate_connectors_with_deps(self, tmp_path: Path) -> None:
        """Test generate_connectors creates files for modules with deps."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text(json.dumps({
            "modules": [
                {"name": "api", "dependencies": ["auth"], "exports": ["handle_request"]}
            ],
            "dependencies": {},
            "build_order": []
        }))

        manager = IntegrationManager(tmp_path)
        manager.generate_connectors()

        connectors_dir = tmp_path / "integration" / "connectors"
        connector_file = connectors_dir / "api_connector.py"

        assert connector_file.exists()
        content = connector_file.read_text()
        assert "auth" in content
        assert "handle_request" in content


class TestIntegrationManagerEdgeCases:
    """Tests for IntegrationManager edge cases."""

    def test_no_registry_file(self, tmp_path: Path) -> None:
        """Test operations when registry file doesn't exist."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        manager = IntegrationManager(tmp_path)

        # Should not raise, should return empty/error-free results
        errors = manager.analyze_dependencies()
        assert errors == []

        order = manager.get_build_order()
        assert order == []

    def test_malformed_registry(self, tmp_path: Path) -> None:
        """Test handling of malformed registry JSON."""
        from vibecraft.modes.modular.integration_manager import IntegrationManager

        vibecraft_dir = tmp_path / ".vibecraft"
        vibecraft_dir.mkdir()
        registry_path = vibecraft_dir / "modules-registry.json"
        registry_path.write_text("not valid json")

        manager = IntegrationManager(tmp_path)

        # Should handle gracefully
        errors = manager.analyze_dependencies()
        assert errors == []
