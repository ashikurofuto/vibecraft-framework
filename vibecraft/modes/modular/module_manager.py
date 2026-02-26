"""
Module Manager for Vibecraft Framework.

Handles CRUD operations for modules in modular mode.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from vibecraft.core.exceptions import ModuleError
from vibecraft.modes.modular.validation import ModuleValidator
from vibecraft.modes.modular.security import SecurityValidator
from vibecraft.modes.modular.module_registry import ModuleRegistry


class ModuleManager:
    """
    Manages modules in a Vibecraft project.
    
    Responsibilities:
    - Create modules
    - List modules
    - Initialize module structure
    - Get module status
    """

    def __init__(self, project_root: Path):
        """
        Initialize ModuleManager.
        
        Args:
            project_root: Root path of the Vibecraft project
        """
        self.project_root = Path(project_root)
        self.modules_dir = self.project_root / "modules"
        self.validator = ModuleValidator()
        self.security_validator = SecurityValidator()
        
        # Ensure modules directory exists
        self.initialize()
    
    def initialize(self) -> None:
        """Create modules directory if it doesn't exist."""
        self.modules_dir.mkdir(parents=True, exist_ok=True)
    
    def create_module(
        self,
        name: str,
        description: str,
        dependencies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new module.
        
        Args:
            name: Module name (must be valid Python identifier)
            description: Human-readable description
            dependencies: List of module names this module depends on
        
        Returns:
            Module information dictionary
        
        Raises:
            ModuleError: If module name is invalid or module already exists
        """
        # Validate module name
        self.validator.validate_module_name(name)

        # Validate module path for security
        self.security_validator.validate_module_path(name, self.project_root)

        # Note: We don't validate dependencies exist here to allow forward references.
        # Dependencies will be validated during 'vibecraft integrate analyze'

        # Check if module already exists
        module_path = self.modules_dir / name
        if module_path.exists():
            raise ModuleError(f"Module '{name}' already exists")
        
        # Create module directory
        module_path.mkdir(parents=True, exist_ok=True)
        
        # Create .module.json
        module_data = {
            "name": name,
            "description": description,
            "status": "planned",
            "dependencies": dependencies or [],
            "exports": [],
            "created_at": datetime.now().isoformat(),
            "phases_completed": []
        }

        module_json_path = module_path / ".module.json"
        module_json_path.write_text(json.dumps(module_data, indent=2))

        # Update registry using Module object to preserve all data
        registry_path = self.project_root / ".vibecraft" / "modules-registry.json"
        registry = ModuleRegistry(registry_path)
        
        from vibecraft.core.config import Module
        module = Module(
            name=name,
            path=str(module_path.relative_to(self.project_root)),
            description=description,
            dependencies=dependencies or [],
            status="planned"
        )
        registry.add_module(module)

        return module_data
    
    def list_modules(self) -> List[Dict[str, Any]]:
        """
        List all modules in the project.
        
        Returns:
            List of module information dictionaries
        """
        modules: List[Dict[str, Any]] = []
        
        if not self.modules_dir.exists():
            return modules
        
        for module_path in self.modules_dir.iterdir():
            if module_path.is_dir():
                module_json = module_path / ".module.json"
                if module_json.exists():
                    data = json.loads(module_json.read_text())
                    modules.append(data)
        
        return modules
    
    def get_status(self, name: str) -> Dict[str, Any]:
        """
        Get status of a specific module.
        
        Args:
            name: Module name
        
        Returns:
            Module information dictionary
        
        Raises:
            ModuleError: If module doesn't exist
        """
        module_path = self.modules_dir / name
        
        if not module_path.exists():
            raise ModuleError(f"Module '{name}' not found")
        
        module_json = module_path / ".module.json"
        if not module_json.exists():
            raise ModuleError(f"Module '{name}' has no .module.json")
        
        return json.loads(module_json.read_text())
    
    def init_module(self, name: str) -> None:
        """
        Initialize module structure with directories and files.
        
        Creates:
        - research.md
        - stack.md
        - agents/ directory
        - skills/ directory
        
        Args:
            name: Module name
        
        Raises:
            ModuleError: If module doesn't exist
        """
        module_path = self.modules_dir / name
        
        if not module_path.exists():
            raise ModuleError(f"Module '{name}' not found")
        
        # Create directories
        agents_dir = module_path / "agents"
        skills_dir = module_path / "skills"
        
        agents_dir.mkdir(exist_ok=True)
        skills_dir.mkdir(exist_ok=True)
        
        # Create research.md if it doesn't exist
        research_path = module_path / "research.md"
        if not research_path.exists():
            research_path.write_text(f"# {name} — Research\n\n")
        
        # Create stack.md if it doesn't exist
        stack_path = module_path / "stack.md"
        if not stack_path.exists():
            stack_path.write_text(f"# {name} — Technology Stack\n\n")
