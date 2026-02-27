"""
Tests for Vibecraft CLI 'status' and 'context' commands.

Tests verify these commands invoke correct underlying functionality.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner
from vibecraft.cli import main


class TestCliStatus:
    """Tests for 'vibecraft status' command."""

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
            "project_type": ["api"],
            "current_phase": "research",
            "phases": ["research", "design"],
            "phases_completed": [],
            "updated_at": "2026-02-27T10:00:00Z",
            "agents": ["researcher"],
            "stack": {"lang": "Python"},
        }))

        original_cwd = Path.cwd()
        import os
        os.chdir(project)

        yield project
        os.chdir(original_cwd)

    def test_status_calls_context_manager_print_status(
        self, runner: CliRunner, mock_project: Path
    ):
        """status command calls ContextManager.print_status()."""
        # Arrange
        with patch("vibecraft.cli.ContextManager") as mock_cm_class:
            mock_cm = MagicMock()
            mock_cm_class.return_value = mock_cm

            # Act
            result = runner.invoke(main, ["status"])

            # Assert
            assert result.exit_code == 0
            mock_cm_class.assert_called_once()
            mock_cm.print_status.assert_called_once()

    def test_status_errors_when_not_in_project(
        self, runner: CliRunner, tmp_path: Path
    ):
        """status command shows error when not inside project."""
        # Act
        result = runner.invoke(main, ["status"])

        # Assert
        assert "Not inside a Vibecraft project" in result.output


class TestCliContext:
    """Tests for 'vibecraft context' command."""

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

    def test_context_calls_build_and_copy_with_no_args(
        self, runner: CliRunner, mock_project: Path
    ):
        """context command calls ContextManager.build_and_copy() without args."""
        # Arrange
        with patch("vibecraft.cli.ContextManager") as mock_cm_class:
            mock_cm = MagicMock()
            mock_cm_class.return_value = mock_cm

            # Act
            result = runner.invoke(main, ["context"])

            # Assert
            assert result.exit_code == 0
            mock_cm.build_and_copy.assert_called_once_with(skill=None, phase=None)

    def test_context_passes_skill_option(
        self, runner: CliRunner, mock_project: Path
    ):
        """context command passes --skill to build_and_copy()."""
        # Arrange
        with patch("vibecraft.cli.ContextManager") as mock_cm_class:
            mock_cm = MagicMock()
            mock_cm_class.return_value = mock_cm

            # Act
            result = runner.invoke(main, ["context", "--skill", "research"])

            # Assert
            assert result.exit_code == 0
            mock_cm.build_and_copy.assert_called_once_with(skill="research", phase=None)

    def test_context_passes_phase_option(
        self, runner: CliRunner, mock_project: Path
    ):
        """context command passes --phase to build_and_copy()."""
        # Arrange
        with patch("vibecraft.cli.ContextManager") as mock_cm_class:
            mock_cm = MagicMock()
            mock_cm_class.return_value = mock_cm

            # Act
            result = runner.invoke(main, ["context", "--phase", "1"])

            # Assert
            assert result.exit_code == 0
            mock_cm.build_and_copy.assert_called_once_with(skill=None, phase=1)

    def test_context_errors_when_not_in_project(
        self, runner: CliRunner, tmp_path: Path
    ):
        """context command shows error when not inside project."""
        # Act
        result = runner.invoke(main, ["context"])

        # Assert
        assert "Not inside a Vibecraft project" in result.output
