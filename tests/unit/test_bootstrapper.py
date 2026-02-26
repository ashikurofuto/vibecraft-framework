"""Tests for Bootstrapper module."""

import json
import pytest
from pathlib import Path
from vibecraft.bootstrapper import Bootstrapper
from vibecraft.modes.simple.bootstrapper import SimpleBootstrapper


class TestParseStack:
    """Tests for _parse_stack - the most bug-prone method."""

    def test_parses_double_hash_headings(self, tmp_path):
        """BUG-001 regression: ## Language: TypeScript should give key 'language'."""
        stack = "## Language: TypeScript\n## Framework: Phaser.js\n"
        b = _make_bootstrapper(tmp_path, stack=stack)
        result = b._parse_stack()
        assert "language" in result, f"Got keys: {list(result.keys())}"
        assert result["language"] == "TypeScript"
        assert "##_language" not in result

    def test_parses_single_hash_headings(self, tmp_path):
        """# Language: TypeScript should give key 'language'."""
        stack = "# Language: TypeScript\n# Framework: Phaser.js\n"
        b = _make_bootstrapper(tmp_path, stack=stack)
        result = b._parse_stack()
        assert result["language"] == "TypeScript"
        assert result["framework"] == "Phaser.js"

    def test_parses_asterisk_prefix(self, tmp_path):
        """* Language: TypeScript should give key 'language'."""
        stack = "* Language: TypeScript\n* Framework: Phaser.js\n"
        b = _make_bootstrapper(tmp_path, stack=stack)
        result = b._parse_stack()
        assert result["language"] == "TypeScript"

    def test_parses_dash_prefix(self, tmp_path):
        """- Language: TypeScript should give key 'language'."""
        stack = "- Language: TypeScript\n- Framework: Phaser.js\n"
        b = _make_bootstrapper(tmp_path, stack=stack)
        result = b._parse_stack()
        assert result["language"] == "TypeScript"

    def test_parses_mixed_formats(self, tmp_path):
        """Mixed formats should all parse correctly."""
        stack = """# Language: TypeScript
## Framework: Phaser.js
* Architecture: Clean
- Testing: Vitest
"""
        b = _make_bootstrapper(tmp_path, stack=stack)
        result = b._parse_stack()
        assert result == {
            "language": "TypeScript",
            "framework": "Phaser.js",
            "architecture": "Clean",
            "testing": "Vitest",
        }


class TestExtractProjectName:
    """Tests for _extract_project_name."""

    def test_extracts_from_h1_heading(self, tmp_path):
        """Should extract from # heading."""
        research = "# My Awesome Project\n\nSome description."
        b = _make_bootstrapper(tmp_path, research=research)
        assert b._extract_project_name() == "My Awesome Project"

    def test_extracts_from_h2_heading(self, tmp_path):
        """Should extract from ## heading."""
        research = "## My Awesome Project\n\nSome description."
        b = _make_bootstrapper(tmp_path, research=research)
        assert b._extract_project_name() == "My Awesome Project"

    def test_extracts_from_project_line(self, tmp_path):
        """Should extract from 'Project: name' line."""
        research = "Some intro\nProject: My Awesome Project\nMore text."
        b = _make_bootstrapper(tmp_path, research=research)
        assert b._extract_project_name() == "My Awesome Project"

    def test_returns_none_when_no_name_found(self, tmp_path):
        """BUG-006 regression: Should return None, not fallback to filename."""
        research = "Just some description without any project name."
        b = _make_bootstrapper(tmp_path, research=research)
        assert b._extract_project_name() is None

    def test_build_context_uses_fallback(self, tmp_path):
        """_build_context should use fallback when no name found."""
        research = "Just some description."
        b = _make_bootstrapper(tmp_path, research=research)
        ctx = b._build_context()
        # Fallback uses filename: research.md -> "Research"
        assert ctx["project_name"] == "Research"


class TestValidateInputs:
    """Tests for _validate_inputs."""

    def test_rejects_short_research(self, tmp_path):
        """Should reject research.md shorter than minimum."""
        research = "Too short"
        b = _make_bootstrapper(tmp_path, research=research)
        with pytest.raises(SystemExit):
            b._validate_inputs()

    def test_rejects_short_stack(self, tmp_path):
        """Should reject stack.md shorter than minimum."""
        stack = "x"
        b = _make_bootstrapper(tmp_path, stack=stack)
        with pytest.raises(SystemExit):
            b._validate_inputs()

    def test_rejects_missing_project_name(self, tmp_path):
        """BUG-006 regression: Should reject if no project name found."""
        research = "A" * 100  # Long enough but no project name
        b = _make_bootstrapper(tmp_path, research=research)
        with pytest.raises(SystemExit):
            b._validate_inputs()


class TestBootstrapperRun:
    """Integration tests for Bootstrapper.run()."""

    def test_creates_directory_structure(self, tmp_path, research_file, stack_file):
        """Should create all required directories."""
        b = _make_bootstrapper(tmp_path, research_file=research_file, stack_file=stack_file)
        b.run()

        output = tmp_path / "output"
        assert (output / ".vibecraft" / "agents").exists()
        assert (output / ".vibecraft" / "skills").exists()
        assert (output / ".vibecraft" / "prompts").exists()
        assert (output / ".vibecraft" / "snapshots").exists()
        assert (output / "docs" / "design").exists()
        assert (output / "docs" / "plans").exists()
        assert (output / "src" / "tests").exists()

    def test_copies_input_files(self, tmp_path, research_file, stack_file):
        """Should copy research.md and stack.md to docs/."""
        b = _make_bootstrapper(tmp_path, research_file=research_file, stack_file=stack_file)
        b.run()

        output = tmp_path / "output"
        assert (output / "docs" / "research.md").exists()
        assert (output / "docs" / "stack.md").exists()

    def test_generates_manifest(self, tmp_path, research_file, stack_file):
        """Should generate valid manifest.json."""
        b = _make_bootstrapper(tmp_path, research_file=research_file, stack_file=stack_file)
        b.run()

        output = tmp_path / "output"
        manifest_path = output / ".vibecraft" / "manifest.json"
        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text())
        assert "project_name" in manifest
        assert "project_type" in manifest
        assert "agents" in manifest
        assert "skills" in manifest
        assert "phases" in manifest
        assert "phases_completed" in manifest

    def test_generates_agents(self, tmp_path, research_file, stack_file):
        """Should generate agent files."""
        b = _make_bootstrapper(tmp_path, research_file=research_file, stack_file=stack_file)
        b.run()

        output = tmp_path / "output"
        agents_dir = output / ".vibecraft" / "agents"
        assert agents_dir.exists()
        agent_files = list(agents_dir.glob("*.md"))
        assert len(agent_files) > 0

    def test_generates_skills(self, tmp_path, research_file, stack_file):
        """Should generate skill YAML files."""
        b = _make_bootstrapper(tmp_path, research_file=research_file, stack_file=stack_file)
        b.run()

        output = tmp_path / "output"
        skills_dir = output / ".vibecraft" / "skills"
        assert skills_dir.exists()
        skill_files = list(skills_dir.glob("*.yaml"))
        assert len(skill_files) == 5  # research, design, plan, implement, review


def _make_bootstrapper(tmp_path, research="# Test\nContent", stack="## Lang: TS", research_file=None, stack_file=None):
    """Helper to create a Bootstrapper with minimal config."""
    if research_file is None:
        research_file = tmp_path / "research.md"
        research_file.write_text(research)
    if stack_file is None:
        stack_file = tmp_path / "stack.md"
        stack_file.write_text(stack)
    output = tmp_path / "output"
    output.mkdir(exist_ok=True)
    
    from vibecraft.core.config import VibecraftConfig, ProjectMode
    
    config = VibecraftConfig(
        project_name="Test Project",
        mode=ProjectMode.SIMPLE,
    )
    
    return SimpleBootstrapper(
        project_root=output,
        config=config,
        research_path=research_file,
        stack_path=stack_file,
        force=True,
    )
