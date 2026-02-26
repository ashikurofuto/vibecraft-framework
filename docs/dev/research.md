# Vibecraft Framework v0.4 - Multi-Mode Architecture

## Project Vision

Расширение Vibecraft Framework для поддержки двух режимов разработки:
- **Simple Mode** (текущий) - для маленьких проектов с линейной структурой
- **Modular Mode** (новый) - для больших проектов с модульной архитектурой

Ключевая идея: один фреймворк, два подхода к разработке, с возможностью выбора режима при инициализации проекта.

---

## Current State Summary (v0.3.0)

### Existing Architecture

**Core Components:**
- `vibecraft/bootstrapper.py` - создает проект из research.md + stack.md, генерирует агенты и skills
- `vibecraft/runner.py` - запускает skills, строит промпт из шаблонов, копирует в clipboard
- `vibecraft/context_manager.py` - управляет фазами проекта, обновляет context.md
- `vibecraft/cli.py` - CLI entry point: init, run, status, doctor, rollback, export
- `vibecraft/doctor.py` - проверка окружения и зависимостей
- `vibecraft/rollback.py` - откат к предыдущему состоянию
- `vibecraft/exporter.py` - экспорт контекста проекта
- `vibecraft/adapters/clipboard_adapter.py` - единственный адаптер (clipboard-only by design)

**Current Workflow:**
```bash
# Инициализация проекта
vibecraft init -r research.md -s stack.md

# Фазы разработки (промпт → clipboard → LLM)
vibecraft run research
vibecraft run design
vibecraft run plan
vibecraft run implement --phase 1
vibecraft run review

# Вспомогательные команды
vibecraft doctor    # Проверка окружения
vibecraft status    # Текущее состояние
vibecraft rollback  # Откат изменений
```

**Generated Project Structure:**
```
project/
├── .vibecraft/
│   ├── manifest.json          # Состояние проекта, completed phases
│   ├── agents/                # 8 core + conditional agents
│   │   ├── researcher.md
│   │   ├── architect.md
│   │   ├── planner.md
│   │   ├── plan_reviewer.md
│   │   ├── pre_checker.md
│   │   ├── tdd_writer.md
│   │   ├── implementer.md
│   │   └── code_reviewer.md
│   ├── skills/                # 5 core skills (YAML)
│   │   ├── research_skill.yaml
│   │   ├── design_skill.yaml
│   │   ├── plan_skill.yaml
│   │   ├── implement_skill.yaml  # 6 phases: pre_check, write_tests, run_red, implement, run_green, review
│   │   └── review_skill.yaml
│   ├── prompts/               # Generated prompts (history)
│   └── snapshots/             # Rollback snapshots
├── docs/
│   ├── research.md            # Copied from input
│   ├── stack.md               # Copied from input
│   ├── context.md             # Auto-generated, updated each phase
│   ├── design/                # Design artifacts
│   └── plans/                 # Development plans
└── src/
    └── tests/                 # Test files
```

**Key Features:**
- **TDD Pipeline:** RED/GREEN phases - write tests first, then implementation
- **Agent System:** 8 core agents (researcher, architect, planner, etc.) + conditional agents (security, performance, UX)
- **Skill Orchestration:** Each skill = sequence of agent calls
- **Phase Tracking:** manifest.json tracks completed phases
- **Context Management:** context.md auto-updates with project state
- **Clipboard Integration:** All prompts copy to clipboard (no direct LLM calls)
- **Jinja2 Templates:** Flexible agent and skill templates
- **Rollback System:** Snapshots before each phase

**Technology Stack:**
```python
# Core dependencies (pyproject.toml)
click>=8.1         # CLI framework
jinja2>=3.1        # Template engine
pyyaml>=6.0        # YAML parsing
rich>=13.0         # Terminal formatting
pyperclip>=1.8     # Clipboard operations

# Test dependencies
pytest>=8.0
pytest-cov>=4.0
```

**Test Coverage:**
- 83 unit tests, 100% passing
- Coverage: bootstrapper, runner, context_manager, doctor, rollback, exporter, adapters
- Regression tests for all major bugs

**Project Type Detection:**
- Парсит research.md и stack.md
- Определяет project_type: web, api, cli, game, mobile, database
- Добавляет conditional agents на основе типа проекта

### What Works Well

✅ **Simple projects:** Отлично работает для маленьких проектов  
✅ **TDD workflow:** RED/GREEN phases реально работают  
✅ **Context preservation:** context.md всегда актуален  
✅ **Clipboard approach:** Не зависим от конкретного LLM API  
✅ **Windows support:** UTF-8 encoding fixes работают  
✅ **Type detection:** Автоматически определяет тип проекта  

### Current Limitations (Why v0.4 is needed)

❌ **Monolithic structure:** Весь проект в одной директории src/  
❌ **No modules:** Нельзя разбить большой проект на части  
❌ **No dependency management:** Между частями проекта  
❌ **No development plan:** Для больших проектов нужен поэтапный план  
❌ **Single mode only:** Нет выбора между simple/complex подходом  
❌ **No integration system:** Нет способа собрать модули в единое целое  
❌ **Team collaboration:** Сложно работать нескольким разработчикам  

### Design Constraints to Respect

**Must maintain:**
- Clipboard-only approach (no direct LLM calls)
- Simple mode as default
- Full backward compatibility
- Windows compatibility
- Agent-driven architecture
- Jinja2 templating system

**Must NOT break:**
- Existing CLI commands
- manifest.json format (можно расширить, но не сломать)
- Template structure
- Test suite

### Files that Need Refactoring

**To move/reorganize:**
- `vibecraft/bootstrapper.py` → `vibecraft/modes/simple/bootstrapper.py`

**To create new:**
- `vibecraft/core/base_bootstrapper.py` (ABC)
- `vibecraft/core/config.py` (ProjectMode, VibecraftConfig)
- `vibecraft/modes/modular/bootstrapper.py`
- `vibecraft/modes/modular/module_manager.py`
- `vibecraft/modes/modular/integration_manager.py`
- `vibecraft/modes/modular/plan_generator.py`

**To update:**
- `vibecraft/cli.py` (add --mode, module commands)
- `vibecraft/runner.py` (support both modes)

### Migration Strategy

**Phase 0 (Refactoring):**
1. Create new structure: `core/` and `modes/`
2. Move existing code to `modes/simple/`
3. Create abstract base classes
4. Update imports, tests
5. Ensure 100% backward compatibility

**After Phase 0:**
- `vibecraft init` still works exactly as before
- All tests pass
- Zero breaking changes

---

## Problem Statement

### Текущие ограничения
1. Vibecraft создает монолитную структуру проекта
2. Для больших проектов нет разбивки на модули
3. Нет управления зависимостями между частями проекта
4. Сложно масштабировать разработку на команду
5. Нет плана разработки с фазами для крупных проектов

### Целевая аудитория
- **Simple Mode**: indie-разработчики, MVP, прототипы, маленькие утилиты
- **Modular Mode**: enterprise-проекты, SaaS-платформы, большие команды, долгосрочная разработка

---

## Goals and Success Metrics

### Primary Goals
1. Сохранить полную обратную совместимость с текущим функционалом
2. Добавить modular режим без усложнения simple режима
3. Реализовать полный цикл работы с модулями (create → develop → integrate)
4. Создать систему управления зависимостями между модулями

### Success Metrics
- ✅ Simple mode работает без изменений
- ✅ Возможность создать проект в modular режиме одной командой
- ✅ Минимум 5 модулей в тестовом проекте успешно интегрируются
- ✅ Development plan автоматически генерируется из research.md
- ✅ 100% test coverage для нового функционала

---

## Core Features

### Feature 1: Dual-Mode Architecture
**Description:** Базовая архитектура для поддержки двух режимов

**Components:**
- `BaseBootstrapper` - абстрактный класс для всех режимов
- `ProjectMode` enum - simple | modular
- `VibecraftConfig` - конфигурация проекта
- Mode selector в CLI

**User Flow:**
```bash
# Simple mode (default)
vibecraft init -r research.md -s stack.md

# Modular mode (explicit)
vibecraft init -r research.md -s stack.md --mode modular
```

---

### Feature 2: Module Management System
**Description:** Полный цикл работы с модулями

**Components:**
- `ModuleManager` - создание, список, статус модулей
- Module structure generator
- Module registry (JSON)
- Per-module research files

**User Flow:**
```bash
vibecraft module create auth --description "Authentication module"
vibecraft module list
vibecraft module init auth
vibecraft module status auth
```

**Module Structure:**
```
modules/auth/
├── .module.json      # Конфигурация модуля
├── research.md       # Research для модуля
├── context.md        # Контекст разработки
├── src/              # Исходники
└── tests/            # Тесты
```

---

### Feature 3: Development Plan Generator
**Description:** Автоматическое создание плана разработки из research.md

**Components:**
- `DevelopmentPlanGenerator` - анализ research и создание плана
- Module extraction logic
- Dependency graph builder
- Build order calculator

**Output:**
```markdown
# Development Plan

## Phase 1: Core Infrastructure (Week 1-2)
- Module: database
- Module: config
- Module: logging

## Phase 2: Business Logic (Week 3-5)
- Module: auth (depends on: database)
- Module: users (depends on: auth, database)

## Phase 3: API Layer (Week 6-7)
- Module: rest_api (depends on: auth, users)
```

---

### Feature 4: Module Integration System
**Description:** Связывание модулей в единый проект

**Components:**
- `IntegrationManager` - управление интеграцией
- Dependency analyzer
- Interface generator
- Build orchestrator

**User Flow:**
```bash
vibecraft integrate analyze   # Анализ зависимостей
vibecraft integrate build     # Сборка проекта
```

**Generated Files:**
```
integration/
├── interfaces.py        # Типы для всех модулей
├── module_registry.py   # Реестр модулей
└── connectors/
    ├── auth_to_users.py
    └── users_to_api.py
```

---

### Feature 5: Modular Runner
**Description:** Запуск skills в контексте модулей

**Components:**
- `ModularRunner` - runner для modular режима
- Module context manager
- Per-module skill execution

**User Flow:**
```bash
# Работа с конкретным модулем
vibecraft run implement --module auth --phase 1

# Работа с общим проектом
vibecraft run design
```

---

## Technical Architecture

### Directory Structure (Modular Mode)
```
my-big-project/
├── .vibecraft/
│   ├── config.json              # mode: "modular"
│   ├── manifest.json            # Текущее состояние
│   ├── modules-registry.json   # Список модулей
│   ├── development-plan.md     # План разработки
│   ├── agents/                 # Агенты
│   ├── skills/                 # Skills
│   └── research/
│       ├── project-research.md
│       └── project-stack.md
├── modules/                     # Модули проекта
│   ├── auth/
│   ├── users/
│   └── products/
├── shared/                      # Общий код
│   ├── types/
│   ├── utils/
│   └── config/
├── integration/                 # Связи между модулями
│   ├── interfaces.py
│   └── connectors/
├── docs/
│   ├── research.md
│   ├── stack.md
│   ├── context.md
│   └── architecture.md
└── project.json                # Манифест проекта
```

### Configuration Files

**`.vibecraft/config.json`:**
```json
{
  "mode": "modular",
  "version": "0.4.0",
  "project_name": "my-app",
  "project_type": "web",
  "created_at": "2026-02-26T12:00:00",
  
  "modular": {
    "modules_dir": "modules",
    "shared_dir": "shared",
    "integration_dir": "integration",
    "modules": [
      "auth",
      "users",
      "products"
    ]
  }
}
```

**`modules/auth/.module.json`:**
```json
{
  "name": "auth",
  "description": "Authentication and authorization",
  "status": "in_progress",
  "dependencies": ["database", "config"],
  "exports": ["AuthService", "login", "logout"],
  "created_at": "2026-02-26T13:00:00",
  "phases_completed": [1, 2]
}
```

**`.vibecraft/modules-registry.json`:**
```json
{
  "modules": [
    {
      "name": "auth",
      "path": "modules/auth",
      "status": "in_progress"
    }
  ],
  "dependencies": {
    "auth": ["database", "config"],
    "users": ["auth", "database"]
  },
  "build_order": ["database", "config", "auth", "users"]
}
```

---

## Development Phases

### Phase 0: Refactoring (Week 1)
**Goal:** Подготовить архитектуру для dual-mode

**Tasks:**
- [ ] Создать `vibecraft/core/` с базовыми классами
- [ ] Создать `vibecraft/modes/` структуру
- [ ] Перенести текущий код в `modes/simple/`
- [ ] Создать `BaseBootstrapper` abstract class
- [ ] Создать `VibecraftConfig` dataclass
- [ ] Обновить tests для новой структуры

**Deliverables:**
- `vibecraft/core/base_bootstrapper.py`
- `vibecraft/core/config.py`
- `vibecraft/modes/simple/bootstrapper.py`
- `vibecraft/modes/modular/` (заглушка)

---

### Phase 1: Mode Selection (Week 2)
**Goal:** Добавить выбор режима в CLI

**Tasks:**
- [ ] Обновить `cli.py` с `--mode` параметром
- [ ] Реализовать mode selection logic
- [ ] Создать config.json template
- [ ] Создать `ModularBootstrapper` skeleton
- [ ] Написать integration tests

**Deliverables:**
- Команда `vibecraft init --mode modular` работает
- `.vibecraft/config.json` создается
- Simple mode остается по умолчанию

---

### Phase 2: Modular Structure (Week 3)
**Goal:** Создать базовую структуру modular проекта

**Tasks:**
- [ ] Реализовать `ModularBootstrapper.run()`
- [ ] Создать directory structure generator
- [ ] Реализовать `DevelopmentPlanGenerator`
- [ ] Создать modules-registry.json template
- [ ] Создать Jinja2 templates для modular режима

**Deliverables:**
- Полная структура modular проекта создается
- `development-plan.md` генерируется
- `modules-registry.json` инициализируется

---

### Phase 3: Module Management (Week 4-5)
**Goal:** Реализовать полный цикл работы с модулями

**Tasks:**
- [ ] Создать `ModuleManager` class
- [ ] Реализовать `module create` command
- [ ] Реализовать `module list` command
- [ ] Реализовать `module init` command
- [ ] Создать `.module.json` template
- [ ] Создать per-module research template
- [ ] Написать unit tests для ModuleManager

**Deliverables:**
- `vibecraft module create` работает
- `vibecraft module list` показывает таблицу
- Каждый модуль имеет свою структуру

---

### Phase 4: Integration System (Week 6-7)
**Goal:** Связать модули в единый проект

**Tasks:**
- [ ] Создать `IntegrationManager` class
- [ ] Реализовать dependency analyzer
- [ ] Реализовать interface generator
- [ ] Реализовать build orchestrator
- [ ] Создать `integrate analyze` command
- [ ] Создать `integrate build` command
- [ ] Написать integration tests

**Deliverables:**
- `vibecraft integrate analyze` работает
- `vibecraft integrate build` создает финальный проект
- `integration/` директория генерируется

---

### Phase 5: Modular Runner (Week 8)
**Goal:** Адаптировать runner для работы с модулями

**Tasks:**
- [ ] Создать `ModularRunner` class
- [ ] Обновить `SkillRunner` для dual-mode
- [ ] Реализовать module context switching
- [ ] Обновить skills templates для modular режима
- [ ] Написать tests для modular runner

**Deliverables:**
- `vibecraft run implement --module auth` работает
- Skills выполняются в контексте модуля
- Context.md обновляется для каждого модуля

---

### Phase 6: Testing & Documentation (Week 9-10)
**Goal:** Полное покрытие тестами и документация

**Tasks:**
- [ ] Написать unit tests для всех новых компонентов
- [ ] Написать integration tests
- [ ] Создать `docs/MODULAR_MODE.md`
- [ ] Создать `docs/MODULE_DEVELOPMENT.md`
- [ ] Создать `docs/INTEGRATION_GUIDE.md`
- [ ] Обновить `README.md`
- [ ] Создать migration guide: simple → modular

**Deliverables:**
- 100% test coverage для нового кода
- Полная документация
- Примеры в `examples/modular/`

---

## User Stories

### Story 1: Indie Developer (Simple Mode)
**As** an indie developer  
**I want** to quickly bootstrap a small project  
**So that** I can focus on coding, not project setup

**Acceptance Criteria:**
- Simple mode работает как раньше
- Одна команда создает полную структуру
- Нет сложности с модулями

---

### Story 2: Tech Lead (Modular Mode)
**As** a tech lead in a big team  
**I want** to split the project into independent modules  
**So that** my team can work in parallel

**Acceptance Criteria:**
- Могу создать проект в modular режиме
- Могу создать 10+ модулей
- Каждый модуль независим
- Есть план разработки

---

### Story 3: Backend Developer (Module Development)
**As** a backend developer  
**I want** to work on my module independently  
**So that** I don't conflict with frontend developers

**Acceptance Criteria:**
- Могу инициализировать свой модуль
- Могу запускать skills только для моего модуля
- Мой context.md отдельный
- Могу видеть зависимости моего модуля

---

### Story 4: DevOps Engineer (Integration)
**As** a DevOps engineer  
**I want** to integrate all modules into final project  
**So that** we can deploy the application

**Acceptance Criteria:**
- Могу проанализировать зависимости
- Могу построить граф модулей
- Могу собрать финальный проект
- Все связи между модулями корректны

---

## Risks and Mitigation

### Risk 1: Breaking Changes
**Impact:** High  
**Probability:** Medium  
**Mitigation:**
- Сохранить full backward compatibility
- Simple mode остается default
- Extensive regression testing

### Risk 2: Complexity Creep
**Impact:** High  
**Probability:** High  
**Mitigation:**
- Держать simple mode простым
- Modular mode - opt-in
- Clear separation of concerns

### Risk 3: Module Dependencies Hell
**Impact:** Medium  
**Probability:** Medium  
**Mitigation:**
- Dependency analyzer с циклическими проверками
- Clear dependency declaration в .module.json
- Визуализация dependency graph

### Risk 4: Performance Degradation
**Impact:** Low  
**Probability:** Low  
**Mitigation:**
- Benchmarking tests
- Lazy loading модулей
- Efficient JSON parsing

---

## Open Questions

1. **Module Versioning:** Нужна ли версионность модулей?
2. **Shared Code:** Как управлять shared директорией?
3. **Testing Strategy:** Как тестировать интеграцию модулей?
4. **Migration Path:** Нужна ли автоматическая миграция simple → modular?
5. **Module Templates:** Создавать ли готовые шаблоны модулей (auth, api, db)?
6. **Team Collaboration:** Как синхронизировать работу нескольких разработчиков?
7. **CI/CD:** Нужны ли готовые pipeline для modular проектов?

---

## Future Enhancements (v0.5+)

1. **Visual Module Graph:** Web-интерфейс для визуализации модулей
2. **Module Templates:** Библиотека готовых модулей
3. **Auto-Migration:** Автоматическая конвертация simple → modular
4. **Module Marketplace:** Sharing модулей между проектами
5. **AI-Powered Planning:** LLM для автоматического создания development plan
6. **Real-time Collaboration:** Синхронизация между разработчиками
7. **Docker Integration:** Автоматическая контейнеризация модулей
8. **Kubernetes Manifests:** Генерация k8s манифестов для модулей

---

## Appendix

### Example Projects

**Simple Mode:**
- CLI utility
- Discord bot
- Small web scraper
- Personal blog

**Modular Mode:**
- E-commerce platform
- SaaS application
- Enterprise CRM
- Microservices backend

### Terminology

- **Mode:** Режим работы фреймворка (simple | modular)
- **Module:** Независимая единица кода с собственным research и tests
- **Integration:** Процесс связывания модулей в единый проект
- **Development Plan:** Автоматически сгенерированный план разработки
- **Module Registry:** JSON файл со списком всех модулей проекта
- **Build Order:** Последовательность разработки модулей с учетом зависимостей
