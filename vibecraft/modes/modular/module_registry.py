"""
Module Registry for Vibecraft Framework.

Central registry for all modules in a project.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, overload
import json

from vibecraft.core.config import Module


class ModuleRegistry:
    """
    Central registry for module information.

    Stores module metadata in .vibecraft/modules-registry.json
    """

    def __init__(self, registry_path: Path):
        """
        Initialize ModuleRegistry.

        Args:
            registry_path: Path to the registry JSON file
        """
        self.registry_path = Path(registry_path)
        self._cache: Optional[Dict[str, Any]] = None
        self._ensure_registry_exists()

    def _ensure_registry_exists(self) -> None:
        """Create registry file if it doesn't exist."""
        if not self.registry_path.exists():
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            initial_data: Dict[str, Any] = {
                "modules": [],
                "dependencies": {},
                "build_order": []
            }
            self.registry_path.write_text(json.dumps(initial_data, indent=2))

    def _read(self) -> Dict[str, Any]:
        """Read registry data from file with caching."""
        # Return cached data if available
        if self._cache is not None:
            return self._cache
        
        # Read from file
        data = json.loads(self.registry_path.read_text(encoding='utf-8'))
        self._cache = data
        return self._cache

    def _write(self, data: Dict[str, Any]) -> None:
        """Write registry data to file."""
        # Update cache
        self._cache = data
        
        # Write to file
        self.registry_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def invalidate_cache(self) -> None:
        """Invalidate cache to force reload from disk."""
        self._cache = None

    def _module_to_dict(self, module: Module) -> Dict[str, Any]:
        """Convert Module object to registry dict format."""
        # Set path if not already set
        path = module.path
        if not path:
            path = f"modules/{module.name}"
        
        return {
            "name": module.name,
            "path": path,
            "status": module.status,
            "description": module.description,
            "dependencies": module.dependencies,
            "exports": module.exports,
            "phases_completed": module.phases_completed,
            "created_at": module.created_at.isoformat() if module.created_at else None,
            "metadata": module.metadata
        }

    def _dict_to_module(self, data: Dict[str, Any]) -> Module:
        """Convert registry dict to Module object."""
        from datetime import datetime, timezone

        # Parse created_at from ISO format string
        created_at_str = data.get("created_at")
        if created_at_str:
            created_at = datetime.fromisoformat(created_at_str)
        else:
            created_at = datetime.now(timezone.utc)

        return Module(
            name=data.get("name", ""),
            description=data.get("description", ""),
            path=data.get("path", f"modules/{data.get('name', '')}"),
            status=data.get("status", "planned"),
            dependencies=data.get("dependencies", []),
            exports=data.get("exports", []),
            phases_completed=data.get("phases_completed", []),
            created_at=created_at,
            metadata=data.get("metadata")
        )

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all modules from registry as dictionaries.

        Returns:
            List of module information dictionaries

        Note: For Module objects, use get_all_modules()
        """
        data = self._read()
        return data.get("modules", [])

    def get_all_modules(self) -> List["Module"]:
        """
        Get all modules from registry as Module objects.

        Returns:
            List of Module objects

        Note: Phase 6+ API
        """
        from vibecraft.core.config import Module

        data = self._read()
        modules_data = data.get("modules", [])
        return [self._dict_to_module(m) for m in modules_data]

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get module by name.

        Args:
            name: Module name

        Returns:
            Module information dictionary or None if not found

        Note: For Module object, use get_module_by_name()
        """
        modules = self.get_all()
        for module in modules:
            if module.get("name") == name:
                return module
        return None

    def get_module_by_name(self, name: str) -> Optional["Module"]:
        """
        Get module by name as Module object.

        Args:
            name: Module name

        Returns:
            Module object or None if not found

        Note: Phase 6+ API
        """
        from vibecraft.core.config import Module

        modules = self.get_all_modules()
        for module in modules:
            if module.name == name:
                return module
        return None

    def has_module(self, name: str) -> bool:
        """
        Check if module exists in registry.

        Args:
            name: Module name

        Returns:
            True if module exists, False otherwise
        """
        return self.get_by_name(name) is not None

    @overload
    def add_module(self, module: Module) -> None:
        """Add module using Module object (Phase 6+ API)."""
        ...

    @overload
    def add_module(self, name: str, path: str, description: str, **kwargs: Any) -> None:
        """Add module using legacy API (Phase 5 API)."""
        ...

    def add_module(self, *args: Any, **kwargs: Any) -> None:
        """
        Add a module to the registry.

        Supports two calling styles:
        1. New style (Phase 6+): add_module(module: Module)
        2. Legacy style (Phase 5): add_module(name: str, path: str, description: str)

        Args:
            For new style: Module object
            For legacy style: name, path, description as positional args

        Example:
            # New style
            registry.add_module(Module(name="auth", description="Auth"))

            # Legacy style
            registry.add_module("auth", "modules/auth", "Authentication")
        """
        from vibecraft.core.config import Module

        # New style: add_module(module: Module)
        if len(args) == 1 and isinstance(args[0], Module):
            module = args[0]
        # Legacy style: add_module(name, path, description)
        elif len(args) >= 3:
            name, path, description = args[0], args[1], args[2]
            module = Module(
                name=name,
                path=path,
                description=description,
                dependencies=kwargs.get("dependencies", []),
                status=kwargs.get("status", "planned")
            )
        # Keyword style: add_module(name=..., path=..., description=...)
        elif "name" in kwargs and "path" in kwargs and "description" in kwargs:
            module = Module(
                name=kwargs["name"],
                path=kwargs["path"],
                description=kwargs["description"],
                dependencies=kwargs.get("dependencies", []),
                status=kwargs.get("status", "planned")
            )
        else:
            raise TypeError(
                "add_module() requires either a Module object or "
                "(name, path, description) arguments"
            )

        # Check if module already exists
        if self.has_module(module.name):
            return  # Module already in registry

        # Add new module
        new_module_data = self._module_to_dict(module)
        data = self._read()
        data["modules"].append(new_module_data)
        self._write(data)

    @overload
    def update_module(self, module: Module) -> None:
        """Update module using Module object (Phase 6+ API)."""
        ...

    @overload
    def update_module(self, name: str, **kwargs: Any) -> None:
        """Update module using legacy API (Phase 5 API)."""
        ...

    def update_module(self, *args: Any, **kwargs: Any) -> None:
        """
        Update module information.

        Supports two calling styles:
        1. New style (Phase 6+): update_module(module: Module)
        2. Legacy style (Phase 5): update_module(name: str, **kwargs)

        Args:
            For new style: Module object with updated information
            For legacy style: name as first arg, then fields to update as kwargs

        Raises:
            ModuleError: If module doesn't exist
        """
        from vibecraft.core.exceptions import ModuleError
        from vibecraft.core.config import Module

        # New style: update_module(module: Module)
        if len(args) == 1 and isinstance(args[0], Module):
            module = args[0]
            name = module.name

            data = self._read()

            # Find module
            module_found = False
            for i, existing_module in enumerate(data["modules"]):
                if existing_module.get("name") == name:
                    # Update fields from module object
                    updated_data = self._module_to_dict(module)
                    data["modules"][i] = updated_data
                    module_found = True
                    break

            if not module_found:
                raise ModuleError(f"Module '{name}' not found")

            self._write(data)

        # Legacy style: update_module(name, **kwargs)
        elif len(args) >= 1 and isinstance(args[0], str):
            name = args[0]
            updates = kwargs

            data = self._read()

            # Find module
            module_found = False
            for i, existing_module in enumerate(data["modules"]):
                if existing_module.get("name") == name:
                    # Update fields
                    for key, value in updates.items():
                        data["modules"][i][key] = value
                    module_found = True
                    break

            if not module_found:
                raise ModuleError(f"Module '{name}' not found")

            self._write(data)
        else:
            raise TypeError(
                "update_module() requires either a Module object or "
                "(name, **kwargs) arguments"
            )

    def remove_module(self, name: str) -> None:
        """
        Remove module from registry.

        Args:
            name: Module name

        Raises:
            ModuleError: If module doesn't exist
        """
        from vibecraft.core.exceptions import ModuleError

        data = self._read()

        # Check if module exists first
        if not self.has_module(name):
            raise ModuleError(f"Module '{name}' not found")

        # Remove module
        data["modules"] = [m for m in data["modules"] if m.get("name") != name]

        self._write(data)

    def save(self) -> None:
        """
        Save registry to file.

        This is a no-op since we save on every modification,
        but kept for API compatibility.
        """
        pass  # Already saved on each modification
