"""
Tests for Vibecraft ConfigMigrator.

Tests verify configuration migration between versions.
"""

import pytest
from vibecraft.core.migrations import ConfigMigrator


class TestConfigMigrator:
    """Tests for ConfigMigrator class."""

    def test_migrate_none_config_returns_empty_dict(self):
        """migrate() returns empty dict when config is None."""
        # Arrange
        migrator = ConfigMigrator()

        # Act
        result = migrator.migrate(None, "0.3.0", "0.4.0")

        # Assert
        assert result == {}

    def test_migrate_0_3_to_0_4_adds_mode_field(self):
        """migrate() adds 'mode': 'simple' when migrating 0.3.0 to 0.4.0."""
        # Arrange
        migrator = ConfigMigrator()
        config = {"project_name": "Legacy Project"}

        # Act
        result = migrator.migrate(config, "0.3.0", "0.4.0")

        # Assert
        assert result["mode"] == "simple"
        assert result["project_name"] == "Legacy Project"

    def test_migrate_0_3_to_0_4_adds_version_field(self):
        """migrate() adds 'version': '0.4.0' when migrating 0.3.0 to 0.4.0."""
        # Arrange
        migrator = ConfigMigrator()
        config = {"project_name": "Legacy Project"}

        # Act
        result = migrator.migrate(config, "0.3.0", "0.4.0")

        # Assert
        assert result["version"] == "0.4.0"

    def test_migrate_0_3_to_0_4_preserves_existing_fields(self):
        """migrate() preserves all existing config fields."""
        # Arrange
        migrator = ConfigMigrator()
        config = {
            "project_name": "Test",
            "stack": {"lang": "Python"},
            "agents": ["researcher"],
        }

        # Act
        result = migrator.migrate(config, "0.3.0", "0.4.0")

        # Assert
        assert result["project_name"] == "Test"
        assert result["stack"] == {"lang": "Python"}
        assert result["agents"] == ["researcher"]

    def test_migrate_0_3_to_0_4_does_not_overwrite_existing_mode(self):
        """migrate() keeps existing mode field if present."""
        # Arrange
        migrator = ConfigMigrator()
        config = {"project_name": "Test", "mode": "modular"}

        # Act
        result = migrator.migrate(config, "0.3.0", "0.4.0")

        # Assert
        assert result["mode"] == "modular"

    def test_migrate_0_3_to_0_4_does_not_overwrite_existing_version(self):
        """migrate() keeps existing version field if present."""
        # Arrange
        migrator = ConfigMigrator()
        config = {"project_name": "Test", "version": "0.3.0"}

        # Act
        result = migrator.migrate(config, "0.3.0", "0.4.0")

        # Assert
        assert result["version"] == "0.3.0"

    def test_migrate_0_3_to_0_4_replaces_falsy_mode(self):
        """migrate() replaces falsy mode (empty string, None) with 'simple'."""
        # Arrange
        migrator = ConfigMigrator()

        # Act - empty string mode
        result_empty = migrator.migrate(
            {"project_name": "Test", "mode": ""},
            "0.3.0", "0.4.0"
        )
        # Act - None mode
        result_none = migrator.migrate(
            {"project_name": "Test", "mode": None},
            "0.3.0", "0.4.0"
        )

        # Assert
        assert result_empty["mode"] == "simple"
        assert result_none["mode"] == "simple"

    def test_migrate_unknown_version_pair_returns_copy(self):
        """migrate() returns unchanged copy for unknown version pairs."""
        # Arrange
        migrator = ConfigMigrator()
        config = {"project_name": "Test"}

        # Act - different from_version
        result1 = migrator.migrate(config, "0.2.0", "0.4.0")
        # Act - different to_version
        result2 = migrator.migrate(config, "0.3.0", "0.5.0")

        # Assert - should be copy, not same object
        assert result1 == config
        assert result1 is not config
        assert result2 == config
        assert result2 is not config

    def test_migrate_returns_copy_not_original(self):
        """migrate() returns new dict, does not modify original."""
        # Arrange
        migrator = ConfigMigrator()
        config = {"project_name": "Test"}

        # Act
        result = migrator.migrate(config, "0.3.0", "0.4.0")

        # Assert - original unchanged
        assert "mode" not in config
        assert "mode" in result

    def test_migrate_0_3_to_0_4_complete_migration(self):
        """migrate() performs complete 0.3.0 to 0.4.0 migration."""
        # Arrange
        migrator = ConfigMigrator()
        config = {
            "project_name": "My Project",
            "stack": {"lang": "Python"},
        }

        # Act
        result = migrator.migrate(config, "0.3.0", "0.4.0")

        # Assert - all expected fields present
        assert result["project_name"] == "My Project"
        assert result["stack"] == {"lang": "Python"}
        assert result["mode"] == "simple"
        assert result["version"] == "0.4.0"

    def test_internal_migrate_0_3_to_0_4_method(self):
        """_migrate_0_3_to_0_4() adds mode and version fields."""
        # Arrange
        migrator = ConfigMigrator()
        config = {"project_name": "Test"}

        # Act
        result = migrator._migrate_0_3_to_0_4(config)

        # Assert
        assert result["mode"] == "simple"
        assert result["version"] == "0.4.0"
        assert result["project_name"] == "Test"
