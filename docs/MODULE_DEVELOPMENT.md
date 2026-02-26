# Vibecraft Framework — Module Development Guide

## Introduction

Это руководство описывает процесс разработки модулей в Vibecraft Framework Modular Mode.

## Module Lifecycle

```
planned → in_progress → testing → completed
```

### Status Transitions

| From | To | Trigger |
|------|-----|---------|
| `planned` | `in_progress` | Начата разработка (phase 1) |
| `in_progress` | `testing` | Реализация завершена |
| `testing` | `completed` | Все тесты прошли, code review approved |
| `completed` | `in_progress` | Bug fix или новая функциональность |

## Step-by-Step: Создание нового модуля

### Шаг 1: Планирование

Перед созданием модуля определите:
- **Назначение**: Что делает модуль?
- **Ответственность**: Какую задачу решает?
- **Зависимости**: Какие модули нужны?
- **Экспорты**: Что модуль предоставляет наружу?

Пример документации:
```markdown
## Module: auth

**Purpose**: Authentication and authorization

**Responsibilities**:
- User login/logout
- Token management
- Permission verification

**Dependencies**: database

**Exports**: AuthService, login, logout, verify_token
```

### Шаг 2: Создание модуля

```bash
vibecraft module create auth \
  -d "Authentication and authorization module" \
  --depends-on database
```

Это создаст запись в реестре, но не создаст файлы.

### Шаг 3: Инициализация модуля

```bash
vibecraft module init auth
```

Это создаст структуру директорий:
```
modules/auth/
├── .module.json
├── context.md
├── src/
├── tests/
└── plans/
```

### Шаг 4: Проверка зависимостей

Перед началом разработки убедитесь, что зависимости готовы:

```bash
vibecraft module status auth
```

Если зависимости не готовы:
```bash
vibecraft module status database
# Если database не completed → разработайте сначала его
```

### Шаг 5: Research для модуля

```bash
vibecraft run research --module auth
```

Исследование модуля включает:
- Анализ предметной области
- Исследование лучших практик
- Определение архитектурных паттернов

Результат: `modules/auth/plans/research.md`

### Шаг 6: Plan для модуля

```bash
vibecraft run plan --module auth
```

Планирование разбивает модуль на фазы:
- Phase 1: Базовая структура
- Phase 2: Основная логика
- Phase 3: Интеграция с зависимостями
- Phase 4: Оптимизация

Результат: `modules/auth/plans/phase_1.md`, `phase_2.md`, etc.

### Шаг 7: TDD Implementation

Для каждой фазы:

#### RED Phase
```bash
vibecraft run implement --phase 1 --module auth
```

1. Pre-check: проверка окружения
2. Write tests: создание тестов в `modules/auth/tests/phase_1/`
3. Run tests: подтверждение, что тесты FAIL (RED)

#### GREEN Phase
4. Implement: написание кода в `modules/auth/src/`
5. Run tests: подтверждение, что тесты PASS (GREEN)

#### REVIEW Phase
6. Code review: проверка качества

Повторите для каждой фазы.

### Шаг 8: Обновление контекста

После каждой фазы обновляйте `context.md`:

```markdown
## Phase 1 Complete ✅

**Completed**: 2026-02-27

**Implementation**:
- Created AuthService class
- Implemented login function
- Added token generation

**Tests**: 15 tests, 100% coverage

**Notes**:
- Using bcrypt for password hashing
- JWT tokens with 15min expiry
```

### Шаг 9: Завершение модуля

Когда все фазы завершены:

```bash
vibecraft module status auth
```

Статус должен быть `completed`.

## Module Structure

### .module.json

```json
{
  "name": "auth",
  "description": "Authentication and authorization module",
  "dependencies": ["database"],
  "exports": [
    "AuthService",
    "login",
    "logout",
    "verify_token"
  ],
  "status": "in_progress",
  "metadata": {
    "owner": "backend-team",
    "priority": "high",
    "estimated_days": 5,
    "created_at": "2026-02-27"
  }
}
```

### src/

Исходный код модуля. Рекомендуемая структура:

```
modules/auth/src/
├── __init__.py          # Публичные экспорты
├── services/
│   ├── __init__.py
│   └── auth_service.py  # AuthService
├── functions/
│   ├── __init__.py
│   ├── login.py         # login()
│   ├── logout.py        # logout()
│   └── verify.py        # verify_token()
└── utils/
    └── token_utils.py   # Внутренние утилиты
```

### tests/

Тесты модуля:

```
modules/auth/tests/
├── __init__.py
├── conftest.py          # Общие фикстуры
├── phase_1/
│   ├── __init__.py
│   └── test_auth_init.py
├── phase_2/
│   ├── __init__.py
│   └── test_login.py
└── integration/
    └── test_auth_integration.py
```

### plans/

Планы и результаты фаз:

```
modules/auth/plans/
├── research.md
├── phase_1.md
├── pre_check_phase_1.md
├── red_result_phase_1.md
├── green_result_phase_1.md
├── code_review_phase_1.md
├── phase_2.md
└── ...
```

## Dependencies Management

### Объявление зависимостей

В `.module.json`:
```json
{
  "dependencies": ["database", "config"]
}
```

### Использование зависимостей

В коде модуля:
```python
# modules/auth/src/services/auth_service.py

# Импорт из зависимого модуля
from modules.database.src.connection import DatabaseConnection

class AuthService:
    def __init__(self, db: DatabaseConnection):
        self.db = db
```

### Проверка зависимостей

```bash
# Проверить все зависимости
vibecraft integrate analyze

# Проверить конкретный модуль
vibecraft module status auth
```

## Best Practices

### 1. Single Responsibility

Каждый модуль должен решать одну задачу.

✅ **Good**: `auth` — только аутентификация
❌ **Bad**: `auth` — аутентификация + логирование + кэширование

### 2. Interface Segregation

Экспортируйте минимальный необходимый интерфейс.

✅ **Good**:
```json
"exports": ["AuthService", "login", "logout"]
```

❌ **Bad**:
```json
"exports": ["AuthService", "login", "logout", "_internal_helper", "_utils"]
```

### 3. Dependency Inversion

Зависите от абстракций, не от реализаций.

✅ **Good**:
```python
from database import DatabaseProtocol  # Protocol/Interface
```

❌ **Bad**:
```python
from database import ConcreteDatabase  # Concrete implementation
```

### 4. Test Isolation

Тесты модуля должны быть изолированы.

✅ **Good**: Mock зависимостей в тестах
❌ **Bad**: Реальные вызовы к другим модулям в unit тестах

### 5. Documentation

Документируйте публичные API.

✅ **Good**:
```python
def login(username: str, password: str) -> AuthToken:
    """
    Authenticate user and return token.
    
    Args:
        username: User's username
        password: User's password
        
    Returns:
        AuthToken for authenticated session
        
    Raises:
        AuthenticationError: If credentials invalid
    """
```

## Common Issues

### Issue: Module not found

**Cause**: Модуль не инициализирован

**Solution**:
```bash
vibecraft module init <module_name>
```

### Issue: Circular dependency

**Cause**: Модуль A зависит от B, B зависит от A

**Solution**:
1. Выделите общую логику в отдельный модуль C
2. A и B зависят от C
3. Удалите циклическую зависимость

### Issue: Export not available

**Cause**: Экспорт не указан в `.module.json`

**Solution**:
```json
{
  "exports": ["NewService"]  // Добавьте экспорт
}
```

### Issue: Tests fail after implementation

**Cause**: Implementation не соответствует тестам

**Solution**:
1. Проверьте `red_result_phase_X.md` — тесты должны FAIL до реализации
2. Проверьте `green_result_phase_X.md` — тесты должны PASS после
3. Если тесты всё ещё FAIL → исправьте implementation

## Module Checklist

Перед тем как пометить модуль как `completed`:

- [ ] Все фазы реализованы
- [ ] Все тесты проходят (GREEN)
- [ ] Code review approved
- [ ] `context.md` обновлён
- [ ] `.module.json` актуален
- [ ] Зависимые модули могут импортировать экспорты
- [ ] Документация полная

## See Also

- [MODULAR_MODE.md](./MODULAR_MODE.md) — Overview modular mode
- [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) — Integration build
- [MIGRATION_SIMPLE_TO_MODULAR.md](./MIGRATION_SIMPLE_TO_MODULAR.md) — Migration guide

---

*Vibecraft Framework v0.4 | Last updated: 2026-02-27*
