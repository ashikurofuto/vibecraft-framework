"""
Unit tests for ModuleContextManager.
"""
import pytest
from pathlib import Path
import json


class TestModuleContextManagerInit:
    """Tests for ModuleContextManager initialization."""

    def test_init_with_project_root(self, tmp_path: Path) -> None:
        """Test initialization with project root."""
        from vibecraft.modes.modular.context_manager import ModuleContextManager
        
        cm = ModuleContextManager(tmp_path)
        
        assert cm.project_root == tmp_path


class TestGetModuleDir:
    """Tests for _get_module_dir method."""

    def test_get_module_dir(self, tmp_path: Path) -> None:
        """Test getting module directory path."""
        from vibecraft.modes.modular.context_manager import ModuleContextManager
        
        cm = ModuleContextManager(tmp_path)
        module_dir = cm._get_module_dir("auth")
        
        expected = tmp_path / "modules" / "auth"
        assert module_dir == expected


class TestGetContextPath:
    """Tests for _get_context_path method."""

    def test_get_context_path(self, tmp_path: Path) -> None:
        """Test getting context.md path."""
        from vibecraft.modes.modular.context_manager import ModuleContextManager
        
        cm = ModuleContextManager(tmp_path)
        context_path = cm._get_context_path("auth")
        
        expected = tmp_path / "modules" / "auth" / "context.md"
        assert context_path == expected


class TestBuildContext:
    """Tests for build_context method."""

    def test_build_existing_context(self, tmp_path: Path) -> None:
        """Test building context from existing module."""
        from vibecraft.modes.modular.context_manager import ModuleContextManager
        
        # Create module with context
        module_dir = tmp_path / "modules" / "auth"
        module_dir.mkdir(parents=True)
        (module_dir / "context.md").write_text("# Auth Context\n\nContent.")
        
        cm = ModuleContextManager(tmp_path)
        context = cm.build_context("auth")
        
        assert "# Auth Context" in context
        assert "Content." in context

    def test_build_nonexistent_context(self, tmp_path: Path) -> None:
        """Test building context from nonexistent module returns empty string."""
        from vibecraft.modes.modular.context_manager import ModuleContextManager
        
        cm = ModuleContextManager(tmp_path)
        context = cm.build_context("nonexistent")
        
        assert context == ""


class TestUpdateContext:
    """Tests for update_context method."""

    def test_update_existing_context(self, tmp_path: Path) -> None:
        """Test updating existing module context."""
        from vibecraft.modes.modular.context_manager import ModuleContextManager
        
        # Create module with context
        module_dir = tmp_path / "modules" / "auth"
        module_dir.mkdir(parents=True)
        (module_dir / "context.md").write_text("# Old Context")
        
        cm = ModuleContextManager(tmp_path)
        cm.update_context("auth", "# New Context\n\nUpdated content.")
        
        context_file = module_dir / "context.md"
        content = context_file.read_text()
        
        assert "# New Context" in content
        assert "Updated content." in content

    def test_update_creates_module_dir(self, tmp_path: Path) -> None:
        """Test that update_context creates module directory."""
        from vibecraft.modes.modular.context_manager import ModuleContextManager
        
        cm = ModuleContextManager(tmp_path)
        cm.update_context("new_module", "# New Module Context")
        
        module_dir = tmp_path / "modules" / "new_module"
        assert module_dir.exists()
        
        context_file = module_dir / "context.md"
        assert context_file.exists()
        assert "# New Module Context" in context_file.read_text()

    def test_update_creates_context_file(self, tmp_path: Path) -> None:
        """Test that update_context creates context.md file."""
        from vibecraft.modes.modular.context_manager import ModuleContextManager
        
        # Create module without context
        module_dir = tmp_path / "modules" / "auth"
        module_dir.mkdir(parents=True)
        
        cm = ModuleContextManager(tmp_path)
        cm.update_context("auth", "# Context Content")
        
        context_file = module_dir / "context.md"
        assert context_file.exists()
        assert "# Context Content" in context_file.read_text()


class TestAppendToContext:
    """Tests for append_to_context method."""

    def test_append_to_existing_context(self, tmp_path: Path) -> None:
        """Test appending to existing context."""
        from vibecraft.modes.modular.context_manager import ModuleContextManager
        
        # Create module with context
        module_dir = tmp_path / "modules" / "auth"
        module_dir.mkdir(parents=True)
        (module_dir / "context.md").write_text("# Original Context")
        
        cm = ModuleContextManager(tmp_path)
        cm.append_to_context("auth", "## New Section\n\nAdded content.")
        
        context_file = module_dir / "context.md"
        content = context_file.read_text()
        
        assert "# Original Context" in content
        assert "## New Section" in content
        assert "Added content." in content

    def test_append_to_empty_context(self, tmp_path: Path) -> None:
        """Test appending to nonexistent context."""
        from vibecraft.modes.modular.context_manager import ModuleContextManager
        
        cm = ModuleContextManager(tmp_path)
        cm.append_to_context("auth", "# Appended Content")
        
        context_file = tmp_path / "modules" / "auth" / "context.md"
        content = context_file.read_text()
        
        assert "# Appended Content" in content


class TestGetModuleInfo:
    """Tests for get_module_info method."""

    def test_get_existing_info(self, tmp_path: Path) -> None:
        """Test getting info from existing module."""
        from vibecraft.modes.modular.context_manager import ModuleContextManager
        
        # Create module with config
        module_dir = tmp_path / "modules" / "auth"
        module_dir.mkdir(parents=True)
        
        config = {
            "name": "auth",
            "description": "Authentication module",
            "dependencies": ["database"]
        }
        (module_dir / ".module.json").write_text(json.dumps(config))
        
        cm = ModuleContextManager(tmp_path)
        info = cm.get_module_info("auth")
        
        assert info is not None
        assert info["name"] == "auth"
        assert "Authentication" in info["description"]

    def test_get_nonexistent_info(self, tmp_path: Path) -> None:
        """Test getting info from nonexistent module returns None."""
        from vibecraft.modes.modular.context_manager import ModuleContextManager
        
        cm = ModuleContextManager(tmp_path)
        info = cm.get_module_info("nonexistent")
        
        assert info is None