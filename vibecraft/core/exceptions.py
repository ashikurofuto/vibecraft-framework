"""
Custom exceptions for Vibecraft Framework.

Exception hierarchy:
    VibecraftError (base)
    ├── ConfigurationError
    ├── ModuleError
    │   ├── DependencyError
    │   │   ├── CyclicDependencyError
    │   │   └── MissingDependencyError
    │   └── SecurityError
    └── TemplateError
"""


class VibecraftError(Exception):
    """Base exception for all Vibecraft errors."""

    def __init__(self, message: str, details: str | None = None):
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class ConfigurationError(VibecraftError):
    """Configuration-related errors."""

    pass


class ModuleError(VibecraftError):
    """Module-related errors."""

    pass


class DependencyError(ModuleError):
    """Dependency-related errors."""

    pass


class CyclicDependencyError(DependencyError):
    """Cyclic dependency detected."""

    pass


class MissingDependencyError(DependencyError):
    """Required dependency not found."""

    pass


class SecurityError(ModuleError):
    """Security-related errors (e.g., path traversal)."""

    pass


class TemplateError(VibecraftError):
    """Template rendering errors."""

    pass
