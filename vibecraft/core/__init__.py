"""
Core module for Vibecraft Framework.

This module provides the foundational abstractions for the framework:
- Base classes (ABC) for bootstrappers and runners
- Configuration models using Pydantic
- Protocols for structural subtyping
- Exception hierarchy

Example:
    >>> from vibecraft.core import (
    ...     BaseBootstrapper,
    ...     BaseRunner,
    ...     VibecraftConfig,
    ...     ProjectMode,
    ...     VibecraftError
    ... )
"""

# Base classes (ABC) for bootstrappers and runners
from .base_bootstrapper import BaseBootstrapper
from .base_runner import BaseRunner

# Configuration models using Pydantic
from .config import (
    VibecraftConfig,
    ProjectMode,
    ProjectType,
    ModularConfig,
    Module,
)

# Protocols for structural subtyping
from .protocols import Creatable, Listable, Buildable

# Exception hierarchy
from .exceptions import (
    VibecraftError,
    ConfigurationError,
    ModuleError,
    DependencyError,
    CyclicDependencyError,
    MissingDependencyError,
    SecurityError,
    TemplateError,
)

__all__ = [
    # Base classes
    "BaseBootstrapper",
    "BaseRunner",
    # Config models
    "VibecraftConfig",
    "ProjectMode",
    "ProjectType",
    "ModularConfig",
    "Module",
    # Protocols
    "Creatable",
    "Listable",
    "Buildable",
    # Exceptions
    "VibecraftError",
    "ConfigurationError",
    "ModuleError",
    "DependencyError",
    "CyclicDependencyError",
    "MissingDependencyError",
    "SecurityError",
    "TemplateError",
]
