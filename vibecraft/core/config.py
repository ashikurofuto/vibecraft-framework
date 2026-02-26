"""
Configuration models for Vibecraft Framework using Pydantic.

This module defines the data models for project configuration, modes, and modules.
All models use Pydantic v2 for validation and serialization.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ProjectMode(str, Enum):
    """Project mode enumeration.

    Attributes:
        SIMPLE: Simple mode for small projects (linear structure).
        MODULAR: Modular mode for large projects (module-based architecture).
    """

    SIMPLE = "simple"
    MODULAR = "modular"


class ProjectType(str, Enum):
    """Project type enumeration.

    Attributes:
        WEB: Web application.
        API: REST/GraphQL API.
        CLI: Command-line interface tool.
        GAME: Game development project.
        MOBILE: Mobile application.
        DATABASE: Database/database-driven project.
    """

    WEB = "web"
    API = "api"
    CLI = "cli"
    GAME = "game"
    MOBILE = "mobile"
    DATABASE = "database"


class Module(BaseModel):
    """Module model for modular mode.

    Represents a single module in a modular project with its metadata,
    dependencies, and exports.

    Attributes:
        name: Module name (must be valid Python identifier).
        description: Human-readable description.
        status: Module status (planned, in_progress, completed).
        dependencies: List of module names this module depends on.
        exports: List of public exports from this module.
        created_at: Module creation timestamp.
        phases_completed: List of completed development phases.
        metadata: Optional metadata (owner, priority, etc.).

    Example:
        >>> module = Module(
        ...     name="auth",
        ...     description="Authentication module",
        ...     dependencies=["database"]
        ... )
        >>> print(module.name)
        'auth'
    """

    name: str
    description: str = ""
    path: str = ""
    status: str = "planned"
    dependencies: List[str] = Field(default_factory=list)
    exports: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    phases_completed: List[int] = Field(default_factory=list)
    metadata: Optional[dict] = Field(default=None)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate module name is a valid Python identifier.

        Args:
            v: The module name to validate.

        Returns:
            The validated module name.

        Raises:
            ValueError: If name is not a valid Python identifier.
        """
        if not v.isidentifier():
            raise ValueError(
                f"Module name must be a valid Python identifier, got '{v}'"
            )
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of the allowed values.

        Args:
            v: The status to validate.

        Returns:
            The validated status.

        Raises:
            ValueError: If status is not valid.
        """
        allowed = {"planned", "in_progress", "completed", "blocked"}
        if v not in allowed:
            raise ValueError(
                f"Status must be one of {allowed}, got '{v}'"
            )
        return v


class ModularConfig(BaseModel):
    """Configuration for modular mode.

    Contains settings specific to modular project structure.

    Attributes:
        modules_dir: Directory name for modules (default: "modules").
        shared_dir: Directory name for shared code (default: "shared").
        integration_dir: Directory name for integration code (default: "integration").
        modules: List of module names in the project.

    Example:
        >>> config = ModularConfig(modules=["auth", "users"])
        >>> print(config.modules_dir)
        'modules'
    """

    modules_dir: str = "modules"
    shared_dir: str = "shared"
    integration_dir: str = "integration"
    modules: List[str] = Field(default_factory=list)

    @field_validator("modules_dir", "shared_dir", "integration_dir")
    @classmethod
    def validate_dir_name(cls, v: str) -> str:
        """Validate directory names are safe.

        Args:
            v: The directory name to validate.

        Returns:
            The validated directory name.

        Raises:
            ValueError: If directory name contains unsafe characters.
        """
        if not v or ".." in v or v.startswith("/"):
            raise ValueError(f"Invalid directory name: '{v}'")
        return v


class VibecraftConfig(BaseModel):
    """Main configuration model for Vibecraft projects.

    This is the root configuration object that contains all project settings.

    Attributes:
        mode: Project mode (simple or modular).
        version: Vibecraft version (default: "0.4.0").
        project_name: Name of the project.
        project_type: Type of project (web, api, cli, etc.).
        created_at: Project creation timestamp.
        modular: Optional modular-specific configuration.

    Example:
        >>> config = VibecraftConfig(
        ...     mode=ProjectMode.SIMPLE,
        ...     project_name="my-project",
        ...     project_type=ProjectType.WEB
        ... )
        >>> print(config.version)
        '0.4.0'
    """

    model_config = ConfigDict(use_enum_values=True)

    mode: ProjectMode = ProjectMode.SIMPLE
    version: str = "0.4.0"
    project_name: str
    project_type: List[ProjectType] | ProjectType = ProjectType.CLI
    created_at: datetime = Field(default_factory=datetime.now)
    modular: Optional[ModularConfig] = None

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        """Validate project name is not empty.

        Args:
            v: The project name to validate.

        Returns:
            The validated project name.

        Raises:
            ValueError: If project name is empty.
        """
        if not v or not v.strip():
            raise ValueError("Project name cannot be empty")
        return v.strip()

    @field_validator("project_type")
    @classmethod
    def normalize_project_type(cls, v):
        """Normalize project_type to always be a list.

        Args:
            v: The project type(s) to normalize.

        Returns:
            List of ProjectType values.
        """
        if isinstance(v, list):
            return v
        return [v]
