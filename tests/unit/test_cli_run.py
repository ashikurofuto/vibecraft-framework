"""
Tests for Vibecraft CLI 'run' command.

Tests verify the run command invokes correct underlying functionality.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner
from vibecraft.cli import main


class TestCliRun:
    """Tests for 'vibecraft run' command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_project(self, tmp_path: Path) -> Path:
        """Create mock Vibecraft project structure."""
        project = tmp_path / "test-project"
        project.mkdir()

        vibecraft_dir = project / ".vibecraft"
        vibecraft_dir.mkdir()

        manifest = vibecraft_dir / "manifest.json"
        manifest.write_text(json.dumps({
            "mode": "simple",
            "project_name": "Test",
            "current_phase": "research",
        }))

        original_cwd = Path.cwd()
        import os
        os.chdir(project)

        yield project

        os.chdir(original_cwd)

    def test_run_calls_skill_runner_for_simple_mode(
        self, runner: CliRunner, mock_project: Path
    ):
        """run command calls SkillRunner.run() for simple mode."""
        # Arrange
        with patch("vibecraft.cli.SkillRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner_class.return_value = mock_runner

            # Act
            result = runner.invoke(main, ["run", "research"])

            # Assert
            assert result.exit_code == 0
            mock_runner_class.assert_called_once()
            mock_runner.run.assert_called_once_with("research", phase=None)

    def test_run_calls_modular_runner_when_module_specified(
        self, runner: CliRunner, mock_project: Path
    ):
        """run command calls ModularRunner when --module provided."""
        # Arrange
        with patch("vibecraft.modes.modular.runner.ModularRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner_class.return_value = mock_runner

            # Act
            result = runner.invoke(main, ["run", "implement", "--module", "auth"])

            # Assert
            assert result.exit_code == 0
            mock_runner_class.assert_called_once()
            mock_runner.run.assert_called_once_with("implement", module="auth", phase=None)

    def test_run_passes_phase_option(
        self, runner: CliRunner, mock_project: Path
    ):
        """run command passes phase option to runner."""
        # Arrange
        with patch("vibecraft.cli.SkillRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner_class.return_value = mock_runner

            # Act
            result = runner.invoke(main, ["run", "implement", "--phase", "1"])

            # Assert
            assert result.exit_code == 0
            mock_runner.run.assert_called_once_with("implement", phase=1)

    def test_run_errors_when_not_in_project(
        self, runner: CliRunner, tmp_path: Path
    ):
        """run command shows error when not inside Vibecraft project."""
        # Arrange - no .vibecraft directory
        # Act
        result = runner.invoke(main, ["run", "research"])

        # Assert
        assert result.exit_code == 0  # Command completes, but shows error message
        assert "Not inside a Vibecraft project" in result.output

    def test_run_requires_skill_name(
        self, runner: CliRunner, mock_project: Path
    ):
        """run command requires skill name argument."""
        # Act - no skill name provided
        result = runner.invoke(main, ["run"])

        # Assert - should show error about missing skill
        assert result.exit_code != 0 or "Missing argument" in result.output

    def test_run_with_multiple_phase_numbers(
        self, runner: CliRunner, mock_project: Path
    ):
        """run command handles different phase numbers."""
        # Arrange
        with patch("vibecraft.cli.SkillRunner") as mock_runner_class:
            mock_runner = MagicMock()
            mock_runner_class.return_value = mock_runner

            # Act
            result = runner.invoke(main, ["run", "implement", "--phase", "3"])

            # Assert
            assert result.exit_code == 0
            mock_runner.run.assert_called_once_with("implement", phase=3)
