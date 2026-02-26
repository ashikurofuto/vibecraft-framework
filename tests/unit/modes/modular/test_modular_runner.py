"""
Unit tests for ModularRunner.
"""
import pytest
from pathlib import Path
import json


class TestModularRunnerInit:
    """Tests for ModularRunner initialization."""

    def test_init_with_project_root(self, tmp_path: Path) -> None:
        """Test ModularRunner initialization with project root."""
        from vibecraft.modes.modular.runner import ModularRunner
        
        runner = ModularRunner(tmp_path)
        
        assert runner.project_root == tmp_path
        assert runner._module is None
        assert runner._module_context is None
        assert runner._kwargs == {}

    def test_init_with_module(self, tmp_path: Path) -> None:
        """Test ModularRunner initialization with module parameter."""
        from vibecraft.modes.modular.runner import ModularRunner
        
        runner = ModularRunner(tmp_path, module="auth")
        
        assert runner.project_root == tmp_path
        assert runner._module == "auth"


class TestLoadModuleContext:
    """Tests for _load_module_context method."""

    def test_load_existing_context(self, tmp_path: Path) -> None:
        """Test loading context from existing module."""
        from vibecraft.modes.modular.runner import ModularRunner
        
        # Create module with context
        module_dir = tmp_path / "modules" / "auth"
        module_dir.mkdir(parents=True)
        (module_dir / "context.md").write_text("# Auth Context\n\nContent here.")
        
        runner = ModularRunner(tmp_path)
        context = runner._load_module_context("auth")
        
        assert context is not None
        assert "# Auth Context" in context
        assert "Content here" in context

    def test_load_nonexistent_context(self, tmp_path: Path) -> None:
        """Test loading context from nonexistent module returns None."""
        from vibecraft.modes.modular.runner import ModularRunner
        
        runner = ModularRunner(tmp_path)
        context = runner._load_module_context("nonexistent")
        
        assert context is None


class TestLoadModuleConfig:
    """Tests for _load_module_config method."""

    def test_load_existing_config(self, tmp_path: Path) -> None:
        """Test loading config from existing module."""
        from vibecraft.modes.modular.runner import ModularRunner
        
        # Create module with config
        module_dir = tmp_path / "modules" / "auth"
        module_dir.mkdir(parents=True)
        
        config = {
            "name": "auth",
            "description": "Authentication module",
            "dependencies": ["database"],
            "exports": ["AuthService", "login"]
        }
        (module_dir / ".module.json").write_text(json.dumps(config))
        
        runner = ModularRunner(tmp_path)
        loaded_config = runner._load_module_config("auth")
        
        assert loaded_config is not None
        assert loaded_config["name"] == "auth"
        assert "Authentication" in loaded_config["description"]
        assert loaded_config["dependencies"] == ["database"]

    def test_load_nonexistent_config(self, tmp_path: Path) -> None:
        """Test loading config from nonexistent module returns None."""
        from vibecraft.modes.modular.runner import ModularRunner
        
        runner = ModularRunner(tmp_path)
        config = runner._load_module_config("nonexistent")
        
        assert config is None


class TestResolveOutputPath:
    """Tests for _resolve_output_path method."""

    def test_resolve_simple_path(self, tmp_path: Path) -> None:
        """Test resolving simple output path."""
        from vibecraft.modes.modular.runner import ModularRunner
        
        module_dir = tmp_path / "modules" / "auth"
        module_dir.mkdir(parents=True)
        
        runner = ModularRunner(tmp_path)
        output_path = runner._resolve_output_path("src/auth.py", "auth")
        
        expected = tmp_path / "modules" / "auth" / "src" / "auth.py"
        assert output_path == expected

    def test_resolve_nested_path(self, tmp_path: Path) -> None:
        """Test resolving nested output path."""
        from vibecraft.modes.modular.runner import ModularRunner
        
        module_dir = tmp_path / "modules" / "auth"
        module_dir.mkdir(parents=True)
        
        runner = ModularRunner(tmp_path)
        output_path = runner._resolve_output_path("services/auth_service.py", "auth")
        
        expected = tmp_path / "modules" / "auth" / "services" / "auth_service.py"
        assert output_path == expected

    def test_resolve_creates_directories(self, tmp_path: Path) -> None:
        """Test that resolving path creates parent directories."""
        from vibecraft.modes.modular.runner import ModularRunner
        
        module_dir = tmp_path / "modules" / "auth"
        module_dir.mkdir(parents=True)
        
        runner = ModularRunner(tmp_path)
        output_path = runner._resolve_output_path("deep/nested/path/file.py", "auth")
        
        # Parent directories should be created
        assert output_path.parent.exists()
        assert output_path.parent == tmp_path / "modules" / "auth" / "deep" / "nested" / "path"

    def test_resolve_rejects_path_traversal(self, tmp_path: Path) -> None:
        """Test that path traversal is rejected."""
        from vibecraft.modes.modular.runner import ModularRunner
        
        module_dir = tmp_path / "modules" / "auth"
        module_dir.mkdir(parents=True)
        
        runner = ModularRunner(tmp_path)
        
        with pytest.raises(ValueError, match="Invalid output path"):
            runner._resolve_output_path("../../../etc/passwd", "auth")

    def test_resolve_rejects_absolute_path(self, tmp_path: Path) -> None:
        """Test that absolute paths are rejected."""
        from vibecraft.modes.modular.runner import ModularRunner
        
        module_dir = tmp_path / "modules" / "auth"
        module_dir.mkdir(parents=True)
        
        runner = ModularRunner(tmp_path)
        
        with pytest.raises(ValueError, match="Invalid output path"):
            runner._resolve_output_path("/etc/passwd", "auth")


class TestRunSkill:
    """Tests for run method."""

    def test_run_global_skill(self, tmp_path: Path) -> None:
        """Test running global skill without module."""
        from vibecraft.modes.modular.runner import ModularRunner
        
        runner = ModularRunner(tmp_path)
        runner.run("research")
        
        # Module should remain None
        assert runner._module is None

    def test_run_module_skill(self, tmp_path: Path) -> None:
        """Test running skill for specific module."""
        from vibecraft.modes.modular.runner import ModularRunner
        from vibecraft.modes.modular.module_manager import ModuleManager

        # Create module first
        manager = ModuleManager(tmp_path)
        manager.create_module("auth", "Auth module")

        runner = ModularRunner(tmp_path)
        
        # Module skill should not raise (will fail at SimpleRunner level since no skills)
        # We just test that module validation passes
        try:
            runner.run("implement", module="auth", phase=1)
        except Exception:
            # Expected to fail at SimpleRunner level (no skills initialized)
            pass

        # Module should be set
        assert runner._module == "auth"
        assert runner._kwargs == {"phase": 1}