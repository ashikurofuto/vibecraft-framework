"""Tests for SkillRunner module."""

import pytest
from pathlib import Path
from vibecraft.runner import SkillRunner


class TestResolveOutputPath:
    """Tests for _resolve_output_path."""

    def test_resolves_simple_path(self, tmp_project):
        """Should resolve simple path."""
        runner = SkillRunner(tmp_project)
        path = runner._resolve_output_path("docs/test.md", None)
        assert path == tmp_project / "docs" / "test.md"

    def test_resolves_phase_placeholder(self, tmp_project):
        """Should replace {phase} with phase number."""
        runner = SkillRunner(tmp_project)
        path = runner._resolve_output_path("src/tests/phase_{phase}/", 1)
        assert path == tmp_project / "src" / "tests" / "phase_1"

    def test_raises_when_phase_required_but_missing(self, tmp_project):
        """BUG-007 regression: Should raise when {phase} in path but phase=None."""
        runner = SkillRunner(tmp_project)
        with pytest.raises(ValueError, match="requires --phase"):
            runner._resolve_output_path("src/tests/phase_{phase}/", None)


class TestExtractFilesFromResponse:
    """Tests for _extract_files_from_response."""

    def test_extracts_single_file_with_heading(self, tmp_project):
        """Should extract file from ### heading + code block."""
        runner = SkillRunner(tmp_project)
        response = """### src/main.ts
```typescript
console.log("Hello");
```
"""
        output_dir = tmp_project / "src"
        output_dir.mkdir(exist_ok=True)
        created = runner._extract_files_from_response(response, output_dir)

        assert len(created) == 1
        assert created[0].name == "main.ts"
        assert 'console.log("Hello")' in created[0].read_text()

    def test_extracts_file_with_backticks_in_heading(self, tmp_project):
        """Should extract file from ### `filename` heading."""
        runner = SkillRunner(tmp_project)
        response = """### `src/utils.ts`
```typescript
export const x = 1;
```
"""
        output_dir = tmp_project / "src"
        output_dir.mkdir(exist_ok=True)
        created = runner._extract_files_from_response(response, output_dir)

        assert len(created) == 1
        assert created[0].name == "utils.ts"

    def test_extracts_file_with_bold_backtick(self, tmp_project):
        """Should extract file from **`filename`** heading."""
        runner = SkillRunner(tmp_project)
        response = """**`src/helper.ts`**
```typescript
function help() {}
```
"""
        output_dir = tmp_project / "src"
        output_dir.mkdir(exist_ok=True)
        created = runner._extract_files_from_response(response, output_dir)

        assert len(created) == 1
        assert created[0].name == "helper.ts"

    def test_extracts_multiple_files(self, tmp_project):
        """Should extract multiple files from response."""
        runner = SkillRunner(tmp_project)
        response = """### src/a.ts
```typescript
export const a = 1;
```

### src/b.ts
```typescript
export const b = 2;
```
"""
        output_dir = tmp_project / "src"
        output_dir.mkdir(exist_ok=True)
        created = runner._extract_files_from_response(response, output_dir)

        assert len(created) == 2

    def test_fallback_to_output_md(self, tmp_project):
        """Should save as output.md when no files found."""
        runner = SkillRunner(tmp_project)
        response = "Just plain text without code blocks"

        output_dir = tmp_project / "src"
        output_dir.mkdir(exist_ok=True)
        created = runner._extract_files_from_response(response, output_dir)

        assert len(created) == 1
        assert created[0].name == "output.md"
        assert "Just plain text" in created[0].read_text()


class TestSaveOutput:
    """Tests for _save_output."""

    def test_saves_single_file(self, tmp_project, capsys):
        """Should save response to single file."""
        runner = SkillRunner(tmp_project)
        output_path = tmp_project / "docs" / "output.md"

        runner._save_output("Test content", output_path, {})

        assert output_path.read_text() == "Test content"

    def test_extracts_files_for_directory(self, tmp_project, capsys):
        """Should extract files when output is directory."""
        runner = SkillRunner(tmp_project)
        output_dir = tmp_project / "output"
        output_dir.mkdir(exist_ok=True)

        response = """### test.ts
```typescript
test();
```
"""
        runner._save_output(response, output_dir, {})

        assert (output_dir / "test.ts").exists()

    def test_respects_immutability_constraint(self, tmp_project, capsys):
        """Should not save inside immutable path."""
        runner = SkillRunner(tmp_project)
        output_path = tmp_project / "src" / "tests" / "test.ts"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        step = {"constraint": {"immutable": "src/tests/"}}
        runner._save_output("content", output_path, step)

        # Should not have saved
        assert not output_path.exists()


class TestLoadSkill:
    """Tests for _load_skill."""

    def test_loads_skill_with_suffix(self, tmp_project):
        """Should find skill with _skill suffix."""
        # Create a skill file first
        skills_dir = tmp_project / ".vibecraft" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        (skills_dir / "research_skill.yaml").write_text("name: research_skill\n")

        runner = SkillRunner(tmp_project)
        skill = runner._load_skill("research_skill")
        assert skill is not None
        assert skill["name"] == "research_skill"

    def test_loads_skill_without_suffix(self, tmp_project):
        """Should find skill without _skill suffix."""
        # Create a skill file first
        skills_dir = tmp_project / ".vibecraft" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        (skills_dir / "research_skill.yaml").write_text("name: research_skill\n")

        runner = SkillRunner(tmp_project)
        skill = runner._load_skill("research")
        assert skill is not None
        assert skill["name"] == "research_skill"

    def test_returns_none_for_missing_skill(self, tmp_project, capsys):
        """Should return None for non-existent skill."""
        runner = SkillRunner(tmp_project)
        skill = runner._load_skill("nonexistent")
        assert skill is None
        captured = capsys.readouterr()
        assert "not found" in captured.out


class TestSnapshot:
    """Tests for _snapshot."""

    def test_creates_snapshot_directory(self, tmp_project):
        """Should create timestamped snapshot directory."""
        runner = SkillRunner(tmp_project)
        runner._snapshot("test_skill")

        snapshots_dir = tmp_project / ".vibecraft" / "snapshots"
        assert snapshots_dir.exists()
        snapshots = list(snapshots_dir.glob("*_test_skill"))
        assert len(snapshots) > 0

    def test_snapshots_docs_and_src(self, tmp_project):
        """Should copy docs/ and src/ to snapshot."""
        # Add content to docs/src
        (tmp_project / "docs" / "test.md").write_text("test")
        (tmp_project / "src" / "test.ts").write_text("test")

        runner = SkillRunner(tmp_project)
        runner._snapshot("test_skill")

        snapshots_dir = tmp_project / ".vibecraft" / "snapshots"
        snapshots = list(snapshots_dir.glob("*_test_skill"))
        assert len(snapshots) > 0

        snap = snapshots[0]
        assert (snap / "docs" / "test.md").exists()
        assert (snap / "src" / "test.ts").exists()

    def test_snapshots_manifest(self, tmp_project):
        """BUG-004 regression: Should copy manifest.json to snapshot."""
        runner = SkillRunner(tmp_project)
        runner._snapshot("test_skill")

        snapshots_dir = tmp_project / ".vibecraft" / "snapshots"
        snapshots = list(snapshots_dir.glob("*_test_skill"))
        assert len(snapshots) > 0

        snap = snapshots[0]
        assert (snap / "manifest.json").exists()
