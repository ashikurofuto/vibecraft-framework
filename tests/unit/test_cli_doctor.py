"""
Tests for Vibecraft CLI 'doctor', 'rollback', 'snapshots' commands.

Tests verify these commands invoke correct underlying functionality.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner
from vibecraft.cli import main


class TestCliDoctor:
    """Tests for 'vibecraft doctor' command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click CLI test runner."""
        return CliRunner()

    def test_doctor_calls_run_doctor(
        self, runner: CliRunner, tmp_path: Path
    ):
        """doctor command calls run_doctor() with project root."""
        # Arrange
        with patch("vibecraft.cli.run_doctor") as mock_doctor:
            # Act
            result = runner.invoke(main, ["doctor"])

            # Assert
            assert result.exit_code == 0
            mock_doctor.assert_called_once()


class TestCliRollback:
    """Tests for 'vibecraft rollback' command."""

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

    def test_rollback_calls_rollback_with_no_target(
        self, runner: CliRunner, mock_project: Path
    ):
        """rollback command calls RollbackManager.rollback(None) when no target."""
        # Arrange
        with patch("vibecraft.cli.RollbackManager") as mock_rm_class:
            mock_rm = MagicMock()
            mock_rm_class.return_value = mock_rm

            # Act
            result = runner.invoke(main, ["rollback"])

            # Assert
            assert result.exit_code == 0
            mock_rm.rollback.assert_called_once_with(None)

    def test_rollback_calls_rollback_with_target(
        self, runner: CliRunner, mock_project: Path
    ):
        """rollback command passes target to RollbackManager.rollback()."""
        # Arrange
        with patch("vibecraft.cli.RollbackManager") as mock_rm_class:
            mock_rm = MagicMock()
            mock_rm_class.return_value = mock_rm

            # Act
            result = runner.invoke(main, ["rollback", "design"])

            # Assert
            assert result.exit_code == 0
            mock_rm.rollback.assert_called_once_with("design")

    def test_rollback_errors_when_not_in_project(
        self, runner: CliRunner, tmp_path: Path
    ):
        """rollback command shows error when not inside project."""
        # Act
        result = runner.invoke(main, ["rollback"])

        # Assert
        assert "Not inside a Vibecraft project" in result.output


class TestCliSnapshots:
    """Tests for 'vibecraft snapshots' command."""

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

    def test_snapshots_calls_print_snapshots(
        self, runner: CliRunner, mock_project: Path
    ):
        """snapshots command calls RollbackManager.print_snapshots()."""
        # Arrange
        with patch("vibecraft.cli.RollbackManager") as mock_rm_class:
            mock_rm = MagicMock()
            mock_rm_class.return_value = mock_rm

            # Act
            result = runner.invoke(main, ["snapshots"])

            # Assert
            assert result.exit_code == 0
            mock_rm.print_snapshots.assert_called_once()

    def test_snapshots_errors_when_not_in_project(
        self, runner: CliRunner, tmp_path: Path
    ):
        """snapshots command shows error when not inside project."""
        # Act
        result = runner.invoke(main, ["snapshots"])

        # Assert
        assert "Not inside a Vibecraft project" in result.output
