"""
Security Validator for Vibecraft Framework.

Validates module paths for security issues.
"""
from pathlib import Path
from vibecraft.core.exceptions import SecurityError


class SecurityValidator:
    """
    Validates module paths for security issues.
    
    Checks:
    - Path traversal attacks (../, ..\\)
    - Reserved paths
    - Path is within project boundaries
    """
    
    # Reserved names that cannot be used as module paths
    RESERVED_NAMES = {
        "core",
        "vibecraft",
        "test",
        "shared",
        "integration"
    }
    
    def validate_module_path(
        self,
        module_name: str,
        project_root: Path
    ) -> None:
        """
        Validate a module path for security issues.
        
        Args:
            module_name: Module name
            project_root: Project root path
        
        Raises:
            SecurityError: If path is invalid or insecure
        """
        # Check for reserved names
        if self._is_reserved_name(module_name):
            raise SecurityError(f"Module path is invalid: '{module_name}' is a reserved name")
        
        # Check for path traversal attempts
        if self._is_path_traversal(module_name):
            raise SecurityError(f"Module path is invalid: '{module_name}'. Path traversal is not allowed")
        
        # Check for absolute paths
        if self._is_absolute_path(module_name):
            raise SecurityError(f"Module path is invalid: '{module_name}'. Absolute paths are not allowed")
        
        # Verify the resolved path is within project
        module_path = project_root / "modules" / module_name
        try:
            resolved_path = module_path.resolve()
            resolved_project = project_root.resolve()
            
            if not resolved_path.is_relative_to(resolved_project):
                raise SecurityError("Module path is invalid: must be within project directory")
        except (ValueError, OSError):
            # If we can't resolve, that's also suspicious
            raise SecurityError(f"Module path is invalid: '{module_name}'")
    
    def _is_reserved_name(self, name: str) -> bool:
        """
        Check if name is a reserved name.
        
        Args:
            name: Name to check
        
        Returns:
            True if reserved, False otherwise
        """
        return name in self.RESERVED_NAMES
    
    def _is_path_traversal(self, path: str) -> bool:
        """
        Check if path contains path traversal attempts.
        
        Args:
            path: Path to check
        
        Returns:
            True if path traversal detected, False otherwise
        """
        # Check for various path traversal patterns
        traversal_patterns = [
            "..",
            "../",
            "..\\",
            "/..",
            "\\..",
        ]
        
        for pattern in traversal_patterns:
            if pattern in path:
                return True
        
        return False
    
    def _is_absolute_path(self, path: str) -> bool:
        """
        Check if path is an absolute path.
        
        Args:
            path: Path to check
        
        Returns:
            True if absolute, False otherwise
        """
        # Check for Unix absolute path
        if path.startswith("/"):
            return True
        
        # Check for Windows absolute path (e.g., C:\, D:\)
        if len(path) >= 2 and path[1] == ":":
            return True
        
        # Check for UNC paths
        if path.startswith("\\\\"):
            return True
        
        return False
