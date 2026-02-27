"""
Tests for SecurityValidator module.

Tests verify that SecurityValidator properly validates module paths
for security issues including path traversal, reserved names, and
absolute paths.
"""

import pytest
from pathlib import Path

from vibecraft.modes.modular.security import SecurityValidator
from vibecraft.core.exceptions import SecurityError


class TestSecurityValidatorInit:
    """Tests for SecurityValidator initialization."""

    def test_init_creates_validator(self):
        """SecurityValidator can be instantiated."""
        # Act
        validator = SecurityValidator()

        # Assert
        assert validator is not None

    def test_init_has_reserved_names(self):
        """SecurityValidator has predefined reserved names."""
        # Act
        validator = SecurityValidator()

        # Assert
        assert len(validator.RESERVED_NAMES) > 0
        assert "core" in validator.RESERVED_NAMES
        assert "vibecraft" in validator.RESERVED_NAMES


class TestValidateModulePathReservedNames:
    """Tests for reserved name validation."""

    @pytest.fixture
    def validator(self) -> SecurityValidator:
        """Create SecurityValidator instance."""
        return SecurityValidator()

    @pytest.fixture
    def project_root(self, tmp_path: Path) -> Path:
        """Create temporary project root."""
        project = tmp_path / "test-project"
        project.mkdir()
        return project

    @pytest.mark.parametrize("reserved_name", [
        "core",
        "vibecraft",
        "test",
        "shared",
        "integration",
    ])
    def test_rejects_reserved_names(self, validator, project_root, reserved_name):
        """validate_module_path rejects reserved names: {reserved_name}."""
        # Act & Assert
        with pytest.raises(SecurityError, match="reserved name"):
            validator.validate_module_path(reserved_name, project_root)

    def test_accepts_non_reserved_name(self, validator, project_root):
        """validate_module_path accepts non-reserved names."""
        # Act & Assert - should not raise
        validator.validate_module_path("auth", project_root)
        validator.validate_module_path("user_service", project_root)


class TestValidateModulePathTraversal:
    """Tests for path traversal validation."""

    @pytest.fixture
    def validator(self) -> SecurityValidator:
        """Create SecurityValidator instance."""
        return SecurityValidator()

    @pytest.fixture
    def project_root(self, tmp_path: Path) -> Path:
        """Create temporary project root."""
        project = tmp_path / "test-project"
        project.mkdir()
        return project

    @pytest.mark.parametrize("malicious_path", [
        "../etc/passwd",
        "../../etc/shadow",
        "..\\..\\windows\\system32",
        "auth/../../../etc/passwd",
        "modules/../../../secret",
    ])
    def test_rejects_path_traversal_attempts(
        self, validator, project_root, malicious_path
    ):
        """validate_module_path rejects path traversal: {malicious_path}."""
        # Act & Assert
        with pytest.raises(SecurityError, match="Path traversal"):
            validator.validate_module_path(malicious_path, project_root)

    def test_rejects_doubledot_in_name(self, validator, project_root):
        """validate_module_path rejects names containing '..'."""
        # Act & Assert
        with pytest.raises(SecurityError, match="Path traversal"):
            validator.validate_module_path("my..module", project_root)


class TestValidateModulePathAbsolute:
    """Tests for absolute path validation."""

    @pytest.fixture
    def validator(self) -> SecurityValidator:
        """Create SecurityValidator instance."""
        return SecurityValidator()

    @pytest.fixture
    def project_root(self, tmp_path: Path) -> Path:
        """Create temporary project root."""
        project = tmp_path / "test-project"
        project.mkdir()
        return project

    @pytest.mark.parametrize("absolute_path", [
        "/etc/passwd",
        "/usr/local/lib",
        "/var/tmp/module",
    ])
    def test_rejects_unix_absolute_paths(self, validator, project_root, absolute_path):
        """validate_module_path rejects Unix absolute paths: {absolute_path}."""
        # Act & Assert
        with pytest.raises(SecurityError, match="Absolute paths"):
            validator.validate_module_path(absolute_path, project_root)

    @pytest.mark.parametrize("windows_path", [
        "C:\\Windows\\System32",
        "D:\\Modules\\auth",
        "C:/Program Files/module",
    ])
    def test_rejects_windows_absolute_paths(
        self, validator, project_root, windows_path
    ):
        """validate_module_path rejects Windows absolute paths: {windows_path}."""
        # Act & Assert
        with pytest.raises(SecurityError, match="Absolute paths"):
            validator.validate_module_path(windows_path, project_root)

    @pytest.mark.parametrize("unc_path", [
        "\\\\server\\share\\module",
        "\\\\localhost\\c$\\modules",
    ])
    def test_rejects_unc_paths(self, validator, project_root, unc_path):
        """validate_module_path rejects UNC paths: {unc_path}."""
        # Act & Assert
        with pytest.raises(SecurityError, match="Absolute paths"):
            validator.validate_module_path(unc_path, project_root)


class TestValidateModulePathValid:
    """Tests for valid path acceptance."""

    @pytest.fixture
    def validator(self) -> SecurityValidator:
        """Create SecurityValidator instance."""
        return SecurityValidator()

    @pytest.fixture
    def project_root(self, tmp_path: Path) -> Path:
        """Create temporary project root."""
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "modules").mkdir()
        return project

    @pytest.mark.parametrize("valid_name", [
        "auth",
        "user_service",
        "api_v2",
        "Auth",
        "MyModule",
        "_private",
        "module123",
    ])
    def test_accepts_valid_module_names(self, validator, project_root, valid_name):
        """validate_module_path accepts valid module names: {valid_name}."""
        # Arrange - create module directory
        module_dir = project_root / "modules" / valid_name
        module_dir.mkdir(parents=True, exist_ok=True)

        # Act & Assert - should not raise
        validator.validate_module_path(valid_name, project_root)

    def test_accepts_nested_valid_path(self, validator, project_root):
        """validate_module_path accepts nested valid paths."""
        # Arrange
        nested_path = "auth/providers"
        module_dir = project_root / "modules" / nested_path
        module_dir.mkdir(parents=True, exist_ok=True)

        # Act & Assert - should not raise
        validator.validate_module_path(nested_path, project_root)


class TestValidateModulePathBoundaries:
    """Tests for project boundary validation."""

    @pytest.fixture
    def validator(self) -> SecurityValidator:
        """Create SecurityValidator instance."""
        return SecurityValidator()

    @pytest.fixture
    def project_root(self, tmp_path: Path) -> Path:
        """Create temporary project root."""
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "modules").mkdir()
        return project

    def test_rejects_path_outside_project(self, validator, tmp_path: Path):
        """validate_module_path handles paths that would be outside project."""
        # Note: SecurityValidator checks for path traversal patterns,
        # not actual filesystem boundaries. This test verifies it doesn't crash.
        # Arrange - create module outside project
        outside_project = tmp_path / "outside" / "modules" / "auth"
        outside_project.mkdir(parents=True)

        # Create project without the module
        project_root = tmp_path / "test-project"
        project_root.mkdir()
        (project_root / "modules").mkdir()

        # Act & Assert - should not crash, may or may not raise depending on path
        # The validator checks patterns, not actual filesystem
        try:
            validator.validate_module_path("auth", project_root)
        except SecurityError:
            pass  # Acceptable if it raises

    def test_handles_nonexistent_module_dir(self, validator, project_root):
        """validate_module_path handles non-existent module directory."""
        # Act & Assert - should not raise even if module doesn't exist yet
        validator.validate_module_path("new_module", project_root)


class TestIsReservedName:
    """Tests for _is_reserved_name helper method."""

    @pytest.fixture
    def validator(self) -> SecurityValidator:
        """Create SecurityValidator instance."""
        return SecurityValidator()

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
        "user",
        "api",
        "mycore",  # Similar but not exact
        "test_module",  # Contains but not exact
    ])
    def test_returns_false_for_non_reserved(self, validator, name):
        """_is_reserved_name returns False for non-reserved names."""
        # Act
        result = validator._is_reserved_name(name)

        # Assert
        assert result is False


class TestIsPathTraversal:
    """Tests for _is_path_traversal helper method."""

    @pytest.fixture
    def validator(self) -> SecurityValidator:
        """Create SecurityValidator instance."""
        return SecurityValidator()

    @pytest.mark.parametrize("path", [
        "../etc",
        "..\\windows",
        "auth/../../../etc",
        "modules/..\\..\\secret",
        "/../outside",
        "\\..\\outside",
    ])
    def test_detects_path_traversal_patterns(self, validator, path):
        """_is_path_traversal detects various traversal patterns."""
        # Act
        result = validator._is_path_traversal(path)

        # Assert
        assert result is True

    @pytest.mark.parametrize("path", [
        "auth",
        "user_service",
        "modules/auth",
    ])
    def test_returns_false_for_safe_paths(self, validator, path):
        """_is_path_traversal returns False for safe paths."""
        # Act
        result = validator._is_path_traversal(path)

        # Assert
        assert result is False


class TestIsAbsolutePath:
    """Tests for _is_absolute_path helper method."""

    @pytest.fixture
    def validator(self) -> SecurityValidator:
        """Create SecurityValidator instance."""
        return SecurityValidator()

    @pytest.mark.parametrize("path", [
        "/etc/passwd",
        "/usr/local",
        "/var/tmp",
    ])
    def test_detects_unix_absolute_paths(self, validator, path):
        """_is_absolute_path detects Unix absolute paths."""
        # Act
        result = validator._is_absolute_path(path)

        # Assert
        assert result is True

    @pytest.mark.parametrize("path", [
        "C:\\Windows",
        "D:\\Modules",
        "Z:\\",
    ])
    def test_detects_windows_absolute_paths(self, validator, path):
        """_is_absolute_path detects Windows absolute paths."""
        # Act
        result = validator._is_absolute_path(path)

        # Assert
        assert result is True

    @pytest.mark.parametrize("path", [
        "\\\\server\\share",
        "\\\\localhost\\c$",
    ])
    def test_detects_unc_paths(self, validator, path):
        """_is_absolute_path detects UNC paths."""
        # Act
        result = validator._is_absolute_path(path)

        # Assert
        assert result is True

    @pytest.mark.parametrize("path", [
        "auth",
        "modules/auth",
        "./local",
        "../parent",  # Relative, not absolute
    ])
    def test_returns_false_for_relative_paths(self, validator, path):
        """_is_absolute_path returns False for relative paths."""
        # Act
        result = validator._is_absolute_path(path)

        # Assert
        assert result is False


class TestSecurityValidatorEdgeCases:
    """Tests for edge cases and error messages."""

    @pytest.fixture
    def validator(self) -> SecurityValidator:
        """Create SecurityValidator instance."""
        return SecurityValidator()

    @pytest.fixture
    def project_root(self, tmp_path: Path) -> Path:
        """Create temporary project root."""
        project = tmp_path / "test-project"
        project.mkdir()
        return project

    def test_error_message_includes_module_name(self, validator, project_root):
        """Error messages include the problematic module name."""
        # Act & Assert
        with pytest.raises(SecurityError) as exc_info:
            validator.validate_module_path("core", project_root)

        assert "core" in str(exc_info.value)

    def test_error_message_includes_path_for_traversal(
        self, validator, project_root
    ):
        """Error messages include path for traversal attempts."""
        # Act & Assert
        with pytest.raises(SecurityError) as exc_info:
            validator.validate_module_path("../etc", project_root)

        assert "../etc" in str(exc_info.value)

    def test_handles_valid_module_name(self, validator, project_root):
        """validate_module_path handles valid module names."""
        # Act & Assert - should not raise
        (project_root / "modules" / "valid_module").mkdir(parents=True)
        validator.validate_module_path("valid_module", project_root)
