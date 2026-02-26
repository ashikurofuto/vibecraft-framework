"""
Configuration migration utilities for Vibecraft Framework.

This module handles migration of configuration between different
versions of Vibecraft, ensuring backward compatibility.

Example:
    >>> from vibecraft.core.migrations import ConfigMigrator
    >>> migrator = ConfigMigrator()
    >>> old_config = {"project_name": "test"}
    >>> new_config = migrator.migrate(old_config, "0.3.0", "0.4.0")
    >>> print(new_config["mode"])
    'simple'
"""

from typing import Dict, Any


class ConfigMigrator:
    """Migrates configuration between Vibecraft versions.

    This class provides methods to migrate configuration dictionaries
    from older versions to newer versions, handling field additions,
    removals, and transformations.

    Example:
        >>> migrator = ConfigMigrator()
        >>> config = {"project_name": "My Project"}
        >>> migrated = migrator.migrate(config, "0.3.0", "0.4.0")
    """

    def migrate(
        self,
        config: Dict[str, Any],
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """Migrate configuration between versions.

        Args:
            config: The configuration dictionary to migrate.
            from_version: The source version (e.g., "0.3.0").
            to_version: The target version (e.g., "0.4.0").

        Returns:
            The migrated configuration dictionary.

        Raises:
            ValueError: If config is None.

        Example:
            >>> migrator = ConfigMigrator()
            >>> config = {"project_name": "test"}
            >>> migrated = migrator.migrate(config, "0.3.0", "0.4.0")
        """
        if config is None:
            return {}

        # Handle specific version migrations
        if from_version == "0.3.0" and to_version == "0.4.0":
            return self._migrate_0_3_to_0_4(config)

        # Unknown version pairs return config unchanged
        return config.copy()

    def _migrate_0_3_to_0_4(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate configuration from v0.3.0 to v0.4.0.

        This migration adds the 'mode' and 'version' fields if they
        are missing or falsy.

        Args:
            config: The v0.3.0 configuration dictionary.

        Returns:
            The migrated v0.4.0 configuration dictionary.

        Example:
            >>> migrator = ConfigMigrator()
            >>> old = {"project_name": "Legacy Project"}
            >>> new = migrator._migrate_0_3_to_0_4(old)
            >>> new["mode"]
            'simple'
            >>> new["version"]
            '0.4.0'
        """
        migrated = config.copy()

        # Add mode if missing or falsy (None, empty string, etc.)
        if not migrated.get("mode"):
            migrated["mode"] = "simple"

        # Add version if missing
        if "version" not in migrated:
            migrated["version"] = "0.4.0"

        return migrated
