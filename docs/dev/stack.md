# Technology Stack & Architecture

## Core Technology Stack

### Language & Runtime
- **Python 3.10+** - основной язык разработки
- **Type Hints** - строгая типизация для всех публичных API
- **Dataclasses** - для конфигурационных объектов
- **ABC (Abstract Base Classes)** - для базовых классов

**Rationale:**
- Python 3.10+ для modern features (match/case, better type hints)
- Существующая кодовая база уже на Python
- Отличная экосистема для CLI tools

---

### Core Dependencies

#### CLI & UX
```toml
click>=8.1         # CLI framework (текущая)
rich>=13.0         # Terminal formatting (текущая)
pyperclip>=1.8     # Clipboard operations (текущая)
```

#### Templating & Config
```toml
jinja2>=3.1        # Template engine (текущая)
pyyaml>=6.0        # YAML parsing (текущая)
```

#### Testing
```toml
pytest>=8.0        # Test framework (текущая)
pytest-cov>=4.0    # Coverage reports (текущая)
pytest-mock>=3.12  # Mocking support (NEW)
```

#### Data & Validation (NEW)
```toml
pydantic>=2.5      # Data validation
networkx>=3.2      # Dependency graph analysis
```

#### Optional Dependencies
```toml
graphviz>=0.20     # Module graph visualization
tabulate>=0.9      # Table formatting for CLI
```

---

## Architecture Principles

### 1. Single Responsibility Principle
Каждый модуль отвечает за одну задачу:
- `Bootstrapper` - только инициализация проекта
- `ModuleManager` - только управление модулями
- `IntegrationManager` - только интеграция
- `Runner` - только запуск skills

### 2. Open/Closed Principle
Открыто для расширения, закрыто для модификации:
- `BaseBootstrapper` - abstract class для новых режимов
- `BaseRunner` - abstract class для разных runners
- Plugin system для custom agents

### 3. Liskov Substitution Principle
Все режимы взаимозаменяемы:
```python
# Оба наследника BaseBootstrapper работают одинаково
bootstrapper: BaseBootstrapper = SimpleBootstrapper(...)
bootstrapper: BaseBootstrapper = ModularBootstrapper(...)
bootstrapper.run()  # Одинаковый интерфейс
```

### 4. Interface Segregation Principle
Маленькие, специфичные интерфейсы:
```python
class Creatable(Protocol):
    def create(self) -> None: ...

class Listable(Protocol):
    def list(self) -> List[Dict]: ...

class Buildable(Protocol):
    def build(self) -> None: ...
```

### 5. Dependency Inversion Principle
Зависимости направлены к абстракциям:
- CLI зависит от `BaseBootstrapper`, не от конкретных реализаций
- Managers зависят от протоколов, не от конкретных классов

---

## Project Structure

### High-Level Architecture
```
vibecraft/
├── core/                      # Ядро фреймворка
│   ├── __init__.py
│   ├── base_bootstrapper.py   # ABC для всех bootstrappers
│   ├── base_runner.py         # ABC для всех runners
│   ├── config.py              # Configuration models
│   ├── protocols.py           # Protocol definitions
│   └── exceptions.py          # Custom exceptions
│
├── modes/                     # Режимы работы
│   ├── __init__.py
│   ├── simple/                # Simple mode (текущий)
│   │   ├── __init__.py
│   │   ├── bootstrapper.py
│   │   └── runner.py
│   └── modular/               # Modular mode (новый)
│       ├── __init__.py
│       ├── bootstrapper.py
│       ├── runner.py
│       ├── module_manager.py
│       ├── integration_manager.py
│       ├── plan_generator.py
│       └── dependency_analyzer.py
│
├── cli.py                     # CLI entry point
├── runner.py                  # Orchestrator для runners
├── context_manager.py         # Context management
├── doctor.py                  # Environment checks
├── rollback.py                # Rollback functionality
├── exporter.py                # Export functionality
├── main.py                    # Entry point с encoding fix
│
├── adapters/                  # Adapters для разных backends
│   ├── __init__.py
│   ├── base_adapter.py
│   └── clipboard_adapter.py
│
├── templates/                 # Jinja2 templates
│   ├── simple/                # Simple mode templates
│   │   ├── agents/
│   │   ├── skills/
│   │   └── context.md.j2
│   └── modular/               # Modular mode templates
│       ├── agents/
│       ├── skills/
│       ├── development-plan.md.j2
│       ├── module-config.json.j2
│       ├── module-research.md.j2
│       └── interfaces.py.j2
│
└── utils/                     # Utility functions
    ├── __init__.py
    ├── file_utils.py
    ├── graph_utils.py
    └── validation.py
```

---

## Design Patterns

### 1. Factory Pattern
**Где:** Mode selection, adapter creation

```python
# vibecraft/core/factory.py
class BootstrapperFactory:
    @staticmethod
    def create(mode: ProjectMode, **kwargs) -> BaseBootstrapper:
        if mode == ProjectMode.SIMPLE:
            return SimpleBootstrapper(**kwargs)
        elif mode == ProjectMode.MODULAR:
            return ModularBootstrapper(**kwargs)
        raise ValueError(f"Unknown mode: {mode}")
```

**Benefits:**
- Централизованное создание объектов
- Легко добавлять новые режимы
- Скрывает детали создания

---

### 2. Strategy Pattern
**Где:** Разные runners для разных режимов

```python
# vibecraft/core/base_runner.py
class BaseRunner(ABC):
    @abstractmethod
    def run(self) -> None:
        pass

# CLI использует strategy
runner = BootstrapperFactory.create(config.mode, ...)
runner.run()  # Разное поведение для разных режимов
```

**Benefits:**
- Взаимозаменяемые алгоритмы
- Легко тестировать каждую стратегию
- Минимальный coupling

---

### 3. Builder Pattern
**Где:** Создание сложных конфигураций

```python
# vibecraft/modes/modular/plan_generator.py
class DevelopmentPlanBuilder:
    def __init__(self):
        self._modules = []
        self._dependencies = {}
        
    def add_module(self, name: str, description: str):
        self._modules.append({"name": name, "description": description})
        return self
    
    def add_dependency(self, module: str, depends_on: str):
        if module not in self._dependencies:
            self._dependencies[module] = []
        self._dependencies[module].append(depends_on)
        return self
    
    def build(self) -> DevelopmentPlan:
        return DevelopmentPlan(
            modules=self._modules,
            dependencies=self._dependencies
        )
```

**Benefits:**
- Поэтапное создание сложных объектов
- Fluent interface для удобства
- Валидация на этапе build()

---

### 4. Observer Pattern
**Где:** Events при изменении состояния проекта

```python
# vibecraft/core/events.py
class EventEmitter:
    def __init__(self):
        self._observers = []
    
    def subscribe(self, observer: Callable):
        self._observers.append(observer)
    
    def emit(self, event: str, data: Dict):
        for observer in self._observers:
            observer(event, data)

# Usage
emitter = EventEmitter()
emitter.subscribe(lambda e, d: console.print(f"[green]✓ {e}[/green]"))
emitter.emit("module_created", {"name": "auth"})
```

**Benefits:**
- Loose coupling
- Extensibility для plugins
- Легко добавить logging, metrics

---

### 5. Repository Pattern
**Где:** Работа с modules registry

```python
# vibecraft/modes/modular/module_repository.py
class ModuleRepository:
    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
    
    def get_all(self) -> List[Module]:
        data = json.loads(self.registry_path.read_text())
        return [Module(**m) for m in data["modules"]]
    
    def get_by_name(self, name: str) -> Optional[Module]:
        modules = self.get_all()
        return next((m for m in modules if m.name == name), None)
    
    def save(self, module: Module) -> None:
        modules = self.get_all()
        # Update or insert
        ...
        self._write(modules)
```

**Benefits:**
- Абстракция над хранилищем
- Легко менять формат хранения (JSON → SQLite)
- Простое тестирование с mock repository

---

## Data Models

### Core Models (using Pydantic)

```python
# vibecraft/core/models.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime

class ProjectMode(str, Enum):
    SIMPLE = "simple"
    MODULAR = "modular"

class ProjectType(str, Enum):
    WEB = "web"
    API = "api"
    CLI = "cli"
    GAME = "game"
    MOBILE = "mobile"

class VibecraftConfig(BaseModel):
    """Конфигурация проекта."""
    mode: ProjectMode
    version: str = "0.4.0"
    project_name: str
    project_type: ProjectType
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Modular-specific
    modular: Optional["ModularConfig"] = None
    
    class Config:
        use_enum_values = True

class ModularConfig(BaseModel):
    """Конфигурация для modular режима."""
    modules_dir: str = "modules"
    shared_dir: str = "shared"
    integration_dir: str = "integration"
    modules: List[str] = Field(default_factory=list)

class Module(BaseModel):
    """Модель модуля."""
    name: str
    description: str
    status: str = "planned"  # planned, in_progress, completed
    dependencies: List[str] = Field(default_factory=list)
    exports: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    phases_completed: List[int] = Field(default_factory=list)
    
    @validator("name")
    def validate_name(cls, v):
        if not v.isidentifier():
            raise ValueError("Module name must be valid Python identifier")
        return v

class DependencyGraph(BaseModel):
    """Граф зависимостей между модулями."""
    nodes: List[str]  # Module names
    edges: Dict[str, List[str]]  # module -> [dependencies]
    
    def has_cycle(self) -> bool:
        """Проверка циклических зависимостей."""
        # Implementation using DFS
        pass
    
    def topological_sort(self) -> List[str]:
        """Топологическая сортировка для build order."""
        # Implementation using Kahn's algorithm
        pass
```

---

## Dependency Management

### Module Dependencies

**Declaration (.module.json):**
```json
{
  "name": "users",
  "dependencies": ["auth", "database"],
  "exports": ["UserService", "get_user", "create_user"]
}
```

**Validation:**
```python
class DependencyAnalyzer:
    def validate_dependencies(self, registry: ModuleRegistry) -> List[str]:
        """
        Проверяет:
        1. Все зависимости существуют
        2. Нет циклических зависимостей
        3. Build order возможен
        
        Returns: List of errors or empty list
        """
        errors = []
        
        # Check existence
        for module in registry.modules:
            for dep in module.dependencies:
                if not registry.has_module(dep):
                    errors.append(f"{module.name} depends on non-existent {dep}")
        
        # Check cycles
        graph = self._build_graph(registry)
        if graph.has_cycle():
            errors.append("Circular dependencies detected")
        
        return errors
```

---

## File Formats

### .vibecraft/config.json
```json
{
  "mode": "modular",
  "version": "0.4.0",
  "project_name": "my-saas-platform",
  "project_type": "web",
  "created_at": "2026-02-26T12:00:00Z",
  
  "modular": {
    "modules_dir": "modules",
    "shared_dir": "shared",
    "integration_dir": "integration",
    "modules": ["auth", "users", "billing", "api"]
  }
}
```

### .vibecraft/modules-registry.json
```json
{
  "modules": [
    {
      "name": "auth",
      "path": "modules/auth",
      "status": "completed",
      "dependencies": ["database"],
      "phases_completed": [1, 2, 3, 4, 5]
    }
  ],
  "dependencies": {
    "auth": ["database"],
    "users": ["auth", "database"],
    "billing": ["users", "auth"],
    "api": ["auth", "users", "billing"]
  },
  "build_order": ["database", "auth", "users", "billing", "api"]
}
```

### modules/auth/.module.json
```json
{
  "name": "auth",
  "description": "Authentication and authorization module",
  "status": "in_progress",
  "dependencies": ["database", "config"],
  "exports": [
    "AuthService",
    "login",
    "logout",
    "verify_token",
    "refresh_token"
  ],
  "created_at": "2026-02-26T13:00:00Z",
  "phases_completed": [1, 2],
  
  "metadata": {
    "owner": "backend-team",
    "priority": "high",
    "estimated_days": 5
  }
}
```

---

## Testing Strategy

### Unit Tests
**Location:** `tests/unit/`

```python
# tests/unit/modes/test_module_manager.py
class TestModuleManager:
    def test_create_module(self, tmp_path):
        manager = ModuleManager(tmp_path)
        manager.create_module("auth", "Authentication module")
        
        assert (tmp_path / "modules" / "auth").exists()
        assert (tmp_path / "modules" / "auth" / ".module.json").exists()
    
    def test_list_modules(self, tmp_path):
        manager = ModuleManager(tmp_path)
        manager.create_module("auth", "Auth")
        manager.create_module("users", "Users")
        
        modules = manager.list_modules()
        assert len(modules) == 2
        assert modules[0]["name"] == "auth"
```

### Integration Tests
**Location:** `tests/integration/`

```python
# tests/integration/test_modular_workflow.py
class TestModularWorkflow:
    def test_full_modular_project_creation(self, tmp_path):
        """
        End-to-end test:
        1. Init modular project
        2. Create 3 modules
        3. Analyze dependencies
        4. Build project
        """
        # Init
        bootstrapper = ModularBootstrapper(...)
        bootstrapper.run()
        
        # Create modules
        manager = ModuleManager(tmp_path)
        manager.create_module("database", "DB layer")
        manager.create_module("auth", "Auth", dependencies=["database"])
        manager.create_module("api", "API", dependencies=["auth"])
        
        # Analyze
        integration = IntegrationManager(tmp_path)
        errors = integration.analyze_dependencies()
        assert len(errors) == 0
        
        # Build
        integration.build_project()
        assert (tmp_path / "integration" / "interfaces.py").exists()
```

### Test Coverage Goals
- **Unit tests:** 95%+ для core и modes
- **Integration tests:** Все основные workflows
- **Regression tests:** Все old bugs должны иметь tests

---

## Code Quality Standards

### Type Checking
```bash
# Использовать mypy для статической проверки типов
mypy vibecraft/ --strict
```

**Configuration (pyproject.toml):**
```toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Code Formatting
```bash
# Black для автоформатирования
black vibecraft/ tests/

# isort для сортировки импортов
isort vibecraft/ tests/
```

### Linting
```bash
# ruff для быстрого linting
ruff check vibecraft/ tests/
```

**Configuration (pyproject.toml):**
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Line too long (handled by black)
```

---

## Error Handling

### Custom Exceptions Hierarchy
```python
# vibecraft/core/exceptions.py
class VibecraftError(Exception):
    """Base exception for all Vibecraft errors."""
    pass

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
```

### Error Handling Pattern
```python
from vibecraft.core.exceptions import ModuleError, DependencyError

def create_module(name: str) -> None:
    try:
        _validate_module_name(name)
        _create_module_structure(name)
    except ValueError as e:
        raise ModuleError(f"Invalid module name: {e}") from e
    except OSError as e:
        raise ModuleError(f"Failed to create module: {e}") from e
```

---

## Performance Considerations

### Lazy Loading
```python
# Загружать модули только когда нужно
class ModuleRegistry:
    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self._cache: Optional[Dict] = None
    
    def get_all(self) -> List[Module]:
        if self._cache is None:
            self._cache = self._load()
        return self._cache["modules"]
```

### Efficient Graph Operations
```python
# Использовать networkx для сложных операций
import networkx as nx

class DependencyGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def has_cycle(self) -> bool:
        try:
            nx.find_cycle(self.graph)
            return True
        except nx.NetworkXNoCycle:
            return False
    
    def topological_sort(self) -> List[str]:
        return list(nx.topological_sort(self.graph))
```

---

## Documentation Standards

### Docstrings (Google Style)
```python
def create_module(name: str, description: str, dependencies: List[str]) -> Module:
    """Create a new module in the project.
    
    Args:
        name: Module name (must be valid Python identifier)
        description: Human-readable description
        dependencies: List of module names this module depends on
    
    Returns:
        Module: The created module object
    
    Raises:
        ModuleError: If module name is invalid
        DependencyError: If dependencies don't exist
    
    Example:
        >>> manager = ModuleManager(Path("/project"))
        >>> module = manager.create_module("auth", "Authentication", ["database"])
        >>> print(module.name)
        'auth'
    """
    pass
```

### README Files
Каждая директория с кодом должна иметь README.md:
- `vibecraft/core/README.md` - описание core components
- `vibecraft/modes/README.md` - объяснение режимов
- `vibecraft/modes/modular/README.md` - детали modular режима

---

## Security Considerations

### Path Traversal Prevention
```python
def _validate_module_path(module_name: str, project_root: Path) -> None:
    """Prevent path traversal attacks."""
    module_path = project_root / "modules" / module_name
    
    # Ensure path is within project
    if not module_path.resolve().is_relative_to(project_root.resolve()):
        raise SecurityError(f"Invalid module path: {module_name}")
```

### Input Validation
```python
@validator("name")
def validate_module_name(cls, v: str) -> str:
    """Validate module name is safe."""
    # Only allow alphanumeric and underscore
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v):
        raise ValueError("Invalid module name")
    
    # Prevent reserved words
    if v in ["core", "vibecraft", "test"]:
        raise ValueError(f"'{v}' is a reserved name")
    
    return v
```

---

## Backward Compatibility

### Version Migration
```python
# vibecraft/core/migrations.py
class ConfigMigrator:
    def migrate(self, config: Dict, from_version: str, to_version: str) -> Dict:
        """Migrate config between versions."""
        if from_version == "0.3.0" and to_version == "0.4.0":
            return self._migrate_0_3_to_0_4(config)
        return config
    
    def _migrate_0_3_to_0_4(self, config: Dict) -> Dict:
        """Add mode field if missing."""
        if "mode" not in config:
            config["mode"] = "simple"
        return config
```

### Deprecation Policy
```python
import warnings

def old_function():
    """Deprecated function."""
    warnings.warn(
        "old_function is deprecated, use new_function instead",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function()
```

---

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -e ".[test]"
          pip install mypy ruff black isort
      
      - name: Type checking
        run: mypy vibecraft/
      
      - name: Linting
        run: ruff check vibecraft/
      
      - name: Tests
        run: pytest tests/ --cov=vibecraft --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Future Technology Considerations

### Potential Additions (v0.5+)

1. **SQLite for Large Registries**
   - Если проект имеет 100+ модулей
   - Заменить JSON на SQLite
   - Сохранить backward compatibility

2. **GraphQL API**
   - Для IDE integrations
   - Real-time collaboration
   - Remote project management

3. **Web Dashboard**
   - FastAPI backend
   - React frontend
   - Real-time module status

4. **Docker Integration**
   - Автогенерация Dockerfiles для модулей
   - Docker Compose для локальной разработки

---

## Conclusion

Этот стек обеспечивает:
- ✅ **Maintainability** - чистая архитектура, SOLID принципы
- ✅ **Testability** - 95%+ coverage, clear interfaces
- ✅ **Extensibility** - plugin system, abstract base classes
- ✅ **Performance** - lazy loading, efficient algorithms
- ✅ **Developer Experience** - type hints, rich CLI, good docs
- ✅ **Backward Compatibility** - migration system, deprecation policy

Архитектура позволяет легко добавлять новые режимы работы без изменения существующего кода.
