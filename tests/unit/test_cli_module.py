"""
Tests for Vibecraft CLI 'module' commands.

Tests verify the module commands invoke correct underlying functionality.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner
from vibecraft.cli import main


class TestCliModule:
    """Tests for 'vibecraft module' commands."""

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
        (vibecraft_dir / "manifest.json").write_text(json.dumps({
            "project_name": "Test",
            "current_phase": "research",
            "phases": ["research"],
            "phases_completed": [],
            "agents": [],
            "stack": {},
        }))

        original_cwd = Path.cwd()
        import os
        os.chdir(project)

        yield project
        os.chdir(original_cwd)

    def test_module_create_calls_manager(
        self, runner: CliRunner, mock_project: Path
    ):
        """module create calls ModuleManager.create_module()."""
        # Arrange
        with patch("vibecraft.cli.ModuleManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            # Act
            result = runner.invoke(
                main,
                ["module", "create", "auth", "-d", "Auth module", "--depends-on", "db"],
            )

            # Assert
            assert result.exit_code == 0
            mock_manager.create_module.assert_called_once_with(
                "auth", "Auth module", ["db"]
            )

    def test_module_list_calls_manager(
        self, runner: CliRunner, mock_project: Path
    ):
        """module list calls ModuleManager.list_modules()."""
        # Arrange
        with patch("vibecraft.cli.ModuleManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.list_modules.return_value = [
                {"name": "auth", "description": "Auth", "status": "planned"}
            ]

            # Act
            result = runner.invoke(main, ["module", "list"])

            # Assert
            assert result.exit_code == 0
            mock_manager.list_modules.assert_called_once()

    def test_module_init_calls_manager(
        self, runner: CliRunner, mock_project: Path
    ):
        """module init calls ModuleManager.init_module()."""
        # Arrange
        with patch("vibecraft.cli.ModuleManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            # Act
            result = runner.invoke(main, ["module", "init", "auth"])

            # Assert
            assert result.exit_code == 0
            mock_manager.init_module.assert_called_once_with("auth")

    def test_module_status_calls_manager(
        self, runner: CliRunner, mock_project: Path
    ):
        """module status calls ModuleManager.get_status()."""
        # Arrange
        with patch("vibecraft.cli.ModuleManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.get_status.return_value = {
                "name": "auth",
                "status": "in_progress",
            }

            # Act
            result = runner.invoke(main, ["module", "status", "auth"])

            # Assert
            assert result.exit_code == 0
            mock_manager.get_status.assert_called_once_with("auth")

    def test_module_create_requires_name(
        self, runner: CliRunner, mock_project: Path
    ):
        """module create requires module name argument."""
        # Arrange
        with patch("vibecraft.cli.ModuleManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            # Act - no name provided
            result = runner.invoke(main, ["module", "create"])

            # Assert - should show error about missing name
            assert result.exit_code != 0 or "Missing argument" in result.output

    def test_module_init_requires_name(
        self, runner: CliRunner, mock_project: Path
    ):
        """module init requires module name argument."""
        # Act - no name provided
        result = runner.invoke(main, ["module", "init"])

        # Assert - should show error about missing name
        assert result.exit_code != 0 or "Missing argument" in result.output

    def test_module_status_requires_name(
        self, runner: CliRunner, mock_project: Path
    ):
        """module status requires module name argument."""
        # Act - no name provided
        result = runner.invoke(main, ["module", "status"])

        # Assert - should show error about missing name
        assert result.exit_code != 0 or "Missing argument" in result.output

    def test_module_errors_when_not_in_project(
        self, runner: CliRunner, tmp_path: Path
    ):
        """module commands show error when not inside project."""
        # Act
        result = runner.invoke(main, ["module", "list"])

        # Assert
        assert "Not inside a Vibecraft project" in result.output
