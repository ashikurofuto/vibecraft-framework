"""
Tests for Vibecraft CLI 'complete' and 'module init' commands.

Tests verify error paths and edge cases not covered in other test files.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner
from vibecraft.cli import main


class TestCliComplete:
    """Tests for 'vibecraft complete' command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_project(self, tmp_path: Path) -> Path:
        """Create mock Vibecraft project."""
        project = tmp_path / "test-project"
        project.mkdir()
        vibecraft_dir = project / ".vibecraft"
        vibecraft_dir.mkdir()

        manifest = vibecraft_dir / "manifest.json"
        manifest.write_text(json.dumps({
            "project_name": "Test Project",
            "current_phase": "research",
            "phases": ["research", "design"],
            "phases_completed": [],
        }))

        original_cwd = Path.cwd()
        import os
        os.chdir(project)

        yield project
        os.chdir(original_cwd)

    def test_complete_calls_context_manager_complete_phase(
        self, runner: CliRunner, mock_project: Path
    ):
        """complete command calls ContextManager.complete_phase()."""
        # Arrange
        with patch("vibecraft.cli.ContextManager") as mock_cm_class:
            mock_cm = MagicMock()
            mock_cm_class.return_value = mock_cm

            # Act
            result = runner.invoke(main, ["complete", "1"])

            # Assert
            assert result.exit_code == 0
            mock_cm_class.assert_called_once()
            mock_cm.complete_phase.assert_called_once_with(1)

    def test_complete_errors_when_not_in_project(
        self, runner: CliRunner, tmp_path: Path
    ):
        """complete command shows error when not inside project."""
        # Act
        result = runner.invoke(main, ["complete", "1"])

        # Assert
        assert "Not inside a Vibecraft project" in result.output

    def test_complete_requires_phase_argument(
        self, runner: CliRunner, mock_project: Path
    ):
        """complete command requires phase argument."""
        # Act - no phase provided
        result = runner.invoke(main, ["complete"])

        # Assert - should show error about missing argument
        assert result.exit_code != 0 or "Missing argument" in result.output


class TestCliModuleInit:
    """Tests for 'vibecraft module init' command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_project(self, tmp_path: Path) -> Path:
        """Create mock Vibecraft project with modules directory."""
        project = tmp_path / "test-project"
        project.mkdir()
        vibecraft_dir = project / ".vibecraft"
        vibecraft_dir.mkdir()
        modules_dir = project / "modules"
        modules_dir.mkdir()

        manifest = vibecraft_dir / "manifest.json"
        manifest.write_text(json.dumps({
            "project_name": "Test Project",
            "mode": "modular",
            "current_phase": "research",
            "phases": ["research"],
            "phases_completed": [],
        }))

        original_cwd = Path.cwd()
        import os
        os.chdir(project)

        yield project
        os.chdir(original_cwd)

    def test_module_init_calls_manager_init_module(
        self, runner: CliRunner, mock_project: Path
    ):
        """module init command calls ModuleManager.init_module()."""
        # Arrange
        with patch("vibecraft.cli.ModuleManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            # Act
            result = runner.invoke(main, ["module", "init", "auth"])

            # Assert
            assert result.exit_code == 0
            mock_manager_class.assert_called_once()
            mock_manager.init_module.assert_called_once_with("auth")

    def test_module_init_errors_when_not_in_project(
        self, runner: CliRunner, tmp_path: Path
    ):
        """module init command shows error when not inside project."""
        # Act
        result = runner.invoke(main, ["module", "init", "auth"])

        # Assert
        assert "Not inside a Vibecraft project" in result.output

    def test_module_init_requires_name(
        self, runner: CliRunner, mock_project: Path
    ):
        """module init command requires module name argument."""
        # Act - no name provided
        result = runner.invoke(main, ["module", "init"])

        # Assert - should show error about missing argument
        assert result.exit_code != 0 or "Missing argument" in result.output

    def test_module_init_handles_exception(
        self, runner: CliRunner, mock_project: Path
    ):
        """module init command handles exceptions from ModuleManager."""
        # Arrange
        with patch("vibecraft.cli.ModuleManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.init_module.side_effect = RuntimeError("Test error")
            mock_manager_class.return_value = mock_manager

            # Act
            result = runner.invoke(main, ["module", "init", "auth"])

            # Assert
            assert result.exit_code != 0
            assert "Test error" in result.output


class TestCliModuleStatus:
    """Tests for 'vibecraft module status' command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_project(self, tmp_path: Path) -> Path:
        """Create mock Vibecraft project."""
        project = tmp_path / "test-project"
        project.mkdir()
        vibecraft_dir = project / ".vibecraft"
        vibecraft_dir.mkdir()
        modules_dir = project / "modules"
        modules_dir.mkdir()

        manifest = vibecraft_dir / "manifest.json"
        manifest.write_text(json.dumps({
            "project_name": "Test Project",
            "mode": "modular",
            "current_phase": "research",
        }))

        original_cwd = Path.cwd()
        import os
        os.chdir(project)

        yield project
        os.chdir(original_cwd)

    def test_module_status_calls_manager_get_status(
        self, runner: CliRunner, mock_project: Path
    ):
        """module status command calls ModuleManager.get_status()."""
        # Arrange
        with patch("vibecraft.cli.ModuleManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.get_status.return_value = {
                "name": "auth",
                "description": "Authentication module",
                "status": "implemented",
                "dependencies": ["db"],
            }
            mock_manager_class.return_value = mock_manager

            # Act
            result = runner.invoke(main, ["module", "status", "auth"])

            # Assert
            assert result.exit_code == 0
            mock_manager.get_status.assert_called_once_with("auth")
            assert "auth" in result.output
            assert "Authentication module" in result.output

    def test_module_status_errors_when_not_in_project(
        self, runner: CliRunner, tmp_path: Path
    ):
        """module status command shows error when not inside project."""
        # Act
        result = runner.invoke(main, ["module", "status", "auth"])

        # Assert
        assert "Not inside a Vibecraft project" in result.output

    def test_module_status_requires_name(
        self, runner: CliRunner, mock_project: Path
    ):
        """module status command requires module name argument."""
        # Act - no name provided
        result = runner.invoke(main, ["module", "status"])

        # Assert - should show error about missing argument
        assert result.exit_code != 0 or "Missing argument" in result.output
