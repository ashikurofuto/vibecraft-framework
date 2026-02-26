"""
Tests for Vibecraft configuration models.

These tests verify that:
1. VibecraftConfig validates input correctly
2. Module name validation works
3. ProjectMode enum values are correct
4. ModularConfig validates directory names
"""

import pytest
from datetime import datetime

from vibecraft.core.config import (
    VibecraftConfig,
    ProjectMode,
    ProjectType,
    ModularConfig,
    Module,
)


class TestProjectModeEnum:
    """Tests for ProjectMode enumeration."""

    def test_project_mode_values(self):
        """ProjectMode has correct values."""
        # Assert
        assert ProjectMode.SIMPLE.value == "simple"
        assert ProjectMode.MODULAR.value == "modular"

    def test_project_mode_from_string(self):
        """ProjectMode can be created from string."""
        # Act
        simple_mode = ProjectMode("simple")
        modular_mode = ProjectMode("modular")

        # Assert
        assert simple_mode == ProjectMode.SIMPLE
        assert modular_mode == ProjectMode.MODULAR

    def test_project_mode_invalid_value(self):
        """ProjectMode raises ValueError for invalid value."""
        # Act & Assert
        with pytest.raises(ValueError):
            ProjectMode("invalid_mode")


class TestProjectTypeEnum:
    """Tests for ProjectType enumeration."""

    def test_project_type_values(self):
        """ProjectType has correct values."""
        # Assert
        assert ProjectType.WEB.value == "web"
        assert ProjectType.API.value == "api"
        assert ProjectType.CLI.value == "cli"
        assert ProjectType.GAME.value == "game"
        assert ProjectType.MOBILE.value == "mobile"
        assert ProjectType.DATABASE.value == "database"


class TestVibecraftConfig:
    """Tests for VibecraftConfig model."""

    def test_vibecraft_config_minimal(self):
        """VibecraftConfig can be created with minimal fields."""
        # Act
        config = VibecraftConfig(
            project_name="Test Project"
        )

        # Assert
        assert config.project_name == "Test Project"
        assert config.mode == "simple"  # default
        assert config.version == "0.4.0"  # default
        assert isinstance(config.created_at, datetime)

    def test_vibecraft_config_full(self):
        """VibecraftConfig can be created with all fields."""
        # Arrange
        created_at = datetime(2026, 2, 26, 12, 0, 0)

        # Act
        config = VibecraftConfig(
            mode=ProjectMode.MODULAR,
            version="0.4.0",
            project_name="My SaaS Platform",
            project_type=ProjectType.WEB,
            created_at=created_at,
        )

        # Assert
        assert config.mode == "modular"
        assert config.project_name == "My SaaS Platform"
        assert config.project_type == [ProjectType.WEB]

    def test_vibecraft_config_validation_empty_name(self):
        """VibecraftConfig rejects empty project name."""
        # Act & Assert
        with pytest.raises(ValueError, match="cannot be empty"):
            VibecraftConfig(project_name="")

    def test_vibecraft_config_validation_whitespace_name(self):
        """VibecraftConfig trims whitespace from project name."""
        # Act
        config = VibecraftConfig(project_name="  Test Project  ")

        # Assert
        assert config.project_name == "Test Project"

    def test_vibecraft_config_multiple_project_types(self):
        """VibecraftConfig accepts multiple project types."""
        # Act
        config = VibecraftConfig(
            project_name="Multi Project",
            project_type=[ProjectType.WEB, ProjectType.API],
        )

        # Assert
        assert len(config.project_type) == 2
        assert ProjectType.WEB in config.project_type
        assert ProjectType.API in config.project_type


class TestModularConfig:
    """Tests for ModularConfig model."""

    def test_modular_config_defaults(self):
        """ModularConfig has correct default values."""
        # Act
        config = ModularConfig()

        # Assert
        assert config.modules_dir == "modules"
        assert config.shared_dir == "shared"
        assert config.integration_dir == "integration"
        assert config.modules == []

    def test_modular_config_custom_values(self):
        """ModularConfig accepts custom values."""
        # Act
        config = ModularConfig(
            modules_dir="pkg",
            shared_dir="common",
            integration_dir="int",
            modules=["auth", "users"],
        )

        # Assert
        assert config.modules_dir == "pkg"
        assert config.modules == ["auth", "users"]

    def test_modular_config_invalid_dir_name(self):
        """ModularConfig rejects invalid directory names."""
        # Act & Assert - path traversal
        with pytest.raises(ValueError, match="Invalid directory name"):
            ModularConfig(modules_dir="../evil")

    def test_modular_config_invalid_dir_name_slash(self):
        """ModularConfig rejects directory names starting with slash."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid directory name"):
            ModularConfig(modules_dir="/absolute/path")


class TestModule:
    """Tests for Module model."""

    def test_module_minimal(self):
        """Module can be created with minimal fields."""
        # Act
        module = Module(name="auth")

        # Assert
        assert module.name == "auth"
        assert module.description == ""
        assert module.status == "planned"
        assert module.dependencies == []
        assert module.exports == []

    def test_module_full(self):
        """Module can be created with all fields."""
        # Act
        module = Module(
            name="users",
            description="User management module",
            status="in_progress",
            dependencies=["auth", "database"],
            exports=["UserService", "create_user"],
            phases_completed=[1, 2],
        )

        # Assert
        assert module.name == "users"
        assert module.description == "User management module"
        assert module.status == "in_progress"
        assert module.dependencies == ["auth", "database"]
        assert module.exports == ["UserService", "create_user"]

    def test_module_name_validation_invalid_identifier(self):
        """Module rejects invalid Python identifiers."""
        # Act & Assert
        with pytest.raises(ValueError, match="valid Python identifier"):
            Module(name="my-module")  # hyphen not allowed

    def test_module_name_validation_starts_with_number(self):
        """Module rejects names starting with number."""
        # Act & Assert
        with pytest.raises(ValueError, match="valid Python identifier"):
            Module(name="123auth")

    def test_module_name_validation_valid(self):
        """Module accepts valid Python identifiers."""
        # Act
        module1 = Module(name="auth")
        module2 = Module(name="user_service")
        module3 = Module(name="Auth")

        # Assert
        assert module1.name == "auth"
        assert module2.name == "user_service"
        assert module3.name == "Auth"

    def test_module_status_validation(self):
        """Module validates status values."""
        # Act - valid statuses
        module1 = Module(name="m1", status="planned")
        module2 = Module(name="m2", status="in_progress")
        module3 = Module(name="m3", status="completed")
        module4 = Module(name="m4", status="blocked")

        # Assert
        assert module1.status == "planned"
        assert module2.status == "in_progress"
        assert module3.status == "completed"
        assert module4.status == "blocked"

    def test_module_status_validation_invalid(self):
        """Module rejects invalid status values."""
        # Act & Assert
        with pytest.raises(ValueError, match="Status must be one of"):
            Module(name="test", status="invalid_status")

    def test_module_metadata(self):
        """Module accepts optional metadata."""
        # Act
        module = Module(
            name="auth",
            metadata={
                "owner": "backend-team",
                "priority": "high",
                "estimated_days": 5,
            },
        )

        # Assert
        assert module.metadata is not None
        assert module.metadata["owner"] == "backend-team"
        assert module.metadata["priority"] == "high"
