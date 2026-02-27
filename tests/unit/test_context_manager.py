"""Tests for ContextManager module."""

import json
import pytest
from pathlib import Path
from vibecraft.context_manager import ContextManager


class TestNextPhase:
    """Tests for _next_phase - BUG-005 regression."""

    def test_advances_from_research_to_design(self, tmp_path):
        """After research_skill, should advance to design."""
        manifest = {
            "phases": ["research", "design", "plan", "implement", "review"],
            "phases_completed": ["research_skill"],
        }
        cm = ContextManager(tmp_path)
        assert cm._next_phase(manifest) == "design"

    def test_advances_from_design_to_plan(self, tmp_path):
        """After design_skill, should advance to plan."""
        manifest = {
            "phases": ["research", "design", "plan", "implement", "review"],
            "phases_completed": ["research_skill", "design_skill"],
        }
        cm = ContextManager(tmp_path)
        assert cm._next_phase(manifest) == "plan"

    def test_implement_phase_1_does_not_complete_implement(self, tmp_path):
        """BUG-005 regression: implement_phase_1 should NOT complete 'implement'."""
        manifest = {
            "phases": ["research", "design", "plan", "implement", "review"],
            "phases_completed": ["research_skill", "design_skill", "plan_skill", "implement_phase_1"],
            "total_implement_phases": 0,  # Not set
        }
        cm = ContextManager(tmp_path)
        # Should stay on 'implement', not advance to 'review'
        assert cm._next_phase(manifest) == "implement"

    def test_all_implement_phases_completes_implement(self, tmp_path):
        """When all implement phases done, should advance to review."""
        manifest = {
            "phases": ["research", "design", "plan", "implement", "review"],
            "phases_completed": [
                "research_skill", "design_skill", "plan_skill",
                "implement_phase_1", "implement_phase_2", "implement_phase_3"
            ],
            "total_implement_phases": 3,
        }
        cm = ContextManager(tmp_path)
        assert cm._next_phase(manifest) == "review"

    def test_explicit_implement_completes_implement(self, tmp_path):
        """Explicit 'implement' in phases_completed completes the phase."""
        manifest = {
            "phases": ["research", "design", "plan", "implement", "review"],
            "phases_completed": ["research_skill", "design_skill", "plan_skill", "implement"],
        }
        cm = ContextManager(tmp_path)
        assert cm._next_phase(manifest) == "review"

    def test_all_phases_done_returns_done(self, tmp_path):
        """When all phases complete, should return 'done'."""
        manifest = {
            "phases": ["research", "design", "plan", "implement", "review"],
            "phases_completed": [
                "research_skill", "design_skill", "plan_skill",
                "implement_phase_1", "implement_phase_2", "implement_phase_3", "review_skill"
            ],
            "total_implement_phases": 3,
        }
        cm = ContextManager(tmp_path)
        assert cm._next_phase(manifest) == "done"


class TestCompleteSkill:
    """Tests for complete_skill."""

    def test_adds_skill_to_phases_completed(self, tmp_project):
        """Should add skill to phases_completed."""
        cm = ContextManager(tmp_project)
        cm.complete_skill("research_skill")

        manifest = cm.load_manifest()
        assert "research_skill" in manifest["phases_completed"]

    def test_updates_current_phase(self, tmp_project):
        """Should update current_phase after skill completion."""
        cm = ContextManager(tmp_project)
        cm.complete_skill("research_skill")

        manifest = cm.load_manifest()
        assert manifest["current_phase"] == "design"

    def test_updates_timestamp(self, tmp_project):
        """Should update updated_at timestamp."""
        cm = ContextManager(tmp_project)
        cm.complete_skill("research_skill")

        manifest = cm.load_manifest()
        assert "updated_at" in manifest


class TestExtractAdrs:
    """Tests for _extract_adrs - BUG-012 regression."""

    def test_extracts_adr_from_headings(self, tmp_project):
        """Should extract ADR lines from headings."""
        arch_path = tmp_project / "docs" / "design" / "architecture.md"
        arch_path.parent.mkdir(parents=True, exist_ok=True)
        arch_path.write_text("""# Architecture

## ADR-001: Use TypeScript
We chose TypeScript for type safety.

## ADR-002: Clean Architecture
Layers: Domain, Application, Infrastructure.
""")
        cm = ContextManager(tmp_project)
        adrs = cm._extract_adrs()
        assert "ADR-001: Use TypeScript" in adrs
        assert "ADR-002: Clean Architecture" in adrs

    def test_extracts_adr_with_bullet_points(self, tmp_project):
        """Should extract ADR lines even with bullet prefixes."""
        arch_path = tmp_project / "docs" / "design" / "architecture.md"
        arch_path.parent.mkdir(parents=True, exist_ok=True)
        arch_path.write_text("""# Architecture

- ADR-001: Use TypeScript
* ADR-002: Clean Architecture
""")
        cm = ContextManager(tmp_project)
        adrs = cm._extract_adrs()
        assert "ADR-001: Use TypeScript" in adrs
        assert "ADR-002: Clean Architecture" in adrs

    def test_returns_empty_when_no_adrs(self, tmp_project):
        """Should return empty list when no ADRs found."""
        arch_path = tmp_project / "docs" / "design" / "architecture.md"
        arch_path.parent.mkdir(parents=True, exist_ok=True)
        arch_path.write_text("# Architecture\n\nNo ADRs here.\n")
        cm = ContextManager(tmp_project)
        adrs = cm._extract_adrs()
        assert adrs == []

    def test_returns_empty_when_no_architecture_file(self, tmp_path):
        """Should return empty list when architecture.md doesn't exist."""
        cm = ContextManager(tmp_path)
        adrs = cm._extract_adrs()
        assert adrs == []


class TestPrintStatus:
    """Tests for print_status."""

    def test_prints_project_info(self, tmp_project, capsys):
        """Should print project name and type."""
        cm = ContextManager(tmp_project)
        cm.print_status()
        captured = capsys.readouterr()
        assert "Tower Defense Game (Multiplayer)" in captured.out

    def test_shows_phase_status(self, tmp_project, capsys):
        """Should show phase status table."""
        cm = ContextManager(tmp_project)
        cm.print_status()
        captured = capsys.readouterr()
        assert "research" in captured.out
        assert "current" in captured.out or "done" in captured.out


class TestCompletePhase:
    """Tests for complete_phase method."""

    def test_completes_implement_phase(self, tmp_project):
        """complete_phase adds implement_phase_N to phases_completed."""
        # Arrange
        cm = ContextManager(tmp_project)
        manifest = cm.load_manifest()
        assert "implement_phase_1" not in manifest["phases_completed"]

        # Act
        cm.complete_phase(1)

        # Assert
        updated = cm.load_manifest()
        assert "implement_phase_1" in updated["phases_completed"]

    def test_updates_timestamp(self, tmp_project):
        """complete_phase updates updated_at timestamp."""
        # Arrange
        cm = ContextManager(tmp_project)

        # Act
        cm.complete_phase(1)

        # Assert - timestamp should be set
        updated = cm.load_manifest()
        assert "updated_at" in updated
        assert updated["updated_at"].endswith("Z")

    def test_rebuilds_context_md(self, tmp_project):
        """complete_phase rebuilds context.md."""
        # Arrange
        cm = ContextManager(tmp_project)
        context_path = tmp_project / "docs" / "context.md"
        original_content = context_path.read_text()

        # Act
        cm.complete_phase(1)

        # Assert - context.md should be updated
        new_content = context_path.read_text()
        assert new_content != original_content or "Implement Phase 1" in new_content


class TestBuildAndCopy:
    """Tests for build_and_copy method."""

    def test_copies_context_to_clipboard(self, tmp_project, monkeypatch):
        """build_and_copy copies context to clipboard."""
        # Arrange
        cm = ContextManager(tmp_project)
        copied_text = None

        def mock_copy(text):
            nonlocal copied_text
            copied_text = text

        monkeypatch.setattr("vibecraft.context_manager.pyperclip.copy", mock_copy)

        # Act
        cm.build_and_copy()

        # Assert
        assert copied_text is not None
        assert "Tower Defense Game" in copied_text

    def test_adds_skill_content_when_provided(self, tmp_project, monkeypatch):
        """build_and_copy adds skill content when skill parameter provided."""
        # Arrange
        cm = ContextManager(tmp_project)
        # Create a skill file
        skill_file = tmp_project / ".vibecraft" / "skills" / "test_skill.yaml"
        skill_file.write_text("name: test_skill\nsteps: []\n")

        copied_text = None
        def mock_copy(text):
            nonlocal copied_text
            copied_text = text

        monkeypatch.setattr("vibecraft.context_manager.pyperclip.copy", mock_copy)

        # Act
        cm.build_and_copy(skill="test")

        # Assert
        assert copied_text is not None
        assert "test_skill" in copied_text

    def test_warns_when_skill_not_found(self, tmp_project, monkeypatch, capsys):
        """build_and_copy shows warning when skill file not found."""
        # Arrange
        cm = ContextManager(tmp_project)
        monkeypatch.setattr("vibecraft.context_manager.pyperclip.copy", lambda x: None)

        # Act
        cm.build_and_copy(skill="nonexistent")

        # Assert
        captured = capsys.readouterr()
        assert "Skill not found" in captured.out

    def test_handles_clipboard_unavailable(self, tmp_project, monkeypatch, capsys):
        """build_and_copy handles clipboard unavailable gracefully."""
        # Arrange
        cm = ContextManager(tmp_project)

        def mock_copy_fail(text):
            raise RuntimeError("Clipboard unavailable")

        monkeypatch.setattr("vibecraft.context_manager.pyperclip.copy", mock_copy_fail)

        # Act - should not raise
        cm.build_and_copy()

        # Assert
        captured = capsys.readouterr()
        assert "Clipboard unavailable" in captured.out
