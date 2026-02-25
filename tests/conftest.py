"""Shared fixtures for Vibecraft tests."""

import json
import pytest
from pathlib import Path


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
    p = tmp_path / "research.md"
    p.write_text(SAMPLE_RESEARCH)
    return p


@pytest.fixture
def stack_file(tmp_path: Path) -> Path:
    p = tmp_path / "stack.md"
    p.write_text(SAMPLE_STACK)
    return p


@pytest.fixture
def stack_file_with_hash(tmp_path: Path) -> Path:
    p = tmp_path / "stack_with_hash.md"
    p.write_text(SAMPLE_STACK_WITH_HASH)
    return p
