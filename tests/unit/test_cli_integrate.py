"""
Tests for Vibecraft CLI 'integrate' commands.

Tests verify the integrate commands invoke correct underlying functionality.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner
from vibecraft.cli import main


class TestCliIntegrate:
    """Tests for 'vibecraft integrate' commands."""

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

    def test_integrate_analyze_calls_analyzer(
        self, runner: CliRunner, mock_project: Path
    ):
        """integrate analyze calls DependencyAnalyzer.validate_dependencies()."""
        # Arrange
        with patch("vibecraft.cli.DependencyAnalyzer") as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer_class.return_value = mock_analyzer

            with patch("vibecraft.cli.ModuleRegistry"):
                # Act
                result = runner.invoke(main, ["integrate", "analyze"])

                # Assert
                assert result.exit_code == 0
                mock_analyzer.validate_dependencies.assert_called_once()

    def test_integrate_build_calls_manager(
        self, runner: CliRunner, mock_project: Path
    ):
        """integrate build calls IntegrationManager.build_project()."""
        # Arrange
        with patch("vibecraft.modes.modular.integration_manager.IntegrationManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.analyze_dependencies.return_value = []

            # Act
            result = runner.invoke(main, ["integrate", "build"])

            # Assert
            assert result.exit_code == 0
            mock_manager.build_project.assert_called_once()

    def test_integrate_analyze_shows_error_on_missing_deps(
        self, runner: CliRunner, mock_project: Path
    ):
        """integrate analyze shows error when dependencies missing."""
        # Arrange
        from vibecraft.core.exceptions import MissingDependencyError

        with patch("vibecraft.cli.DependencyAnalyzer") as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer.validate_dependencies.side_effect = MissingDependencyError("Missing: auth")
            mock_analyzer_class.return_value = mock_analyzer

            with patch("vibecraft.cli.ModuleRegistry"):
                # Act
                result = runner.invoke(main, ["integrate", "analyze"])

                # Assert
                assert result.exit_code == 0
                assert "Dependency error" in result.output or "Missing" in result.output

    def test_integrate_analyze_shows_error_on_cyclic_deps(
        self, runner: CliRunner, mock_project: Path
    ):
        """integrate analyze shows error when circular dependencies detected."""
        # Arrange
        from vibecraft.core.exceptions import CyclicDependencyError

        with patch("vibecraft.cli.DependencyAnalyzer") as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer.validate_dependencies.side_effect = CyclicDependencyError("Circular dependency")
            mock_analyzer_class.return_value = mock_analyzer

            with patch("vibecraft.cli.ModuleRegistry"):
                # Act
                result = runner.invoke(main, ["integrate", "analyze"])

                # Assert
                assert result.exit_code == 0
                assert "Dependency error" in result.output or "Circular" in result.output

    def test_integrate_build_shows_error_on_missing_deps(
        self, runner: CliRunner, mock_project: Path
    ):
        """integrate build shows error when dependencies missing."""
        # Arrange
        from vibecraft.core.exceptions import MissingDependencyError

        with patch("vibecraft.modes.modular.integration_manager.IntegrationManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.build_project.side_effect = MissingDependencyError("Missing: db")

            # Act
            result = runner.invoke(main, ["integrate", "build"])

            # Assert - CLI exits with error code on exception
            assert result.exit_code == 1
            assert "error" in result.output.lower() or "Missing" in result.output

    def test_integrate_build_shows_error_on_cyclic_deps(
        self, runner: CliRunner, mock_project: Path
    ):
        """integrate build shows error when circular dependencies detected."""
        # Arrange
        from vibecraft.core.exceptions import CyclicDependencyError

        with patch("vibecraft.modes.modular.integration_manager.IntegrationManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.build_project.side_effect = CyclicDependencyError("Cycle detected")

            # Act
            result = runner.invoke(main, ["integrate", "build"])

            # Assert - CLI exits with error code on exception
            assert result.exit_code == 1
            assert "error" in result.output.lower() or "Circular" in result.output or "Cycle" in result.output

    def test_integrate_requires_subcommand(
        self, runner: CliRunner, mock_project: Path
    ):
        """integrate command requires subcommand (analyze or build)."""
        # Act - no subcommand
        result = runner.invoke(main, ["integrate"])

        # Assert - should show usage or error
        assert result.exit_code != 0 or "Usage:" in result.output

    def test_integrate_errors_when_not_in_project(
        self, runner: CliRunner, tmp_path: Path
    ):
        """integrate commands show error when not inside project."""
        # Act
        result = runner.invoke(main, ["integrate", "analyze"])

        # Assert
        assert "Not inside a Vibecraft project" in result.output

    def test_integrate_analyze_shows_valid_deps_message(
        self, runner: CliRunner, mock_project: Path
    ):
        """integrate analyze shows success message when all deps valid."""
        # Arrange
        with patch("vibecraft.cli.DependencyAnalyzer") as mock_analyzer_class:
            mock_analyzer = MagicMock()
            mock_analyzer.get_build_order.return_value = ["db", "auth", "api"]
            mock_analyzer_class.return_value = mock_analyzer

            with patch("vibecraft.cli.ModuleRegistry"):
                # Act
                result = runner.invoke(main, ["integrate", "analyze"])

                # Assert
                assert result.exit_code == 0
                # Should show build order or success message
                assert "db" in result.output or "auth" in result.output or "valid" in result.output.lower()
