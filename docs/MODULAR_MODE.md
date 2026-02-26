# Vibecraft Framework v0.4 — Modular Mode Guide

## Overview

**Modular Mode** — это режим работы Vibecraft Framework, предназначенный для больших проектов с модульной архитектурой. В отличие от Simple Mode, где весь проект рассматривается как единое целое, Modular Mode позволяет разрабатывать проект как набор независимых модулей с явными зависимостями.

## Когда использовать Modular Mode

| Критерий | Simple Mode | Modular Mode |
|----------|-------------|--------------|
| **Размер проекта** | Маленький (< 10 файлов) | Средний/Большой (> 10 файлов) |
| **Команда** | 1-2 разработчика | 3+ разработчиков |
| **Архитектура** | Монолитная | Модульная/Микросервисная |
| **Зависимости** | Минимальные | Явные зависимости между компонентами |
| **TDD** | Один цикл RED/GREEN | Несколько циклов для модулей |

## Quick Start

### 1. Инициализация проекта

```bash
vibecraft init -r docs/research.md -s docs/stack.md --mode modular
```

### 2. Создание модулей

```bash
# Создать модуль database
vibecraft module create database -d "Database connection layer"

# Создать модуль auth с зависимостью на database
vibecraft module create auth -d "Authentication module" --depends-on database

# Создать модуль users с зависимостями
vibecraft module create users -d "User management" --depends-on auth,database
```

### 3. Инициализация модуля

```bash
# Инициализировать модуль (создать структуру)
vibecraft module init auth
```

### 4. Запуск skills для модуля

```bash
# Запустить research для модуля
vibecraft run research --module auth

# Запустить implement phase 1 для модуля
vibecraft run implement --phase 1 --module auth

# Запустить implement phase 2 для модуля
vibecraft run implement --phase 2 --module auth
```

### 5. Анализ зависимостей

```bash
# Проверить зависимости
vibecraft integrate analyze

# Построить интеграционный слой
vibecraft integrate build
```

## Структура проекта

```
my-project/
├── .vibecraft/
│   ├── manifest.json           # Общая информация о проекте
│   └── modules-registry.json   # Реестр модулей и зависимостей
├── modules/
│   ├── database/
│   │   ├── .module.json        # Конфигурация модуля
│   │   ├── context.md          # Context модуля
│   │   ├── src/                # Исходный код модуля
│   │   ├── tests/              # Тесты модуля
│   │   └── plans/              # Планы для фаз
│   ├── auth/
│   │   ├── .module.json
│   │   ├── context.md
│   │   ├── src/
│   │   ├── tests/
│   │   └── plans/
│   └── users/
│       ├── .module.json
│       ├── context.md
│       ├── src/
│       ├── tests/
│       └── plans/
├── integration/
│   ├── interfaces.py           # Авто-генерированные интерфейсы
│   └── connectors/             # Коннекторы между модулями
├── docs/
│   ├── research.md
│   ├── stack.md
│   ├── context.md
│   └── design/
└── src/
    └── tests/
```

## Конфигурация модуля (.module.json)

Каждый модуль имеет конфигурационный файл `.module.json`:

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
    "estimated_days": 5
  }
}
```

### Поля конфигурации

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | string | Уникальное имя модуля |
| `description` | string | Описание назначения модуля |
| `dependencies` | string[] | Список модулей, от которых зависит этот |
| `exports` | string[] | Публичные экспорты (классы, функции) |
| `status` | string | `planned`, `in_progress`, `completed` |
| `metadata` | object | Дополнительная информация |

## Module Registry

Файл `.vibecraft/modules-registry.json` содержит информацию обо всех модулях:

```json
{
  "modules": [
    {
      "name": "database",
      "path": "modules/database",
      "status": "completed",
      "dependencies": [],
      "exports": ["DatabaseConnection", "execute_query"]
    },
    {
      "name": "auth",
      "path": "modules/auth",
      "status": "in_progress",
      "dependencies": ["database"],
      "exports": ["AuthService", "login"]
    }
  ],
  "dependencies": {
    "database": [],
    "auth": ["database"]
  },
  "build_order": ["database", "auth"]
}
```

## Build Order

Modular Mode автоматически определяет порядок сборки модулей на основе зависимостей. Модули без зависимостей собираются первыми.

Пример:
- `database` (нет зависимостей) → первый
- `auth` (зависит от `database`) → второй
- `users` (зависит от `auth`, `database`) → третий

## Module Context

Каждый модуль имеет свой `context.md`, который содержит:
- Историю разработки модуля
- Принятые архитектурные решения
- Статус выполнения фаз
- Заметки разработчика

Пример:
```markdown
# Auth Module Context

## Module Info
- **Name**: auth
- **Description**: Authentication and authorization
- **Status**: in_progress

## Exports
- AuthService
- login
- logout

## Dependencies
- database

## Current Phase
Implement Phase 2

## Implementation Notes
- Using JWT for tokens
- Refresh token rotation implemented
```

## CLI Commands

| Command | Описание |
|---------|----------|
| `vibecraft module create <name> -d "<desc>"` | Создать новый модуль |
| `vibecraft module create <name> --depends-on <mod1,mod2>` | Создать с зависимостями |
| `vibecraft module list` | Показать список модулей |
| `vibecraft module init <name>` | Инициализировать структуру модуля |
| `vibecraft module status <name>` | Показать статус модуля |
| `vibecraft run <skill> --module <name>` | Запустить skill для модуля |
| `vibecraft integrate analyze` | Анализировать зависимости |
| `vibecraft integrate build` | Построить интеграционный слой |

## Best Practices

### 1. Модули должны быть слабосвязанными

Каждый модуль должен иметь минимальное количество зависимостей. Избегайте циклических зависимостей.

### 2. Явные зависимости

Всегда указывайте зависимости явно в `.module.json`. Не полагайтесь на неявные импорты.

### 3. Следуйте build order

Разрабатывайте модули в порядке, определённом `build_order`. Это гарантирует, что зависимости готовы.

### 4. TDD для каждого модуля

Для каждого модуля применяйте полный цикл TDD:
1. RED: Пишем тесты
2. GREEN: Пишем реализацию
3. REVIEW: Проверяем качество

### 5. Обновляйте context.md

После каждой фазы обновляйте `context.md` модуля. Это поможет другим разработчикам понять историю решений.

## Troubleshooting

### Ошибка: "Module not found"

Убедитесь, что модуль создан и инициализирован:
```bash
vibecraft module create mymodule -d "Description"
vibecraft module init mymodule
```

### Ошибка: "Circular dependency detected"

Modular Mode обнаружил циклическую зависимость. Пересмотрите архитектуру:
```bash
vibecraft integrate analyze  # Покажет цикл
```

### Ошибка: "Path traversal detected"

Попытка записи файла за пределами модуля заблокирована. Проверьте путь вывода.

## Migration from Simple Mode

Если вы начали с Simple Mode и хотите перейти на Modular:

1. Создайте новый проект с `--mode modular`
2. Перенесите `research.md` и `stack.md`
3. Создайте модули на основе вашей архитектуры
4. Перенесите код в соответствующие модули

См. также: [MIGRATION_SIMPLE_TO_MODULAR.md](./MIGRATION_SIMPLE_TO_MODULAR.md)

## See Also

- [MODULE_DEVELOPMENT.md](./MODULE_DEVELOPMENT.md) — Guide по разработке модулей
- [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) — Guide по интеграции модулей
- [MIGRATION_SIMPLE_TO_MODULAR.md](./MIGRATION_SIMPLE_TO_MODULAR.md) — Migration guide

---

*Vibecraft Framework v0.4 | Last updated: 2026-02-27*
