"""
Modular mode bootstrapper for Vibecraft Framework.

This module provides the ModularBootstrapper class for initializing
modular mode projects with module-based architecture.
"""

from pathlib import Path
from typing import Any

from vibecraft.core.base_bootstrapper import BaseBootstrapper
from vibecraft.core.config import VibecraftConfig


class ModularBootstrapper(BaseBootstrapper):
    """Bootstrapper for modular mode projects.

    Modular mode is designed for large projects that benefit from
    a module-based architecture with explicit dependencies.

    Example:
        >>> from vibecraft.core.config import VibecraftConfig, ProjectMode
        >>> config = VibecraftConfig(
        ...     project_name="My SaaS",
        ...     mode=ProjectMode.MODULAR
        ... )
        >>> bootstrapper = ModularBootstrapper(Path("/project"), config)
        >>> bootstrapper.run()
    """

    def __init__(
        self,
        project_root: Path,
        config: VibecraftConfig,
        **kwargs: Any
    ) -> None:
        """Initialize the modular bootstrapper.

        Args:
            project_root: Root directory of the project.
            config: Vibecraft configuration object.
            **kwargs: Additional arguments (ignored for now).
        """
        super().__init__(project_root, config)
        # Store kwargs for potential future use
        self._kwargs = kwargs

    def run(self) -> None:
        """Execute the modular bootstrapping process.

        Creates the modular project structure with:
        - modules/ directory for module packages
        - shared/ directory for shared code
        - integration/ directory for integration layer
        - .vibecraft/modules-registry.json for module registry
        """
        # Create base directories
        modules_dir = self.project_root / self.config.modular.modules_dir if self.config.modular else self.project_root / "modules"
        shared_dir = self.project_root / self.config.modular.shared_dir if self.config.modular else self.project_root / "shared"
        integration_dir = self.project_root / self.config.modular.integration_dir if self.config.modular else self.project_root / "integration"

        modules_dir.mkdir(parents=True, exist_ok=True)
        shared_dir.mkdir(parents=True, exist_ok=True)
        integration_dir.mkdir(parents=True, exist_ok=True)

        # Create .vibecraft structure
        vibecraft_dir = self.project_root / ".vibecraft"
        vibecraft_dir.mkdir(parents=True, exist_ok=True)
        (vibecraft_dir / "agents").mkdir(exist_ok=True)
        (vibecraft_dir / "skills").mkdir(exist_ok=True)
        (vibecraft_dir / "prompts").mkdir(exist_ok=True)
        (vibecraft_dir / "snapshots").mkdir(exist_ok=True)

        # Create docs structure
        docs_dir = self.project_root / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        (docs_dir / "design").mkdir(exist_ok=True)
        (docs_dir / "plans").mkdir(exist_ok=True)

        # Create src/tests structure
        src_tests_dir = self.project_root / "src" / "tests"
        src_tests_dir.mkdir(parents=True, exist_ok=True)

        # Create modules registry
        self._create_modules_registry()

        # Create manifest
        self._create_manifest()

    def validate(self) -> list[str]:
        """Validate inputs before running.

        Returns:
            List of error messages (empty if validation passes).
        """
        errors: list[str] = []

        # Validate project_root is writable
        if not self.project_root.exists():
            try:
                self.project_root.mkdir(parents=True)
            except OSError as e:
                errors.append(f"Cannot create project root: {e}")

        # Validate config
        if not self.config.project_name:
            errors.append("Project name is required")

        return errors

    def _create_modules_registry(self) -> None:
        """Create empty modules registry."""
        import json
        from typing import Any

        registry: dict[str, Any] = {
            "modules": [],
            "dependencies": {},
            "build_order": [],
        }

        registry_path = self.project_root / ".vibecraft" / "modules-registry.json"
        registry_path.write_text(
            json.dumps(registry, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def _create_manifest(self) -> None:
        """Create manifest.json with mode and version."""
        import json
        from datetime import datetime, timezone

        manifest = {
            "mode": "modular",
            "version": "0.4.0",
            "project_name": self.config.project_name,
            "project_type": [pt.value if hasattr(pt, 'value') else str(pt) for pt in self.config.project_type] if isinstance(self.config.project_type, list) else [self.config.project_type],
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "stack": {},
            "agents": [],
            "skills": [],
            "current_phase": "research",
            "phases": ["research", "design", "plan", "implement", "review"],
            "phases_completed": [],
        }

        manifest_path = self.project_root / ".vibecraft" / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
