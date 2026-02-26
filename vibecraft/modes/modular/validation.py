"""
Module Validator for Vibecraft Framework.

Validates module names and properties.
"""
import re
from vibecraft.core.exceptions import ModuleError


class ModuleValidator:
    """
    Validates module names and properties.
    
    Rules:
    - Must be valid Python identifier
    - Cannot be a reserved name
    """
    
    # Reserved names that cannot be used as module names
    RESERVED_NAMES = {
        "core",
        "vibecraft",
        "test",
        "shared",
        "integration"
    }
    
    def validate_module_name(self, name: str) -> None:
        """
        Validate a module name.
        
        Args:
            name: Module name to validate
        
        Raises:
            ModuleError: If name is invalid
        """
        # Check for empty string
        if not name:
            raise ModuleError("Module name is invalid: cannot be empty")
        
        # Check if it's a valid Python identifier
        if not self._is_valid_identifier(name):
            raise ModuleError(f"Module name is invalid: '{name}'. Must be a valid Python identifier")
        
        # Check for reserved names
        if self._is_reserved_name(name):
            raise ModuleError(f"Module name is invalid: '{name}' is reserved")
    
    def _is_valid_identifier(self, name: str) -> bool:
        """
        Check if name is a valid Python identifier.
        
        Args:
            name: Name to check
        
        Returns:
            True if valid, False otherwise
        """
        # Must match: starts with letter or underscore, followed by letters, numbers, or underscores
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, name))
    
    def _is_reserved_name(self, name: str) -> bool:
        """
        Check if name is a reserved name.
        
        Args:
            name: Name to check
        
        Returns:
            True if reserved, False otherwise
        """
        return name in self.RESERVED_NAMES
