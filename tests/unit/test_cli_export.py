"""
Tests for Vibecraft CLI 'export' command.

Tests verify the export command invokes correct underlying functionality.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner
from vibecraft.cli import main


class TestCliExport:
    """Tests for 'vibecraft export' command."""

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

    def test_export_calls_export_markdown_by_default(
        self, runner: CliRunner, mock_project: Path
    ):
        """export command calls Exporter.export_markdown() by default."""
        # Arrange
        with patch("vibecraft.cli.Exporter") as mock_exporter_class:
            mock_exporter = MagicMock()
            mock_exporter_class.return_value = mock_exporter

            # Act
            result = runner.invoke(main, ["export"])

            # Assert
            assert result.exit_code == 0
            mock_exporter.export_markdown.assert_called_once()

    def test_export_calls_export_zip_with_format_zip(
        self, runner: CliRunner, mock_project: Path
    ):
        """export command calls Exporter.export_zip() with --format zip."""
        # Arrange
        with patch("vibecraft.cli.Exporter") as mock_exporter_class:
            mock_exporter = MagicMock()
            mock_exporter_class.return_value = mock_exporter

            # Act
            result = runner.invoke(main, ["export", "--format", "zip"])

            # Assert
            assert result.exit_code == 0
            mock_exporter.export_zip.assert_called_once()

    def test_export_errors_when_not_in_project(
        self, runner: CliRunner, tmp_path: Path
    ):
        """export command shows error when not inside project."""
        # Act
        result = runner.invoke(main, ["export"])

        # Assert
        assert "Not inside a Vibecraft project" in result.output

    def test_export_with_invalid_format(
        self, runner: CliRunner, mock_project: Path
    ):
        """export command handles invalid format option."""
        # Act
        result = runner.invoke(main, ["export", "--format", "invalid"])

        # Assert - should show error about invalid choice
        assert result.exit_code != 0 or "invalid" in result.output.lower()
