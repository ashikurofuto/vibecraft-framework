# Vibecraft Framework — Migration Guide: Simple to Modular

## Introduction

Это руководство описывает процесс миграции проекта из Simple Mode в Modular Mode.

## When to Migrate

Рассмотрите миграцию, если:

| Критерий | Simple Mode | Modular Mode |
|----------|-------------|--------------|
| **Файлов в проекте** | < 10 | > 10 |
| **Команда** | 1-2 разработчика | 3+ разработчиков |
| **Сборка** | < 1 минуты | > 1 минуты |
| **Зависимости** | Неявные | Требуют явного управления |
| **TDD циклы** | Один на проект | Несколько на модуль |

## Migration Overview

Процесс миграции:

1. **Анализ** текущей архитектуры
2. **Планирование** модульной структуры
3. **Создание** нового modular проекта
4. **Перенос** кода в модули
5. **Настройка** зависимостей
6. **Верификация** интеграции

## Step-by-Step Migration

### Шаг 1: Анализ текущей архитектуры

Изучите структуру Simple проекта:

```
simple-project/
├── src/
│   ├── database.py      # Работа с БД
│   ├── auth.py          # Аутентификация
│   ├── users.py         # Пользователи
│   └── api.py           # REST API
├── tests/
│   ├── test_database.py
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_api.py
├── docs/
│   ├── research.md
│   └── stack.md
└── .vibecraft/
    └── manifest.json
```

Определите логические модули:
- `database.py` → модуль **database**
- `auth.py` → модуль **auth**
- `users.py` → модуль **users**
- `api.py` → модуль **api**

### Шаг 2: Планирование модульной структуры

Определите зависимости между модулями:

```
database ← auth ← users ← api
    ↑        ↑        ↑
config -----+        |
                     |
billing -------------+
```

Запишите план:

```markdown
## Module Plan

### database
- Dependencies: none
- Exports: DatabaseConnection, execute_query

### config
- Dependencies: none
- Exports: Config, get_config

### auth
- Dependencies: database, config
- Exports: AuthService, login, logout

### users
- Dependencies: auth, database
- Exports: UserService, get_user, create_user

### api
- Dependencies: auth, users
- Exports: ApiRouter, routes
```

### Шаг 3: Создание нового modular проекта

```bash
# Создать новую директорию
mkdir my-project-modular
cd my-project-modular

# Инициализировать с modular mode
vibecraft init -r ../simple-project/docs/research.md \
               -s ../simple-project/docs/stack.md \
               --mode modular
```

### Шаг 4: Создание модулей

```bash
# Создать модули без зависимостей сначала
vibecraft module create database -d "Database connection layer"
vibecraft module create config -d "Configuration management"

# Создать модули с зависимостями
vibecraft module create auth -d "Authentication" --depends-on database,config
vibecraft module create users -d "User management" --depends-on auth,database
vibecraft module create api -d "REST API" --depends-on auth,users

# Инициализировать модули
vibecraft module init database
vibecraft module init config
vibecraft module init auth
vibecraft module init users
vibecraft module init api
```

### Шаг 5: Перенос кода в модули

#### 5.1 Перенос database

```bash
# Копировать файл
cp ../simple-project/src/database.py modules/database/src/

# Создать __init__.py для экспортов
echo "from .database import DatabaseConnection, execute_query" > modules/database/src/__init__.py

# Обновить .module.json
# modules/database/.module.json:
{
  "name": "database",
  "exports": ["DatabaseConnection", "execute_query"]
}
```

#### 5.2 Перенос config

```bash
cp ../simple-project/src/config.py modules/config/src/
echo "from .config import Config, get_config" > modules/config/src/__init__.py
```

#### 5.3 Перенос auth

```bash
cp ../simple-project/src/auth.py modules/auth/src/

# Обновить импорты в auth.py
# Было:
from database import DatabaseConnection

# Стало:
from modules.database.src import DatabaseConnection
```

#### 5.4 Перенос users

```bash
cp ../simple-project/src/users.py modules/users/src/

# Обновить импорты
# Было:
from auth import AuthService
from database import DatabaseConnection

# Стало:
from modules.auth.src import AuthService
from modules.database.src import DatabaseConnection
```

#### 5.5 Перенос api

```bash
cp ../simple-project/src/api.py modules/api/src/

# Обновить импорты
```

### Шаг 6: Перенос тестов

```bash
# Копировать тесты в соответствующие модули
cp ../simple-project/tests/test_database.py modules/database/tests/
cp ../simple-project/tests/test_auth.py modules/auth/tests/
cp ../simple-project/tests/test_users.py modules/users/tests/
cp ../simple-project/tests/test_api.py modules/api/tests/

# Переименовать в формат pytest
mv modules/database/tests/test_database.py modules/database/tests/test_database_module.py
```

### Шаг 7: Обновление импортов

Во всех файлах модулей обновите импорты:

#### Before (Simple):
```python
from auth import AuthService
from database import DatabaseConnection
```

#### After (Modular):
```python
# Вариант 1: Прямой импорт
from modules.auth.src import AuthService
from modules.database.src import DatabaseConnection

# Вариант 2: Через integration (рекомендуется)
from integration.interfaces import AuthService, DatabaseConnection
```

### Шаг 8: Построение интеграционного слоя

```bash
# Проверить зависимости
vibecraft integrate analyze

# Построить интерфейсы и коннекторы
vibecraft integrate build
```

### Шаг 9: Верификация

```bash
# Запустить тесты всех модулей
pytest modules/database/tests/ -v
pytest modules/auth/tests/ -v
pytest modules/users/tests/ -v
pytest modules/api/tests/ -v

# Запустить integration тесты
pytest integration/ -v
```

## Import Refactoring

### Pattern 1: Direct module imports

**Before:**
```python
from auth import AuthService
```

**After:**
```python
from modules.auth.src import AuthService
```

### Pattern 2: Relative imports

**Before:**
```python
from .database import DatabaseConnection
```

**After:**
```python
from modules.database.src import DatabaseConnection
```

### Pattern 3: Integration interfaces

**Best Practice:**
```python
from integration.interfaces import AuthService, DatabaseConnection
```

## Common Issues

### Issue: Import errors after migration

**Cause**: Пути к модулям не обновлены

**Solution**:
```bash
# Найти все импорты
grep -r "from auth import" modules/
grep -r "from database import" modules/

# Обновить на правильные пути
```

### Issue: Circular imports

**Cause**: Модули импортируют друг друга напрямую

**Solution**:
1. Использовать integration interfaces
2. Выделить общую логику в отдельный модуль

### Issue: Tests fail with module not found

**Cause**: Тесты используют старые импорты

**Solution**:
```python
# В тестах использовать абсолютные пути
import sys
sys.path.insert(0, str(project_root / "modules" / "auth" / "src"))

from auth import AuthService
```

## Migration Checklist

- [ ] Проанализирована текущая архитектура
- [ ] Определены модули и зависимости
- [ ] Создан modular проект
- [ ] Созданы все модули
- [ ] Код перенесён в модули
- [ ] Импорты обновлены
- [ ] Тесты перенесены
- [ ] `vibecraft integrate analyze` — без ошибок
- [ ] `vibecraft integrate build` — успешно
- [ ] Все тесты проходят

## Post-Migration

После миграции:

1. **Удалите старый Simple проект** (после верификации)
2. **Обновите документацию** проекта
3. **Настройте CI/CD** для modular структуры
4. **Обучите команду** работе с modular mode

## Rollback

Если нужно вернуться к Simple mode:

```bash
# Создать новый simple проект
mkdir my-project-simple
cd my-project-simple

vibecraft init -r ../my-project-modular/docs/research.md \
               -s ../my-project-modular/docs/stack.md \
               --mode simple

# Копировать код обратно
cp -r ../my-project-modular/modules/*/src/* src/
```

## See Also

- [MODULAR_MODE.md](./MODULAR_MODE.md) — Overview modular mode
- [MODULE_DEVELOPMENT.md](./MODULE_DEVELOPMENT.md) — Module development guide
- [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) — Integration guide

---

*Vibecraft Framework v0.4 | Last updated: 2026-02-27*
