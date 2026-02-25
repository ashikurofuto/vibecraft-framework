"""Tests for RollbackManager module."""

import json
import pytest
from pathlib import Path
from vibecraft.rollback import RollbackManager


class TestListSnapshots:
    """Tests for list_snapshots."""

    def test_returns_empty_when_no_snapshots(self, tmp_path):
        """Should return empty list when no snapshots exist."""
        rm = RollbackManager(tmp_path)
        assert rm.list_snapshots() == []

    def test_returns_sorted_snapshots(self, tmp_path):
        """Should return snapshots sorted by name (newest first)."""
        snapshots_dir = tmp_path / ".vibecraft" / "snapshots"
        snapshots_dir.mkdir(parents=True)
        (snapshots_dir / "20250101T100000_design").mkdir()
        (snapshots_dir / "20250101T120000_research").mkdir()
        (snapshots_dir / "20250101T110000_plan").mkdir()

        rm = RollbackManager(tmp_path)
        snapshots = rm.list_snapshots()

        assert len(snapshots) == 3
        # Should be sorted: 12:00, 11:00, 10:00
        assert "120000" in snapshots[0].name
        assert "110000" in snapshots[1].name
        assert "100000" in snapshots[2].name


class TestRollback:
    """Tests for rollback."""

    def test_restores_docs_and_src(self, tmp_path):
        """Should restore docs/ and src/ from snapshot."""
        # Create project structure
        vc_dir = tmp_path / ".vibecraft"
        snapshots_dir = vc_dir / "snapshots"
        vc_dir.mkdir()
        snapshots_dir.mkdir()

        # Create snapshot with docs and src
        snap = snapshots_dir / "20250101T120000_design"
        snap.mkdir()
        (snap / "docs").mkdir()
        (snap / "src").mkdir()
        (snap / "docs" / "research.md").write_text("Old research")
        (snap / "src" / "main.ts").write_text("Old code")

        # Create current (different) docs and src
        (tmp_path / "docs").mkdir()
        (tmp_path / "src").mkdir()
        (tmp_path / "docs" / "research.md").write_text("New research")
        (tmp_path / "docs" / "stack.md").write_text("Stack")
        (tmp_path / "src" / "main.ts").write_text("New code")

        rm = RollbackManager(tmp_path)
        # Auto-confirm by mocking input
        import builtins
        original_input = builtins.input
        builtins.input = lambda *args: "y"
        try:
            rm.rollback("20250101T120000_design")
        finally:
            builtins.input = original_input

        # Verify restoration
        assert (tmp_path / "docs" / "research.md").read_text() == "Old research"
        assert (tmp_path / "src" / "main.ts").read_text() == "Old code"

    def test_restores_manifest(self, tmp_path):
        """BUG-004 regression: Should restore manifest.json from snapshot."""
        # Create project structure
        vc_dir = tmp_path / ".vibecraft"
        snapshots_dir = vc_dir / "snapshots"
        vc_dir.mkdir()
        snapshots_dir.mkdir()

        # Create snapshot with manifest
        snap = snapshots_dir / "20250101T120000_design"
        snap.mkdir()
        manifest_data = {"current_phase": "design", "phases_completed": ["research"]}
        (snap / "manifest.json").write_text(json.dumps(manifest_data))

        # Create current manifest (different)
        current_manifest = vc_dir / "manifest.json"
        current_manifest.write_text(json.dumps({
            "current_phase": "plan",
            "phases_completed": ["research", "design"]
        }))

        rm = RollbackManager(tmp_path)
        import builtins
        original_input = builtins.input
        builtins.input = lambda *args: "y"
        try:
            rm.rollback("20250101T120000_design")
        finally:
            builtins.input = original_input

        # Verify manifest restoration
        restored = json.loads(current_manifest.read_text())
        assert restored["current_phase"] == "design"
        assert restored["phases_completed"] == ["research"]

    def test_cancels_on_negative_response(self, tmp_path):
        """Should cancel rollback on 'n' response."""
        snapshots_dir = tmp_path / ".vibecraft" / "snapshots"
        snapshots_dir.mkdir(parents=True)
        snap = snapshots_dir / "20250101T120000_design"
        snap.mkdir()
        (snap / "docs").mkdir()
        (snap / "docs" / "research.md").write_text("Old research")

        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "research.md").write_text("New research")

        rm = RollbackManager(tmp_path)
        import builtins
        original_input = builtins.input
        builtins.input = lambda *args: "n"
        try:
            result = rm.rollback("20250101T120000_design")
        finally:
            builtins.input = original_input

        assert result is False
        # Should not have changed
        assert (tmp_path / "docs" / "research.md").read_text() == "New research"

    def test_handles_missing_snapshot(self, tmp_path, capsys):
        """Should handle non-existent snapshot gracefully."""
        rm = RollbackManager(tmp_path)
        result = rm.rollback("nonexistent")
        assert result is False

    def test_handles_empty_snapshot(self, tmp_path, capsys):
        """Should handle snapshot without docs/src."""
        snapshots_dir = tmp_path / ".vibecraft" / "snapshots"
        snapshots_dir.mkdir(parents=True)
        snap = snapshots_dir / "20250101T120000_empty"
        snap.mkdir()

        rm = RollbackManager(tmp_path)
        import builtins
        original_input = builtins.input
        builtins.input = lambda *args: "y"
        try:
            result = rm.rollback("20250101T120000_empty")
        finally:
            builtins.input = original_input

        assert result is False


class TestPrintSnapshots:
    """Tests for print_snapshots."""

    def test_shows_message_when_empty(self, tmp_path, capsys):
        """Should show message when no snapshots exist."""
        rm = RollbackManager(tmp_path)
        rm.print_snapshots()
        captured = capsys.readouterr()
        assert "No snapshots found" in captured.out or "No snapshots" in captured.out

    def test_shows_table_with_snapshots(self, tmp_path, capsys):
        """Should show table with snapshot details."""
        snapshots_dir = tmp_path / ".vibecraft" / "snapshots"
        snapshots_dir.mkdir(parents=True)
        (snapshots_dir / "20250101T120000_design").mkdir()

        rm = RollbackManager(tmp_path)
        rm.print_snapshots()
        captured = capsys.readouterr()
        assert "design" in captured.out
        assert "2025" in captured.out
