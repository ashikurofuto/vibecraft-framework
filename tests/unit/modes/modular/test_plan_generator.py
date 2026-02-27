"""
Tests for Vibecraft PlanGenerator.

Tests verify module extraction from research.md and plan generation.
"""

import pytest
from pathlib import Path
from vibecraft.modes.modular.plan_generator import PlanGenerator


class TestPlanGenerator:
    """Tests for PlanGenerator class."""

    @pytest.fixture
    def project_root(self, tmp_path: Path) -> Path:
        """Create project root with docs directory."""
        root = tmp_path / "test-project"
        root.mkdir()
        (root / "docs").mkdir()
        return root

    def test_extract_modules_returns_empty_when_research_not_exists(
        self, project_root: Path
    ):
        """extract_modules() returns empty list when research.md missing."""
        # Arrange
        generator = PlanGenerator(project_root)

        # Act
        result = generator.extract_modules()

        # Assert
        assert result == []

    def test_extract_modules_returns_empty_when_research_is_empty(
        self, project_root: Path
    ):
        """extract_modules() returns empty list when research.md has no modules."""
        # Arrange
        research_path = project_root / "docs" / "research.md"
        research_path.write_text("# Empty Research\n\nNo modules here.")
        generator = PlanGenerator(project_root)

        # Act
        result = generator.extract_modules()

        # Assert
        assert result == []

    def test_extract_modules_finds_dash_format_modules(self, project_root: Path):
        """extract_modules() parses '- module_name: Description' format."""
        # Arrange
        research_path = project_root / "docs" / "research.md"
        research_path.write_text("""# Research

## Modules
- auth: Authentication module
- users: User management
""")
        generator = PlanGenerator(project_root)

        # Act
        result = generator.extract_modules()

        # Assert
        assert len(result) == 2
        assert result[0]["name"] == "auth"
        assert result[0]["description"] == "Authentication module"
        assert result[0]["status"] == "planned"
        assert result[0]["dependencies"] == []

    def test_extract_modules_finds_asterisk_format_modules(self, project_root: Path):
        """extract_modules() parses '* module_name: Description' format."""
        # Arrange
        research_path = project_root / "docs" / "research.md"
        research_path.write_text("""# Research

## Modules
* auth: Authentication module
* users: User management
""")
        generator = PlanGenerator(project_root)

        # Act
        result = generator.extract_modules()

        # Assert
        assert len(result) == 2
        assert result[0]["name"] == "auth"
        assert result[1]["name"] == "users"

    def test_extract_modules_handles_indented_module_list(
        self, project_root: Path
    ):
        """extract_modules() handles indented module definitions."""
        # Arrange
        research_path = project_root / "docs" / "research.md"
        research_path.write_text("""# Research

## Modules
  - auth: Authentication module
    - users: User management
""")
        generator = PlanGenerator(project_root)

        # Act
        result = generator.extract_modules()

        # Assert
        assert len(result) == 2

    def test_extract_modules_strips_description_whitespace(
        self, project_root: Path
    ):
        """extract_modules() strips whitespace from descriptions."""
        # Arrange
        research_path = project_root / "docs" / "research.md"
        research_path.write_text("- auth:    Authentication with JWT    ")
        generator = PlanGenerator(project_root)

        # Act
        result = generator.extract_modules()

        # Assert
        assert result[0]["description"] == "Authentication with JWT"

    def test_extract_modules_only_matches_valid_identifiers(
        self, project_root: Path
    ):
        """extract_modules() only matches valid module names (word chars)."""
        # Arrange
        research_path = project_root / "docs" / "research.md"
        research_path.write_text("""# Research
- auth: Valid module
- invalid-module: Should not match (hyphen)
- also_valid: Another module
""")
        generator = PlanGenerator(project_root)

        # Act
        result = generator.extract_modules()

        # Assert - only valid identifiers matched
        names = [m["name"] for m in result]
        assert "auth" in names
        assert "also_valid" in names
        assert "invalid-module" not in names

    def test_generate_plan_creates_file(self, project_root: Path):
        """generate_plan() creates development-plan.md file."""
        # Arrange
        generator = PlanGenerator(project_root)

        # Act
        generator.generate_plan()

        # Assert
        plan_path = project_root / "docs" / "plans" / "development-plan.md"
        assert plan_path.exists()

    def test_generate_plan_returns_markdown_string(self, project_root: Path):
        """generate_plan() returns plan content as string."""
        # Arrange
        generator = PlanGenerator(project_root)

        # Act
        result = generator.generate_plan()

        # Assert
        assert isinstance(result, str)
        assert "# Development Plan" in result

    def test_generate_plan_includes_modules_section(self, project_root: Path):
        """generate_plan() includes Modules section."""
        # Arrange
        generator = PlanGenerator(project_root)

        # Act
        result = generator.generate_plan()

        # Assert
        assert "## Modules" in result

    def test_generate_plan_shows_extracted_modules(self, project_root: Path):
        """generate_plan() lists extracted modules in plan."""
        # Arrange
        research_path = project_root / "docs" / "research.md"
        research_path.write_text("- auth: Authentication module")
        generator = PlanGenerator(project_root)

        # Act
        result = generator.generate_plan()

        # Assert
        assert "**auth**: Authentication module" in result

    def test_generate_plan_shows_no_modules_message_when_empty(
        self, project_root: Path
    ):
        """generate_plan() shows 'No modules defined yet' when empty."""
        # Arrange
        research_path = project_root / "docs" / "research.md"
        research_path.write_text("# Empty")
        generator = PlanGenerator(project_root)

        # Act
        result = generator.generate_plan()

        # Assert
        assert "No modules defined yet." in result

    def test_generate_plan_includes_phases_section(self, project_root: Path):
        """generate_plan() includes Phases section with 3 phases."""
        # Arrange
        generator = PlanGenerator(project_root)

        # Act
        result = generator.generate_plan()

        # Assert
        assert "## Phases" in result
        assert "### Phase 1: Foundation" in result
        assert "### Phase 2: Core Features" in result
        assert "### Phase 3: Polish" in result

    def test_generate_plan_creates_plans_directory(self, project_root: Path):
        """generate_plan() creates docs/plans/ if not exists."""
        # Arrange - remove plans dir if exists
        plans_dir = project_root / "docs" / "plans"
        generator = PlanGenerator(project_root)

        # Act
        generator.generate_plan()

        # Assert
        assert plans_dir.exists()

    def test_write_plan_creates_file_in_correct_location(self, project_root: Path):
        """_write_plan() creates file at docs/plans/development-plan.md."""
        # Arrange
        generator = PlanGenerator(project_root)
        content = "# Test Plan"

        # Act
        generator._write_plan(content)

        # Assert
        plan_path = project_root / "docs" / "plans" / "development-plan.md"
        assert plan_path.exists()
        assert plan_path.read_text() == "# Test Plan"

    def test_write_plan_creates_parent_directories(self, project_root: Path):
        """_write_plan() creates parent directories if needed."""
        # Arrange
        generator = PlanGenerator(project_root)
        content = "# Test Plan"

        # Act
        generator._write_plan(content)

        # Assert
        assert (project_root / "docs" / "plans").is_dir()
