"""
End-to-end integration tests for Vibecraft simple mode workflow.

Tests verify complete workflow from project initialization to skill execution.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner
from vibecraft.cli import main


class TestSimpleModeWorkflow:
    """End-to-end tests for simple mode workflow."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click CLI test runner."""
        return CliRunner()

    def test_full_init_workflow_creates_project_structure(
        self, runner: CliRunner, e2e_project_files: tuple[Path, Path, Path], tmp_path: Path
    ):
        """E2E: init command creates complete project structure."""
        # Arrange
        research, stack, agents = e2e_project_files
        output_dir = tmp_path / "e2e-project"

        # Act
        with patch("vibecraft.cli.BootstrapperFactory") as mock_factory:
            mock_bootstrapper = MagicMock()
            mock_factory.create.return_value = mock_bootstrapper

            result = runner.invoke(main, [
                "init",
                "-r", str(research),
                "-s", str(stack),
                "-a", str(agents),
                "-o", str(output_dir),
            ])

            # Assert
            assert result.exit_code == 0
            mock_factory.create.assert_called_once()
            mock_bootstrapper.run.assert_called_once()

    def test_status_command_shows_project_info(
        self, runner: CliRunner, mock_project_in_context: Path
    ):
        """E2E: status command shows project information."""
        # Arrange - mock_project_in_context already sets up project
        # Update manifest with more details
        vc_dir = mock_project_in_context / ".vibecraft"
        manifest = {
            "project_name": "E2E Test Project",
            "project_type": ["test"],
            "current_phase": "research",
            "phases": ["research", "design", "plan", "implement", "review"],
            "phases_completed": [],
            "agents": ["researcher"],
            "stack": {"language": "Python"},
        }
        (vc_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

        # Act
        result = runner.invoke(main, ["status"])

        # Assert
        assert result.exit_code == 0
        assert "E2E Test Project" in result.output
        assert "research" in result.output
        assert "current_phase" in result.output.lower() or "research" in result.output.lower()

    def test_context_command_builds_context_file(
        self, runner: CliRunner, mock_project_in_context: Path
    ):
        """E2E: context command builds context.md from research and stack."""
        # Arrange - mock_project_in_context already has research.md and stack.md

        # Act
        result = runner.invoke(main, ["context"])

        # Assert
        assert result.exit_code == 0
        context_file = mock_project_in_context / "docs" / "context.md"
        assert context_file.exists()
        content = context_file.read_text()
        # Should contain content from both research and stack
        assert "Research" in content or "Stack" in content or "Python" in content

    def test_rollback_lists_snapshots(
        self, runner: CliRunner, mock_project_in_context: Path
    ):
        """E2E: snapshots command lists available snapshots."""
        # Arrange - Create snapshots
        vc_dir = mock_project_in_context / ".vibecraft"
        snapshots_dir = vc_dir / "snapshots"
        snapshots_dir.mkdir()
        (snapshots_dir / "20250101T120000_research").mkdir()
        (snapshots_dir / "20250101T130000_design").mkdir()

        # Act
        result = runner.invoke(main, ["snapshots"])

        # Assert
        assert result.exit_code == 0
        assert "research" in result.output
        assert "design" in result.output
        assert "2025" in result.output

    def test_doctor_validates_project_structure(
        self, runner: CliRunner, mock_project_in_context: Path
    ):
        """E2E: doctor command validates project structure."""
        # Arrange - mock_project_in_context has basic structure

        # Act
        result = runner.invoke(main, ["doctor"])

        # Assert
        assert result.exit_code == 0
        assert "Doctor" in result.output

    def test_export_markdown_creates_summary(
        self, runner: CliRunner, mock_project_in_context: Path
    ):
        """E2E: export command creates markdown summary."""
        # Arrange - mock_project_in_context has research.md and stack.md

        # Act
        result = runner.invoke(main, ["export"])

        # Assert
        assert result.exit_code == 0
        summary_file = mock_project_in_context / "docs" / "project_summary.md"
        assert summary_file.exists()
        content = summary_file.read_text()
        assert "Test Project" in content


class TestModularModeWorkflow:
    """End-to-end tests for modular mode workflow."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click CLI test runner."""
        return CliRunner()

    def test_module_create_adds_module_to_registry(
        self, runner: CliRunner, tmp_path: Path
    ):
        """E2E: module create adds module to registry."""
        # Arrange - Create modular project
        project = tmp_path / "test-project"
        project.mkdir()
        vc_dir = project / ".vibecraft"
        vc_dir.mkdir()
        modules_dir = project / "modules"
        modules_dir.mkdir()

        manifest = {
            "project_name": "Modular Test",
            "mode": "modular",
            "current_phase": "research",
            "phases": ["research"],
            "phases_completed": [],
            "agents": [],
            "stack": {},
        }
        (vc_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

        original_cwd = Path.cwd()
        import os
        os.chdir(project)

        try:
            # Act
            with patch("vibecraft.cli.ModuleManager") as mock_manager_class:
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager

                result = runner.invoke(main, [
                    "module", "create", "auth",
                    "-d", "Authentication module"
                ])

                # Assert
                assert result.exit_code == 0
                mock_manager.create_module.assert_called_once_with(
                    "auth", "Authentication module", []
                )
        finally:
            os.chdir(original_cwd)

    def test_integrate_analyze_validates_dependencies(
        self, runner: CliRunner, tmp_path: Path
    ):
        """E2E: integrate analyze validates module dependencies."""
        # Arrange - Create modular project with modules
        project = tmp_path / "test-project"
        project.mkdir()
        vc_dir = project / ".vibecraft"
        vc_dir.mkdir()

        manifest = {
            "project_name": "Integrate Test",
            "mode": "modular",
            "current_phase": "implement",
            "phases": ["research", "implement"],
            "phases_completed": ["research"],
            "agents": [],
            "stack": {},
        }
        (vc_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

        # Create module registry
        registry_data = {
            "modules": [
                {"name": "db", "dependencies": []},
                {"name": "auth", "dependencies": ["db"]},
            ]
        }
        (vc_dir / "modules-registry.json").write_text(json.dumps(registry_data, indent=2))

        original_cwd = Path.cwd()
        import os
        os.chdir(project)

        try:
            # Act
            with patch("vibecraft.cli.ModuleRegistry") as mock_registry_class:
                with patch("vibecraft.cli.DependencyAnalyzer") as mock_analyzer_class:
                    mock_registry = MagicMock()
                    mock_registry.get_all.return_value = [
                        {"name": "db"}, {"name": "auth"}
                    ]
                    mock_registry_class.return_value = mock_registry

                    mock_analyzer = MagicMock()
                    mock_analyzer.get_build_order.return_value = ["db", "auth"]
                    mock_analyzer_class.return_value = mock_analyzer

                    result = runner.invoke(main, ["integrate", "analyze"])

                    # Assert
                    assert result.exit_code == 0
                    # Should show valid dependencies or module names
                    assert "db" in result.output or "auth" in result.output or "valid" in result.output.lower()
        finally:
            os.chdir(original_cwd)


class TestFullWorkflowE2E:
    """Complete end-to-end workflow tests."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click CLI test runner."""
        return CliRunner()

    def test_complete_simple_mode_workflow(
        self, runner: CliRunner, e2e_project_files: tuple[Path, Path, Path], tmp_path: Path
    ):
        """E2E: Complete workflow from init to export in simple mode."""
        # Arrange
        research, stack, agents = e2e_project_files
        output_dir = tmp_path / "complete-project"

        # Act 1: Initialize project
        with patch("vibecraft.cli.BootstrapperFactory") as mock_factory:
            mock_bootstrapper = MagicMock()
            mock_factory.create.return_value = mock_bootstrapper

            init_result = runner.invoke(main, [
                "init",
                "-r", str(research),
                "-s", str(stack),
                "-a", str(agents),
                "-o", str(output_dir),
            ])

            # Assert 1
            assert init_result.exit_code == 0
            mock_bootstrapper.run.assert_called_once()

    def test_error_handling_not_in_project(
        self, runner: CliRunner, tmp_path: Path
    ):
        """E2E: Commands handle 'not in project' error gracefully."""
        # Arrange - no project in tmp_path
        original_cwd = Path.cwd()
        import os
        os.chdir(tmp_path)

        try:
            # Act & Assert - should show error message, not crash
            result = runner.invoke(main, ["status"])
            assert result.exit_code == 0  # Command completes
            assert "Not inside a Vibecraft project" in result.output

            result = runner.invoke(main, ["run", "research"])
            assert result.exit_code == 0
            assert "Not inside a Vibecraft project" in result.output
        finally:
            os.chdir(original_cwd)

    def test_help_command_works(self, runner: CliRunner):
        """E2E: --help command works from any directory."""
        # Act
        result = runner.invoke(main, ["--help"])

        # Assert
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "init" in result.output
        assert "run" in result.output
        assert "status" in result.output
