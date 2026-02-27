"""Shared fixtures for Vibecraft tests."""

import json
import os
import pytest
from pathlib import Path
from click.testing import CliRunner


SAMPLE_RESEARCH = """# Tower Defense Game (Multiplayer)

## Idea
A browser-based multiplayer tower defense game where 2-4 players
cooperate to defend a base against waves of enemies.

## Goals
- Real-time cooperative multiplayer (2-4 players)
- At least 5 tower types with upgrade paths

## Risks
- WebSocket latency
"""

SAMPLE_STACK = """## Language: TypeScript
## Framework: Phaser.js (game engine)
## Architecture: Clean Architecture
## Testing: Vitest
## Principles
- No `any` types
"""

SAMPLE_STACK_WITH_HASH = """# Stack

## Language: TypeScript
## Framework: Phaser.js
## Architecture: Clean Architecture
"""

SAMPLE_MANIFEST = {
    "project_name": "Tower Defense Game (Multiplayer)",
    "project_type": ["game", "multiplayer", "web"],
    "created_at": "2025-01-01T00:00:00Z",
    "stack": {"language": "TypeScript", "framework": "Phaser.js"},
    "agents": ["researcher", "architect", "tdd_writer", "implementer", "code_reviewer"],
    "skills": ["research_skill", "design_skill", "plan_skill", "implement_skill", "review_skill"],
    "current_phase": "research",
    "phases": ["research", "design", "plan", "implement", "review"],
    "phases_completed": [],
}


# ------------------------------------------------------------------ #
#  Core fixtures
# ------------------------------------------------------------------ #

@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a minimal valid vibecraft project in tmp_path."""
    vc_dir = tmp_path / ".vibecraft"
    vc_dir.mkdir()
    (vc_dir / "agents").mkdir()
    skills_dir = vc_dir / "skills"
    skills_dir.mkdir()
    (vc_dir / "prompts").mkdir()
    (vc_dir / "snapshots").mkdir()

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "design").mkdir()
    (docs_dir / "plans").mkdir()
    (tmp_path / "src" / "tests").mkdir(parents=True)

    (docs_dir / "research.md").write_text(SAMPLE_RESEARCH)
    (docs_dir / "stack.md").write_text(SAMPLE_STACK)
    (docs_dir / "context.md").write_text("# Project Context\n")

    # Create minimal skill files
    (skills_dir / "research_skill.yaml").write_text("name: research_skill\nsteps: []\n")
    (skills_dir / "design_skill.yaml").write_text("name: design_skill\nsteps: []\n")
    (skills_dir / "plan_skill.yaml").write_text("name: plan_skill\nsteps: []\n")
    (skills_dir / "implement_skill.yaml").write_text("name: implement_skill\nsteps: []\n")
    (skills_dir / "review_skill.yaml").write_text("name: review_skill\nsteps: []\n")

    manifest_path = vc_dir / "manifest.json"
    manifest_path.write_text(json.dumps(SAMPLE_MANIFEST, indent=2))

    return tmp_path


@pytest.fixture
def research_file(tmp_path: Path) -> Path:
    """Create a sample research.md file."""
    p = tmp_path / "research.md"
    p.write_text(SAMPLE_RESEARCH)
    return p


@pytest.fixture
def stack_file(tmp_path: Path) -> Path:
    """Create a sample stack.md file."""
    p = tmp_path / "stack.md"
    p.write_text(SAMPLE_STACK)
    return p


@pytest.fixture
def stack_file_with_hash(tmp_path: Path) -> Path:
    """Create a sample stack file with hash header."""
    p = tmp_path / "stack_with_hash.md"
    p.write_text(SAMPLE_STACK_WITH_HASH)
    return p


# ------------------------------------------------------------------ #
#  CLI fixtures
# ------------------------------------------------------------------ #

@pytest.fixture
def cli_runner() -> CliRunner:
    """Create Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_project(tmp_path: Path) -> Path:
    """Create mock Vibecraft project for CLI tests."""
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
    os.chdir(project)

    yield project

    os.chdir(original_cwd)


@pytest.fixture
def mock_project_with_manifest(tmp_path: Path, manifest_data: dict | None = None):
    """Create mock Vibecraft project with custom manifest data.
    
    Usage:
        def test_something(mock_project_with_manifest):
            # Uses default manifest
            pass
            
        def test_custom(mock_project_with_manifest):
            # Override with pytest.fixture
            pass
    """
    project = tmp_path / "test-project"
    project.mkdir()
    vibecraft_dir = project / ".vibecraft"
    vibecraft_dir.mkdir()
    
    default_manifest = {
        "project_name": "Test Project",
        "project_type": ["test"],
        "current_phase": "research",
        "phases": ["research", "design", "plan", "implement", "review"],
        "phases_completed": [],
        "agents": ["researcher"],
        "stack": {"language": "Python"},
    }
    
    manifest = manifest_data if manifest_data else default_manifest
    (vibecraft_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    original_cwd = Path.cwd()
    os.chdir(project)

    yield project

    os.chdir(original_cwd)


@pytest.fixture
def mock_project_in_context(tmp_path: Path):
    """Create mock project and return context manager for changing directory.
    
    This fixture properly handles cleanup even if test fails.
    
    Usage:
        def test_something(mock_project_in_context, tmp_path):
            project = mock_project_in_context
            # Already in project directory
    """
    project = tmp_path / "test-project"
    project.mkdir()
    vibecraft_dir = project / ".vibecraft"
    vibecraft_dir.mkdir()
    docs_dir = project / "docs"
    docs_dir.mkdir()
    
    (vibecraft_dir / "manifest.json").write_text(json.dumps({
        "project_name": "Test Project",
        "current_phase": "research",
        "phases": ["research"],
        "phases_completed": [],
        "agents": [],
        "stack": {},
    }))
    
    (docs_dir / "research.md").write_text("# Research\n\nTest content")
    (docs_dir / "stack.md").write_text("# Stack\n\nPython")

    original_cwd = Path.cwd()
    os.chdir(project)

    yield project

    os.chdir(original_cwd)


# ------------------------------------------------------------------ #
#  E2E Test fixtures
# ------------------------------------------------------------------ #

@pytest.fixture
def e2e_project_files(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create research.md, stack.md and agents.yaml for E2E testing."""
    research = tmp_path / "research.md"
    research.write_text("""# Test E2E Project

## Idea
A test project for end-to-end integration testing.

## Goals
- Test vibecraft init command
- Test vibecraft run command
- Verify project structure creation
""")

    stack = tmp_path / "stack.md"
    stack.write_text("""# Stack

## Language: Python
## Framework: FastAPI
## Architecture: Clean Architecture
## Testing: pytest
""")

    agents = tmp_path / "agents.yaml"
    agents.write_text("""- name: custom_agent
  description: Custom test agent
  triggers: ["test", "e2e"]
""")

    return research, stack, agents


# ------------------------------------------------------------------ #
#  Factory fixtures
# ------------------------------------------------------------------ #

@pytest.fixture
def factory_config() -> VibecraftConfig:
    """Create test VibecraftConfig for factory tests."""
    from vibecraft.core.config import VibecraftConfig
    return VibecraftConfig(project_name="test-project")


@pytest.fixture
def factory_project_root(tmp_path: Path) -> Path:
    """Create temporary project root for factory tests."""
    proj = tmp_path / "test-project"
    proj.mkdir()
    return proj
