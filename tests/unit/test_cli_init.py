"""
Tests for Vibecraft CLI 'init' command.

Tests verify the init command invokes correct underlying functionality.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner
from vibecraft.cli import main


class TestCliInit:
    """Tests for 'vibecraft init' command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def input_files(self, tmp_path: Path) -> tuple[Path, Path]:
        """Create research.md and stack.md test files."""
        research = tmp_path / "research.md"
        research.write_text("# Test Project\n\nResearch content here.")

        stack = tmp_path / "stack.md"
        stack.write_text("# Stack\n\nPython, FastAPI")

        return research, stack

    def test_init_calls_bootstrapper_factory_with_simple_mode(
        self, runner: CliRunner, input_files: tuple[Path, Path], tmp_path: Path
    ):
        """init command calls BootstrapperFactory.create() with correct args."""
        # Arrange
        research, stack = input_files
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("vibecraft.cli.BootstrapperFactory") as mock_factory:
            mock_bootstrapper = MagicMock()
            mock_factory.create.return_value = mock_bootstrapper

            # Act
            result = runner.invoke(
                main,
                ["init", "-r", str(research), "-s", str(stack), "-o", str(output_dir)],
            )

            # Assert
            assert result.exit_code == 0
            mock_factory.create.assert_called_once()
            call_kwargs = mock_factory.create.call_args[1]
            assert call_kwargs["mode"] == "simple"
            assert call_kwargs["project_root"] == output_dir
            mock_bootstrapper.run.assert_called_once()

    def test_init_calls_bootstrapper_factory_with_modular_mode(
        self, runner: CliRunner, input_files: tuple[Path, Path], tmp_path: Path
    ):
        """init command passes mode='modular' to factory."""
        # Arrange
        research, stack = input_files
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("vibecraft.cli.BootstrapperFactory") as mock_factory:
            mock_bootstrapper = MagicMock()
            mock_factory.create.return_value = mock_bootstrapper

            # Act
            result = runner.invoke(
                main,
                ["init", "-r", str(research), "-s", str(stack), "-m", "modular"],
            )

            # Assert
            assert result.exit_code == 0
            call_kwargs = mock_factory.create.call_args[1]
            assert call_kwargs["mode"] == "modular"

    def test_init_passes_force_flag(
        self, runner: CliRunner, input_files: tuple[Path, Path], tmp_path: Path
    ):
        """init command passes force=True when --force flag provided."""
        # Arrange
        research, stack = input_files

        with patch("vibecraft.cli.BootstrapperFactory") as mock_factory:
            mock_bootstrapper = MagicMock()
            mock_factory.create.return_value = mock_bootstrapper

            # Act
            result = runner.invoke(
                main,
                ["init", "-r", str(research), "-s", str(stack), "--force"],
            )

            # Assert
            assert result.exit_code == 0
            call_kwargs = mock_factory.create.call_args[1]
            assert call_kwargs["force"] is True

    def test_init_passes_custom_agents_path(
        self, runner: CliRunner, input_files: tuple[Path, Path], tmp_path: Path
    ):
        """init command passes custom_agents_path when --agents provided."""
        # Arrange
        research, stack = input_files
        agents_file = tmp_path / "agents.yaml"
        agents_file.write_text("- name: custom")

        with patch("vibecraft.cli.BootstrapperFactory") as mock_factory:
            mock_bootstrapper = MagicMock()
            mock_factory.create.return_value = mock_bootstrapper

            # Act
            result = runner.invoke(
                main,
                ["init", "-r", str(research), "-s", str(stack), "-a", str(agents_file)],
            )

            # Assert
            assert result.exit_code == 0
            call_kwargs = mock_factory.create.call_args[1]
            assert call_kwargs["custom_agents_path"] == agents_file

    def test_init_requires_research_file(
        self, runner: CliRunner, tmp_path: Path
    ):
        """init command requires research.md file."""
        # Arrange
        stack = tmp_path / "stack.md"
        stack.write_text("# Stack")

        # Act
        result = runner.invoke(
            main,
            ["init", "-s", str(stack)],
        )

        # Assert - should show error about missing research file
        assert result.exit_code != 0 or "research" in result.output.lower()

    def test_init_requires_stack_file(
        self, runner: CliRunner, tmp_path: Path
    ):
        """init command requires stack.md file."""
        # Arrange
        research = tmp_path / "research.md"
        research.write_text("# Research")

        # Act
        result = runner.invoke(
            main,
            ["init", "-r", str(research)],
        )

        # Assert - should show error about missing stack file
        assert result.exit_code != 0 or "stack" in result.output.lower()
