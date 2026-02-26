# Vibecraft Framework v0.4 — Context for Qwen Code

> **Project:** Vibecraft Framework v0.4 - Multi-Mode Architecture
> **Type:** Python CLI Framework / Agent-driven development tool
> **Runtime:** Python 3.10+
> **Working Directory:** `C:\Users\Пользователь\Documents\projects\vibecraft_v0.3`
> **Current Phase:** Phase 10 Complete ✅ (RELEASE v0.4.0 READY)
> **Language:** Russian (для объяснений), English (для кода)

---

## Quick Reference

```bash
# Install framework (development mode)
cd vibecraft-framework
pip install -e ".[test]"

# Run tests
pytest tests/unit/core/ -v       # Phase 1: 66 tests
pytest ../src/tests/phase_4/ -v  # Phase 4: 71 tests
pytest ../src/tests/phase_5/ -v  # Phase 5: 97 tests
pytest ../src/tests/phase_6/ -v  # Phase 6: 66 tests
pytest ../src/tests/phase_7/ -v  # Phase 7: 66 tests ✅

# Use vibecraft CLI
vibecraft doctor
vibecraft init -r docs/research.md -s docs/stack.md
vibecraft init -r docs/research.md -s docs/stack.md --mode modular
vibecraft run research
vibecraft status
```

---

## Project Overview

**Vibecraft Framework** — это CLI-фреймворк для agent-driven разработки, который бутстрапит проект из двух файлов (`research.md` + `stack.md`) и ведёт разработчика через фазы:

```
research → design → plan → implement (TDD) → review
```

### Ключевые особенности v0.4

| Feature | Description |
|---------|-------------|
| **Dual-Mode Architecture** | Simple mode (legacy v0.3) + Modular mode (новый, для больших проектов) |
| **TDD Pipeline** | RED/GREEN фазы: сначала тесты, потом реализация |
| **Agent System** | 14 агентов для различных задач разработки |
| **Clipboard-Only** | Промпты копируются в clipboard, нет прямой интеграции с LLM API |
| **Module Management** | Создание, листинг, инициализация модулей (modular mode) |
| **Dependency Analysis** | Валидация зависимостей, обнаружение циклов, topological sort (Phase 6) |
| **Integration Build** | Генерация интерфейсов и коннекторов между модулями (Phase 7) |
| **Security** | Path traversal prevention, reserved name validation |

### Текущий статус разработки

- ✅ **Research** — завершена
- ✅ **Design** — завершена
- ✅ **Plan** — завершена
- 🟢 **Implement Phase 1** — Core Abstractions Foundation ✅ (66 тестов)
- 🟢 **Implement Phase 2** — Factory Pattern и Mode Selection ✅ (31 тест)
- 🟢 **Implement Phase 3** — Simple Mode Refactoring ✅ (69 тестов)
- 🟢 **Implement Phase 4** — Modular Mode Skeleton ✅ (71 тест)
- 🟢 **Implement Phase 5** — Module Management System ✅ (97 тестов)
- 🟢 **Implement Phase 6** — Dependency Analysis System ✅ (66 тестов)
- 🟢 **Implement Phase 7** — Integration Build System ✅ (66 тестов)
- 🟢 **Implement Phase 8** — Modular Runner & Module Context ✅ (23 тестов)
- 🟢 **Implement Phase 9** — Testing & Documentation ✅ (197 тестов всего)
- 🟢 **Implement Phase 10** — Release v0.4.0 ✅ (258 тестов, 59% coverage)
- ⏳ **Review** — не начата

---

## Directory Structure

```
vibecraft_v0.3/
├── vibecraft-framework/       # Основной пакет фреймворка
│   ├── vibecraft/             # Исходный код
│   │   ├── core/              # Ядро: ABC, config, protocols, exceptions
│   │   │   ├── __init__.py
│   │   │   ├── base_bootstrapper.py
│   │   │   ├── base_runner.py
│   │   │   ├── config.py
│   │   │   ├── exceptions.py
│   │   │   ├── protocols.py
│   │   │   ├── factory.py
│   │   │   └── migrations.py
│   │   ├── modes/             # Режимы: simple/, modular/
│   │   │   ├── __init__.py
│   │   │   ├── simple/        # Simple mode (legacy)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── bootstrapper.py
│   │   │   │   └── runner.py
│   │   │   └── modular/       # Modular mode (Phase 4-7)
│   │   │       ├── __init__.py
│   │   │       ├── bootstrapper.py
│   │   │       ├── runner.py
│   │   │       ├── structure.py
│   │   │       ├── plan_generator.py
│   │   │       ├── module_manager.py      ✅ Phase 5
│   │   │       ├── module_registry.py     ✅ Phase 5-6
│   │   │       ├── dependency_analyzer.py ✅ Phase 6
│   │   │       ├── integration_manager.py ✅ Phase 7
│   │   │       ├── context_manager.py     ✅ Phase 8 (NEW)
│   │   │       ├── validation.py          ✅ Phase 5
│   │   │       └── security.py            ✅ Phase 5
│   │   ├── adapters/          # Clipboard adapter
│   │   ├── templates/         # Jinja2 templates
│   │   ├── cli.py             # CLI entry point (click)
│   │   ├── bootstrapper.py    # Legacy re-export
│   │   ├── runner.py          # Legacy re-export
│   │   └── context_manager.py # Context management
│   ├── tests/                 # Тесты фреймворка
│   │   └── unit/
│   ├── pyproject.toml         # Package config
│   └── README.md              # Документация
│
├── docs/                      # Документация проекта
│   ├── context.md             # Auto-generated project context
│   ├── research.md            # Research document
│   ├── stack.md               # Technology stack & architecture
│   ├── design/
│   │   └── architecture.md    # C4 diagrams, ADR decisions
│   └── plans/
│       ├── phase_1.md - phase_7.md
│       ├── pre_check_phase_*.md
│       ├── red_result_phase_*.md
│       ├── green_result_phase_*.md
│       └── code_review_phase_*.md
│
├── src/                       # Test directory for generated projects
│   └── tests/
│       ├── phase_1/
│       ├── phase_2/
│       ├── phase_3/
│       ├── phase_4/
│       ├── phase_5/           # Phase 5 tests (97 tests)
│       ├── phase_6/           # Phase 6 tests (66 tests)
│       ├── phase_7/           # Phase 7 tests (66 tests)
│       └── phase_8/           # Phase 8 tests (23 tests) ✅ NEW
│
├── modules/                   # Module directory (modular mode)
│
├── integration/               # Generated integration layer (Phase 7)
│   ├── interfaces.py
│   └── connectors/
│
├── .vibecraft/                # Vibecraft metadata
│   ├── manifest.json
│   ├── modules-registry.json
│   ├── agents/
│   ├── prompts/
│   ├── skills/
│   └── snapshots/
│
└── QWEN.md                    # This file
```

---

## Technology Stack

### Core Dependencies

```toml
# Required (все режимы)
click>=8.1         # CLI framework
jinja2>=3.1        # Template engine
pyyaml>=6.0        # YAML parsing
rich>=13.0         # Terminal formatting
pyperclip>=1.8     # Clipboard operations

# Optional (modular mode)
pydantic>=2.5      # Data validation
networkx>=3.2      # Dependency graph analysis

# Test dependencies
pytest>=8.0
pytest-cov>=4.0
pytest-mock>=3.12
mypy>=1.0          # Type checking
ruff>=0.1          # Linting
```

### Architecture Principles

| Principle | Application |
|-----------|-------------|
| **SOLID** | Все 5 принципов применяются строго |
| **Factory Pattern** | `BootstrapperFactory` для mode selection |
| **Strategy Pattern** | Разные runners для разных режимов |
| **Builder Pattern** | `DevelopmentPlanBuilder` для планов |
| **Repository Pattern** | `ModuleRegistry` для module registry |
| **Validator Pattern** | `ModuleValidator`, `SecurityValidator` |

---

## Building and Running

### Installation

```bash
cd vibecraft-framework

# Install with test dependencies
pip install -e ".[test]"

# Or install modular dependencies separately
pip install pydantic>=2.5 networkx>=3.2
```

### Running Tests

```bash
# Phase 1 core tests (66 tests)
pytest tests/unit/core/ -v

# Phase 7 tests (66 tests)
pytest ../src/tests/phase_7/ -v

# All tests with coverage
pytest tests/ ../src/tests/phase_*/ --cov=vibecraft --cov-report=html
```

### CLI Commands

```bash
# Check environment
vibecraft doctor

# Initialize project
vibecraft init -r docs/research.md -s docs/stack.md
vibecraft init -r docs/research.md -s docs/stack.md --mode modular

# Module management (modular mode)
vibecraft module create auth -d "Authentication module"
vibecraft module list
vibecraft module init auth
vibecraft module status auth

# Dependency analysis (Phase 6)
vibecraft integrate analyze

# Integration build (Phase 7)
vibecraft integrate build

# Run skills
vibecraft run research
vibecraft run design
vibecraft run plan
vibecraft run implement --phase 1
vibecraft run review

# Status and context
vibecraft status
vibecraft context
vibecraft context --skill implement

# Rollback
vibecraft snapshots
vibecraft rollback
vibecraft rollback 1

# Export
vibecraft export
vibecraft export --format zip
```

---

## Development Conventions

### Code Style

```bash
# Type checking
mypy vibecraft/ --ignore-missing-imports

# Formatting
black vibecraft/ tests/
isort vibecraft/ tests/

# Linting
ruff check vibecraft/ tests/
```

### Type Hints

Все публичные API должны иметь type hints:

```python
def create_module(
    name: str,
    description: str,
    dependencies: list[str] | None = None
) -> dict[str, Any]:
    """Create a new module."""
    ...
```

### Testing Practices

| Practice | Description |
|----------|-------------|
| **TDD-First** | Сначала тесты (RED), потом реализация (GREEN) |
| **Coverage** | 95%+ для core и modes, 100% для нового кода |
| **Fixtures** | Использовать `conftest.py` для общих фикстур |
| **Isolation** | Каждый тест независим, использует `tmp_path` |
| **Immutability** | Тесты в `src/tests/` locked после approval |

### Commit Conventions

```
feat: добавить IntegrationManager
fix: исправить баг в ModuleRegistry
docs: обновить README.md
test: добавить тесты для IntegrationManager
refactor: рефакторинг ModuleRegistry
```

---

## Key Components

### Core Modules

| Module | File | Responsibility |
|--------|------|----------------|
| `BaseBootstrapper` | `core/base_bootstrapper.py` | ABC для всех bootstrappers |
| `BaseRunner` | `core/base_runner.py` | ABC для всех runners |
| `VibecraftConfig` | `core/config.py` | Pydantic модели конфигурации |
| `BootstrapperFactory` | `core/factory.py` | Factory для создания bootstrappers |
| `ModuleError` | `core/exceptions.py` | Exception hierarchy |
| `Protocols` | `core/protocols.py` | Structural subtyping (Creatable, Listable, Buildable) |

### Modes

| Mode | Location | Description |
|------|----------|-------------|
| **Simple** | `modes/simple/` | Legacy v0.3 workflow, для маленьких проектов |
| **Modular** | `modes/modular/` | Новый режим с модулями, для больших проектов |

### Modular Mode Components

| Component | File | Responsibility |
|-----------|------|----------------|
| `ModularBootstrapper` | `modes/modular/__init__.py` | Bootstrap modular projects |
| `ModularRunner` | `modes/modular/runner.py` | Module-aware skill execution |
| `ModuleManager` | `modes/modular/module_manager.py` | CRUD операции с модулями ✅ Phase 5 |
| `ModuleRegistry` | `modes/modular/module_registry.py` | Central module registry ✅ Phase 5-6 |
| `DependencyAnalyzer` | `modes/modular/dependency_analyzer.py` | Dependency validation ✅ Phase 6 |
| `IntegrationManager` | `modes/modular/integration_manager.py` | Interface/connector generation ✅ Phase 7 |
| `ModuleValidator` | `modes/modular/validation.py` | Name validation ✅ Phase 5 |
| `SecurityValidator` | `modes/modular/security.py` | Path security ✅ Phase 5 |
| `PlanGenerator` | `modes/modular/plan_generator.py` | Development plan generation |

---

## Configuration Files

### pyproject.toml

```toml
[project]
name = "vibecraft"
version = "0.3.0"
requires-python = ">=3.10"
dependencies = [
    "click>=8.1",
    "jinja2>=3.1",
    "pyyaml>=6.0",
    "rich>=13.0",
    "pyperclip>=1.8",
]

[project.optional-dependencies]
modular = ["pydantic>=2.5", "networkx>=3.2"]
test = ["pytest>=8.0", "pytest-cov>=4.0"]
```

### .vibecraft/manifest.json

```json
{
  "project_name": "Vibecraft Framework v0.4 - Multi-Mode Architecture",
  "project_type": ["web", "api", "cli"],
  "current_phase": "implement",
  "phases_completed": ["research", "design", "plan", "implement_phase_1", "implement_phase_2", "implement_phase_3", "implement_phase_4", "implement_phase_5", "implement_phase_6", "implement_phase_7"]
}
```

---

## Architecture Decision Records (ADR)

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Dual-Mode Architecture | Accepted ✅ |
| ADR-002 | Factory Pattern для Mode Selection | Accepted ✅ |
| ADR-003 | Pydantic для Config Models | Accepted ✅ |
| ADR-004 | NetworkX для Dependency Graph | Accepted ✅ |
| ADR-005 | Clipboard-Only Backend | Accepted ✅ |
| ADR-006 | Module Structure (.module.json) | Accepted ✅ |
| ADR-007 | Central Module Registry | Accepted ✅ |
| ADR-008 | TDD-First Implementation | Accepted ✅ |
| ADR-009 | Layered Architecture with Strict Boundaries | Accepted ✅ |
| ADR-010 | Optional Dependencies for Modular Features | Accepted ✅ |
| ADR-011 | ASCII-Only CLI Output | Accepted ✅ |
| ADR-012 | Manifest.json Versioning | Accepted ✅ |

---

## Test Results

| Phase | Tests | Status | Coverage |
|-------|-------|--------|----------|
| **Phase 1** | 66 | ✅ PASS | Core abstractions |
| **Phase 2** | 31 | ✅ PASS | Factory pattern |
| **Phase 3** | 69 | ✅ PASS | Simple mode refactoring |
| **Phase 4** | 71 | ✅ PASS | Modular mode skeleton |
| **Phase 5** | 97 | ✅ PASS | Module management |
| **Phase 6** | 66 | ✅ PASS | Dependency analysis |
| **Phase 7** | 66 | ✅ PASS | Integration build |
| **Phase 8** | 23 | ✅ PASS | Modular Runner & Module Context |
| **Phase 9** | 48 | ✅ PASS | Testing & Documentation |

**Total:** 197 tests ✅

**Code Quality:**
- mypy: clean ✅
- ruff: clean ✅
- coverage: 49% overall (98%+ for new modular code) ✅

---

## Known Issues and Limitations

| Issue | Impact | Workaround |
|-------|--------|------------|
| `datetime.utcnow()` deprecated | Python 3.14+ | Мигрировать на `datetime.now(datetime.UTC)` |
| Clipboard requires pyperclip | All modes | Установить `pip install pyperclip` |
| Windows Unicode | PowerShell | Использовать ASCII-символы, Rich Console |

---

## Testing Strategy

### Test Categories

| Category | Location | Coverage Goal |
|----------|----------|---------------|
| **Unit Tests** | `tests/unit/` | 95%+ для core и modes |
| **Integration Tests** | `tests/integration/` | Все основные workflows |
| **Regression Tests** | `tests/regression/` | Все old bugs покрыты |

### Running Specific Tests

```bash
# Phase 7 tests (integration build)
pytest ../src/tests/phase_7/ -v  # 66 tests

# All tests with coverage
pytest tests/ ../src/tests/phase_*/ --cov=vibecraft --cov-report=xml
```

---

## File Immutability Rules

| File/Directory | Who Can Modify | Locked After |
|----------------|----------------|--------------|
| `src/tests/` | `tdd_writer` only | tdd_writer approval |
| ADR decisions | New ADR only | Acceptance |
| `docs/stack.md` | Architect | Design phase complete |
| `docs/research.md` | Researcher | Research phase complete |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EDITOR` / `VISUAL` | `nano` | Editor для human gate |
| `PYTHONIOENCODING` | `utf-8` | Console encoding (auto-set on Windows) |
| `VIBECRAFT_PROJECT_ROOT` | - | Override project root (for testing) |
| `VIBECRAFT_DEBUG` | `0` | Enable debug logging |

---

## Related Documentation

| Document | Location |
|----------|----------|
| **Research** | `docs/research.md` |
| **Stack** | `docs/stack.md` |
| **Architecture (C4)** | `docs/design/architecture.md` |
| **Development Plans** | `docs/plans/phase_*.md` |
| **Phase Results** | `docs/plans/green_result_phase_*.md` |
| **Code Review** | `docs/plans/code_review_phase_*.md` |

---

## Quick Commands Cheat Sheet

```bash
# === Installation ===
cd vibecraft-framework
pip install -e ".[test]"
pip install pydantic>=2.5 networkx>=3.2  # for modular mode

# === Project Init ===
vibecraft doctor
vibecraft init -r docs/research.md -s docs/stack.md
vibecraft init -r docs/research.md -s docs/stack.md --mode modular

# === Module Management (Modular Mode) ===
vibecraft module create auth -d "Authentication"
vibecraft module create database -d "Database layer"
vibecraft module create auth --depends-on database
vibecraft module list
vibecraft module init auth
vibecraft module status auth

# === Dependency Analysis (Phase 6) ===
vibecraft integrate analyze

# === Integration Build (Phase 7) ===
vibecraft integrate build

# === Development Workflow ===
vibecraft run research
vibecraft run design
vibecraft run plan
vibecraft run implement --phase 1
vibecraft complete 1
vibecraft context

# === Testing ===
pytest tests/unit/core/ -v       # Phase 1: 66 tests
pytest ../src/tests/phase_7/ -v  # Phase 7: 66 tests
pytest ../src/tests/phase_8/ -v  # Phase 8: 23 tests
pytest tests/ ../src/tests/phase_*/ --cov=vibecraft  # All tests

# === Code Quality ===
mypy vibecraft/ --ignore-missing-imports  # Type checking
ruff check vibecraft/ tests/              # Linting

# === Module-Aware Skills (Phase 8) ===
vibecraft run implement --phase 1 --module auth
vibecraft run research --module database
```

---

## ✅ Phase 10 Complete: Release v0.4.0

**All objectives completed:**

1. ✅ Added tests for remaining modular modules (61 new tests)
   - test_module_manager.py: 19 tests
   - test_module_registry.py: 21 tests  
   - test_integration_manager.py: 21 tests

2. ✅ Fixed all deprecation warnings (datetime.utcnow() → datetime.now(timezone.utc))
   - Fixed in 4 files: __init__.py, context_manager.py, exporter.py, module_registry.py

3. ✅ Prepared comprehensive release notes (RELEASE_NOTES_v0.4.0.md)

4. ✅ Updated version to 0.4.0 in setup.py and pyproject.toml

5. ✅ Final test run: 258 tests passing, 59% coverage

**Ready for PyPI publication** 🚀

---

*Generated by Vibecraft Framework v0.4 | Last updated: 2026-02-27 | Phase 10 Complete ✅*
