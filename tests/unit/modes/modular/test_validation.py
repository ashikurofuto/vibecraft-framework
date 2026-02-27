"""
Tests for ModuleValidator module.

Tests verify that ModuleValidator properly validates module names
for Python identifier compliance and reserved name conflicts.
"""

import pytest

from vibecraft.modes.modular.validation import ModuleValidator
from vibecraft.core.exceptions import ModuleError


class TestModuleValidatorInit:
    """Tests for ModuleValidator initialization."""

    def test_init_creates_validator(self):
        """ModuleValidator can be instantiated."""
        # Act
        validator = ModuleValidator()

        # Assert
        assert validator is not None

    def test_init_has_reserved_names(self):
        """ModuleValidator has predefined reserved names."""
        # Act
        validator = ModuleValidator()

        # Assert
        assert len(validator.RESERVED_NAMES) > 0
        assert "core" in validator.RESERVED_NAMES
        assert "vibecraft" in validator.RESERVED_NAMES


class TestValidateModuleNameValid:
    """Tests for valid module name acceptance."""

    @pytest.fixture
    def validator(self) -> ModuleValidator:
        """Create ModuleValidator instance."""
        return ModuleValidator()

    @pytest.mark.parametrize("valid_name", [
        "auth",
        "api",
        "database",
        "user_service",
        "Auth",
        "MyModule",
        "_private",
        "__dunder",
        "module123",
        "v2",
        "api_v2",
        "test_module",
    ])
    def test_accepts_valid_python_identifiers(self, validator, valid_name):
        """validate_module_name accepts valid Python identifiers: {valid_name}."""
        # Act & Assert - should not raise
        validator.validate_module_name(valid_name)

    def test_accepts_underscore_prefix(self, validator):
        """validate_module_name accepts names starting with underscore."""
        # Act & Assert
        validator.validate_module_name("_internal")
        validator.validate_module_name("__private")

    def test_accepts_numbers_after_first_char(self, validator):
        """validate_module_name accepts numbers after first character."""
        # Act & Assert
        validator.validate_module_name("module1")
        validator.validate_module_name("api2")
        validator.validate_module_name("v123")


class TestValidateModuleNameEmpty:
    """Tests for empty name rejection."""

    @pytest.fixture
    def validator(self) -> ModuleValidator:
        """Create ModuleValidator instance."""
        return ModuleValidator()

    def test_rejects_empty_string(self, validator):
        """validate_module_name rejects empty string."""
        # Act & Assert
        with pytest.raises(ModuleError, match="cannot be empty"):
            validator.validate_module_name("")

    def test_error_message_mentions_empty(self, validator):
        """Error message mentions 'empty' for empty name."""
        # Act & Assert
        with pytest.raises(ModuleError) as exc_info:
            validator.validate_module_name("")

        assert "empty" in str(exc_info.value).lower()


class TestValidateModuleNameInvalidIdentifier:
    """Tests for invalid Python identifier rejection."""

    @pytest.fixture
    def validator(self) -> ModuleValidator:
        """Create ModuleValidator instance."""
        return ModuleValidator()

    @pytest.mark.parametrize("invalid_name", [
        "my-module",      # hyphen
        "module.name",    # dot
        "api-v2",         # hyphen
        "user-service",   # hyphen
        "module!",        # exclamation
        "module@",        # at sign
        "module#",        # hash
        "module$",        # dollar
        "module%",        # percent
        "module&",        # ampersand
        "module*",        # asterisk
        "module+",        # plus
        "module=",        # equals
        "module?",        # question mark
        "module/",        # slash
        "module\\",       # backslash
        "module|",        # pipe
        "module;",        # semicolon
        "module:",        # colon
        "module,",        # comma
        "module<",        # less than
        "module>",        # greater than
        "module[",        # bracket
        "module]",        # bracket
        "module{",        # brace
        "module}",        # brace
        "module(",        # paren
        "module)",        # paren
        "module`",        # backtick
        "module~",        # tilde
    ])
    def test_rejects_invalid_python_identifiers(
        self, validator, invalid_name
    ):
        """validate_module_name rejects invalid identifier: {invalid_name}."""
        # Act & Assert
        with pytest.raises(ModuleError, match="valid Python identifier"):
            validator.validate_module_name(invalid_name)

    @pytest.mark.parametrize("invalid_name", [
        "123module",      # starts with number
        "1api",           # starts with number
        "9modules",       # starts with number
    ])
    def test_rejects_names_starting_with_number(
        self, validator, invalid_name
    ):
        """validate_module_name rejects names starting with number: {invalid_name}."""
        # Act & Assert
        with pytest.raises(ModuleError, match="valid Python identifier"):
            validator.validate_module_name(invalid_name)

    def test_rejects_names_with_spaces(self, validator):
        """validate_module_name rejects names with spaces."""
        # Act & Assert
        with pytest.raises(ModuleError, match="valid Python identifier"):
            validator.validate_module_name("my module")

    def test_rejects_names_with_newlines(self, validator):
        """validate_module_name rejects names with newlines."""
        # Act & Assert
        with pytest.raises(ModuleError, match="valid Python identifier"):
            validator.validate_module_name("module\nname")

    def test_rejects_names_with_tabs(self, validator):
        """validate_module_name rejects names with tabs."""
        # Act & Assert
        with pytest.raises(ModuleError, match="valid Python identifier"):
            validator.validate_module_name("module\tname")

    def test_error_message_includes_module_name(self, validator):
        """Error message includes the invalid module name."""
        # Act & Assert
        with pytest.raises(ModuleError) as exc_info:
            validator.validate_module_name("my-module")

        assert "my-module" in str(exc_info.value)


class TestValidateModuleNameReserved:
    """Tests for reserved name rejection."""

    @pytest.fixture
    def validator(self) -> ModuleValidator:
        """Create ModuleValidator instance."""
        return ModuleValidator()

    @pytest.mark.parametrize("reserved_name", [
        "core",
        "vibecraft",
        "test",
        "shared",
        "integration",
    ])
    def test_rejects_reserved_names(self, validator, reserved_name):
        """validate_module_name rejects reserved name: {reserved_name}."""
        # Act & Assert
        with pytest.raises(ModuleError, match="reserved"):
            validator.validate_module_name(reserved_name)

    def test_error_message_includes_reserved_name(self, validator):
        """Error message includes the reserved name."""
        # Act & Assert
        with pytest.raises(ModuleError) as exc_info:
            validator.validate_module_name("core")

        assert "core" in str(exc_info.value)

    def test_error_message_mentions_reserved(self, validator):
        """Error message mentions 'reserved'."""
        # Act & Assert
        with pytest.raises(ModuleError) as exc_info:
            validator.validate_module_name("vibecraft")

        assert "reserved" in str(exc_info.value).lower()

    def test_case_sensitive_reserved(self, validator):
        """Reserved name check is case-sensitive."""
        # Act & Assert - different case should be accepted
        validator.validate_module_name("Core")
        validator.validate_module_name("Vibecraft")
        validator.validate_module_name("TEST")


class TestIsValidIdentifier:
    """Tests for _is_valid_identifier helper method."""

    @pytest.fixture
    def validator(self) -> ModuleValidator:
        """Create ModuleValidator instance."""
        return ModuleValidator()

    @pytest.mark.parametrize("name", [
        "auth",
        "api",
        "user_service",
        "Auth",
        "_private",
        "__dunder",
        "module123",
        "v2",
    ])
    def test_returns_true_for_valid_identifiers(self, validator, name):
        """_is_valid_identifier returns True for valid identifiers."""
        # Act
        result = validator._is_valid_identifier(name)

        # Assert
        assert result is True

    @pytest.mark.parametrize("name", [
        "my-module",
        "module.name",
        "123module",
        "module!",
        "my module",
        "",
    ])
    def test_returns_false_for_invalid_identifiers(self, validator, name):
        """_is_valid_identifier returns False for invalid identifiers."""
        # Act
        result = validator._is_valid_identifier(name)

        # Assert
        assert result is False


class TestIsReservedName:
    """Tests for _is_reserved_name helper method."""

    @pytest.fixture
    def validator(self) -> ModuleValidator:
        """Create ModuleValidator instance."""
        return ModuleValidator()

    @pytest.mark.parametrize("name", [
        "core",
        "vibecraft",
        "test",
        "shared",
        "integration",
    ])
    def test_returns_true_for_reserved(self, validator, name):
        """_is_reserved_name returns True for reserved names."""
        # Act
        result = validator._is_reserved_name(name)

        # Assert
        assert result is True

    @pytest.mark.parametrize("name", [
        "auth",
        "api",
        "database",
        "mycore",       # Similar but not exact
        "test_module",  # Contains but not exact
        "Core",         # Different case
    ])
    def test_returns_false_for_non_reserved(self, validator, name):
        """_is_reserved_name returns False for non-reserved names."""
        # Act
        result = validator._is_reserved_name(name)

        # Assert
        assert result is False


class TestModuleValidatorEdgeCases:
    """Tests for edge cases and special scenarios."""

    @pytest.fixture
    def validator(self) -> ModuleValidator:
        """Create ModuleValidator instance."""
        return ModuleValidator()

    def test_handles_very_long_name(self, validator):
        """validate_module_name handles very long names."""
        # Arrange
        long_name = "a" * 1000

        # Act & Assert - should be valid (just long)
        validator.validate_module_name(long_name)

    def test_handles_unicode_characters(self, validator):
        """ModuleValidator handles Unicode characters (rejects as invalid identifier).
        
        Note: While Python 3 allows Unicode in identifiers, the ModuleValidator
        uses a strict ASCII-only regex pattern for compatibility.
        """
        # Act & Assert - Unicode is rejected by the strict regex
        with pytest.raises(ModuleError, match="valid Python identifier"):
            validator.validate_module_name("модуль")
        
        with pytest.raises(ModuleError, match="valid Python identifier"):
            validator.validate_module_name("模块")

    def test_handles_mixed_case(self, validator):
        """validate_module_name handles mixed case names."""
        # Act & Assert
        validator.validate_module_name("MyModule")
        validator.validate_module_name("myModule")
        validator.validate_module_name("MYMODULE")
        validator.validate_module_name("my_module")

    def test_handles_single_character(self, validator):
        """validate_module_name handles single character names."""
        # Act & Assert
        validator.validate_module_name("a")
        validator.validate_module_name("x")
        validator.validate_module_name("_")

    def test_rejects_single_invalid_character(self, validator):
        """validate_module_name rejects single invalid character."""
        # Act & Assert
        with pytest.raises(ModuleError):
            validator.validate_module_name("-")

    def test_whitespace_only_name(self, validator):
        """validate_module_name rejects whitespace-only names."""
        # Act & Assert
        with pytest.raises(ModuleError):
            validator.validate_module_name("   ")

    def test_null_character_in_name(self, validator):
        """validate_module_name rejects null character."""
        # Act & Assert
        with pytest.raises(ModuleError):
            validator.validate_module_name("mod\x00ule")
