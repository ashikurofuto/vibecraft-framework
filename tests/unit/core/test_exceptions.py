"""
Tests for Vibecraft exception hierarchy.

These tests verify that:
1. All exceptions inherit from VibecraftError
2. Exception hierarchy is correct
3. Exceptions can be raised and caught properly
"""

import pytest

from vibecraft.core.exceptions import (
    VibecraftError,
    ConfigurationError,
    ModuleError,
    DependencyError,
    CyclicDependencyError,
    MissingDependencyError,
    SecurityError,
    TemplateError,
)


class TestExceptionHierarchy:
    """Tests for exception inheritance hierarchy."""

    def test_vibecraft_error_is_base(self):
        """VibecraftError is the base exception."""
        # Assert
        assert issubclass(VibecraftError, Exception)

    def test_configuration_error_inherits_from_vibecraft_error(self):
        """ConfigurationError inherits from VibecraftError."""
        # Assert
        assert issubclass(ConfigurationError, VibecraftError)

    def test_module_error_inherits_from_vibecraft_error(self):
        """ModuleError inherits from VibecraftError."""
        # Assert
        assert issubclass(ModuleError, VibecraftError)

    def test_dependency_error_inherits_from_module_error(self):
        """DependencyError inherits from ModuleError."""
        # Assert
        assert issubclass(DependencyError, ModuleError)
        assert issubclass(DependencyError, VibecraftError)

    def test_cyclic_dependency_error_inherits_from_dependency_error(self):
        """CyclicDependencyError inherits from DependencyError."""
        # Assert
        assert issubclass(CyclicDependencyError, DependencyError)
        assert issubclass(CyclicDependencyError, ModuleError)
        assert issubclass(CyclicDependencyError, VibecraftError)

    def test_missing_dependency_error_inherits_from_dependency_error(self):
        """MissingDependencyError inherits from DependencyError."""
        # Assert
        assert issubclass(MissingDependencyError, DependencyError)
        assert issubclass(MissingDependencyError, ModuleError)
        assert issubclass(MissingDependencyError, VibecraftError)

    def test_security_error_inherits_from_module_error(self):
        """SecurityError inherits from ModuleError."""
        # Assert
        assert issubclass(SecurityError, ModuleError)
        assert issubclass(SecurityError, VibecraftError)

    def test_template_error_inherits_from_vibecraft_error(self):
        """TemplateError inherits from VibecraftError."""
        # Assert
        assert issubclass(TemplateError, VibecraftError)


class TestExceptionBehavior:
    """Tests for exception behavior and usage."""

    def test_vibecraft_error_message(self):
        """VibecraftError stores and returns message."""
        # Arrange
        message = "Test error message"

        # Act
        error = VibecraftError(message)

        # Assert
        assert str(error) == message
        assert error.message == message

    def test_vibecraft_error_with_details(self):
        """VibecraftError includes details when provided."""
        # Arrange
        message = "Test error"
        details = "Additional context"

        # Act
        error = VibecraftError(message, details)

        # Assert
        assert "Additional context" in str(error)
        assert error.details == details

    def test_configuration_error_can_be_raised(self):
        """ConfigurationError can be raised and caught."""
        # Act & Assert
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Invalid configuration")

        assert "Invalid configuration" in str(exc_info.value)

    def test_module_error_can_be_raised(self):
        """ModuleError can be raised and caught."""
        # Act & Assert
        with pytest.raises(ModuleError) as exc_info:
            raise ModuleError("Module not found")

        assert "Module not found" in str(exc_info.value)

    def test_dependency_error_can_be_raised(self):
        """DependencyError can be raised and caught."""
        # Act & Assert
        with pytest.raises(DependencyError) as exc_info:
            raise DependencyError("Missing dependency")

        assert "Missing dependency" in str(exc_info.value)

    def test_cyclic_dependency_error_can_be_raised(self):
        """CyclicDependencyError can be raised and caught."""
        # Act & Assert
        with pytest.raises(CyclicDependencyError) as exc_info:
            raise CyclicDependencyError("Circular dependency detected")

        assert "Circular dependency detected" in str(exc_info.value)

    def test_missing_dependency_error_can_be_raised(self):
        """MissingDependencyError can be raised and caught."""
        # Act & Assert
        with pytest.raises(MissingDependencyError) as exc_info:
            raise MissingDependencyError("Required dependency not found")

        assert "Required dependency not found" in str(exc_info.value)

    def test_security_error_can_be_raised(self):
        """SecurityError can be raised and caught."""
        # Act & Assert
        with pytest.raises(SecurityError) as exc_info:
            raise SecurityError("Path traversal detected")

        assert "Path traversal detected" in str(exc_info.value)

    def test_template_error_can_be_raised(self):
        """TemplateError can be raised and caught."""
        # Act & Assert
        with pytest.raises(TemplateError) as exc_info:
            raise TemplateError("Template rendering failed")

        assert "Template rendering failed" in str(exc_info.value)


class TestExceptionCatching:
    """Tests for exception catching with inheritance."""

    def test_catch_dependency_error_as_module_error(self):
        """DependencyError can be caught as ModuleError."""
        # Act & Assert
        with pytest.raises(ModuleError):
            raise DependencyError("Dependency issue")

    def test_catch_cyclic_dependency_as_dependency_error(self):
        """CyclicDependencyError can be caught as DependencyError."""
        # Act & Assert
        with pytest.raises(DependencyError):
            raise CyclicDependencyError("Cycle detected")

    def test_catch_all_module_errors(self):
        """All module-related errors can be caught as ModuleError."""
        # Act & Assert
        with pytest.raises(ModuleError):
            raise CyclicDependencyError("Cycle")

    def test_catch_all_vibecraft_errors(self):
        """All Vibecraft errors can be caught as VibecraftError."""
        # Act & Assert
        with pytest.raises(VibecraftError):
            raise TemplateError("Template issue")
