"""Tests for SkillRunner module."""

import pytest
from pathlib import Path
from vibecraft.runner import SkillRunner
from unittest.mock import patch, MagicMock

# Constants for test configuration
MAX_RETRIES = 3
EXPECTED_SKILL_COUNT = 5  # research, design, plan, implement, review


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

    def test_resolves_path_with_multiple_outputs_list(self, tmp_project):
        """Should handle list of output paths."""
        runner = SkillRunner(tmp_project)
        output = ["src/file1.py", "src/file2.py"]
        paths = [runner._resolve_output_path(p, None) for p in output]
        assert len(paths) == 2
        assert paths[0] == tmp_project / "src" / "file1.py"
        assert paths[1] == tmp_project / "src" / "file2.py"


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

    def test_saves_single_file(self, tmp_project):
        """_save_output writes content to specified file."""
        runner = SkillRunner(tmp_project)
        output_path = tmp_project / "docs" / "output.md"
        step = {}

        runner._save_output("# Test content", output_path, step)

        assert output_path.exists()
        assert output_path.read_text() == "# Test content"

    def test_creates_parent_directories(self, tmp_project):
        """_save_output creates parent directories if needed."""
        runner = SkillRunner(tmp_project)
        output_path = tmp_project / "deep" / "nested" / "path" / "file.md"
        step = {}

        runner._save_output("# Content", output_path, step)

        assert output_path.exists()

    def test_extracts_files_for_directory(self, tmp_project):
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

    def test_respects_immutability_constraint(self, tmp_project):
        """_save_output blocks writes to immutable paths."""
        runner = SkillRunner(tmp_project)
        # Create immutable file
        immutable = tmp_project / "src" / "tests" / "phase_1"
        immutable.mkdir(parents=True, exist_ok=True)
        (immutable / "test.py").write_text("# Locked")

        output_path = tmp_project / "src" / "tests" / "phase_1" / "test.py"
        step = {"constraint": {"immutable": "src/tests/phase_1"}}

        # Should not overwrite
        runner._save_output("# New content", output_path, step)

        # Original content should be preserved
        assert (immutable / "test.py").read_text() == "# Locked"


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

    def test_loads_skill_from_yaml(self, tmp_project):
        """_load_skill loads skill from YAML file."""
        runner = SkillRunner(tmp_project)
        skill_file = tmp_project / ".vibecraft" / "skills" / "test_skill.yaml"
        skill_file.write_text("name: test_skill\nsteps: []\n")

        skill = runner._load_skill("test_skill")

        assert skill is not None
        assert skill["name"] == "test_skill"

    def test_returns_none_for_missing_skill(self, tmp_project, capsys):
        """Should return None for non-existent skill."""
        runner = SkillRunner(tmp_project)

        skill = runner._load_skill("nonexistent_skill")

        assert skill is None
        captured = capsys.readouterr()
        assert "Skill not found" in captured.out

    def test_lists_available_skills_when_not_found(self, tmp_project, capsys):
        """_load_skill shows available skills when not found."""
        runner = SkillRunner(tmp_project)
        # Create a skill
        (tmp_project / ".vibecraft" / "skills" / "existing_skill.yaml").write_text(
            "name: existing"
        )

        runner._load_skill("missing_skill")

        captured = capsys.readouterr()
        assert "Available" in captured.out
        assert "existing_skill" in captured.out


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


class TestIsInside:
    """Tests for _is_inside helper method."""

    def test_path_inside_parent(self, tmp_project):
        """_is_inside returns True when path is within parent."""
        runner = SkillRunner(tmp_project)
        parent = tmp_project / "src" / "tests"
        child = parent / "test.py"

        assert runner._is_inside(child, parent) is True

    def test_path_outside_parent(self, tmp_project):
        """_is_inside returns False when path is outside parent."""
        runner = SkillRunner(tmp_project)
        parent = tmp_project / "src" / "tests"
        outside = tmp_project / "docs" / "file.md"

        assert runner._is_inside(outside, parent) is False


class TestSavePrompt:
    """Tests for _save_prompt method."""

    def test_saves_prompt_with_timestamp(self, tmp_project):
        """_save_prompt creates timestamped file in prompts directory."""
        runner = SkillRunner(tmp_project)
        prompt_content = "# Test Prompt"

        runner._save_prompt("test_step", prompt_content)

        prompts_dir = tmp_project / ".vibecraft" / "prompts"
        assert prompts_dir.exists()
        prompt_files = list(prompts_dir.glob("*.md"))
        assert len(prompt_files) > 0
        assert prompt_content in prompt_files[0].read_text()


class TestOpenInEditor:
    """Tests for _open_in_editor method."""

    def test_opens_file_in_editor(self, tmp_project, monkeypatch):
        """_open_in_editor calls subprocess with editor and file."""
        runner = SkillRunner(tmp_project)
        test_file = tmp_project / "test.md"
        test_file.write_text("# Test")

        # Mock subprocess and environment
        monkeypatch.setenv("EDITOR", "test_editor")
        with patch("vibecraft.modes.simple.runner.subprocess.run") as mock_run:
            runner._open_in_editor(test_file)
            mock_run.assert_called_once_with(["test_editor", str(test_file)])

    def test_handles_missing_file(self, tmp_project, monkeypatch, capsys):
        """_open_in_editor shows warning for missing file."""
        runner = SkillRunner(tmp_project)
        missing_file = tmp_project / "missing.md"

        monkeypatch.setenv("EDITOR", "test_editor")
        runner._open_in_editor(missing_file)

        captured = capsys.readouterr()
        assert "File not found" in captured.out

    def test_uses_default_editor_when_env_not_set(self, tmp_project, monkeypatch):
        """_open_in_editor uses 'nano' as default editor."""
        # Remove EDITOR and VISUAL env vars
        monkeypatch.delenv("EDITOR", raising=False)
        monkeypatch.delenv("VISUAL", raising=False)

        runner = SkillRunner(tmp_project)
        test_file = tmp_project / "test.md"
        test_file.write_text("# Test")

        with patch("vibecraft.modes.simple.runner.subprocess.run") as mock_run:
            runner._open_in_editor(test_file)
            mock_run.assert_called_once_with(["nano", str(test_file)])


class TestHandleError:
    """Tests for _handle_error method."""

    def test_returns_false_when_max_retries_reached(self, tmp_project):
        """_handle_error returns False when retries exhausted."""
        runner = SkillRunner(tmp_project)
        step = {}

        # Simulate max retries reached
        result = runner._handle_error(
            step=step, step_number=1, total_steps=3,
            skill={}, phase=None, retry_count=MAX_RETRIES, max_retries=MAX_RETRIES
        )

        assert result is False
