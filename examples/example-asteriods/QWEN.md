# Qwen Code Context: Asteroids Game

## Project Overview

**Asteroids Game** — классическая аркадная игра, реализованная на **Vanilla JavaScript** с использованием **TDD (Test-Driven Development)** подхода. Игра следует принципам **Clean Architecture** с разделением на 4 слоя.

### Ключевые характеристики
- **Жанр**: Космический шутер / аркада
- **Платформа**: Веб-браузер (Canvas API)
- **Стек**: Vanilla ES2022+ JavaScript без фреймворков
- **Методология**: TDD (Jest + jsdom)
- **Архитектура**: Clean Architecture (Domain → Application → Infrastructure → Presentation)

---

## Tech Stack

| Компонент | Технология | Версия |
|-----------|------------|--------|
| **Язык** | JavaScript (ECMAScript) | ES2022+ |
| **Платформа** | Веб-браузер | Современные браузеры |
| **Тестирование** | Jest | ^30.2.0 |
| **Test Environment** | jsdom | ^30.2.0 |
| **Рендеринг** | Canvas 2D API | Native |

---

## Architecture

### Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (Renderer, InputHandler, UIController) │
├─────────────────────────────────────────┤
│         Application Layer               │
│  (Game, GameLoop, GameState, Score)     │
├─────────────────────────────────────────┤
│           Domain Layer                  │
│  (Ship, Asteroid, Bullet, UFO, Vector)  │
├─────────────────────────────────────────┤
│        Infrastructure Layer             │
│  (Storage, AudioController)             │
└─────────────────────────────────────────┘
```

### Directory Structure

```
test/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── Ship.js
│   │   │   ├── Asteroid.js
│   │   │   ├── Bullet.js
│   │   │   └── UFO.js
│   │   ├── value-objects/
│   │   │   ├── Vector2D.js
│   │   │   └── CollisionBox.js
│   │   └── services/
│   │       └── CollisionDetector.js
│   ├── application/
│   │   ├── Game.js
│   │   ├── GameLoop.js
│   │   ├── GameState.js
│   │   ├── ScoreManager.js
│   │   └── BulletPool.js
│   ├── infrastructure/
│   │   ├── Storage.js
│   │   └── AudioController.js
│   ├── presentation/
│   │   ├── Renderer.js
│   │   ├── InputHandler.js
│   │   └── UIController.js
│   └── tests/
│       ├── domain/
│       │   ├── Ship.test.js
│       │   ├── Asteroid.test.js
│       │   ├── Bullet.test.js
│       │   ├── UFO.test.js
│       │   ├── Vector2D.test.js
│       │   ├── CollisionBox.test.js
│       │   └── CollisionDetector.test.js
│       └── phase_*/
├── docs/
│   ├── design/
│   │   ├── architecture.md
│   │   ├── data_flow.md
│   │   └── sequence.md
│   ├── plans/
│   │   ├── phase1_domain.md
│   │   ├── phase2_application.md
│   │   ├── phase3_infrastructure.md
│   │   ├── phase4_presentation.md
│   │   └── phase5_ui_polish.md
│   ├── context.md
│   ├── research.md
│   └── stack.md
├── .vibecraft/
│   ├── manifest.json
│   ├── agents/
│   ├── prompts/
│   ├── skills/
│   └── snapshots/
├── .vibecraft-venv/
├── coverage/
├── node_modules/
├── jest.config.js
├── jest.setup.js
├── package.json
└── vibecraft-local.bat
```

---

## Building and Running

### Installation

```bash
npm install
```

### Testing

```bash
# Запуск всех тестов
npm test

# Запуск с покрытием
npm run test:coverage

# Запуск в режиме watch
npm run test:watch
```

### Jest Configuration

```javascript
// jest.config.js
export default {
  testEnvironment: 'jsdom',
  moduleFileExtensions: ['js'],
  testMatch: ['**/test/**/*.test.js'],
  coverageDirectory: 'coverage',
  collectCoverageFrom: ['src/**/*.js'],
  transform: {},
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js']
};
```

---

## Development Conventions

### TDD Process

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   RED       │     │   GREEN     │     │  REFACTOR   │
│  Write test │ ──► │  Make it    │ ──► │  Clean up   │
│  (fails)    │     │  pass       │     │  code       │
└─────────────┘     └─────────────┘     └─────────────┘
       ▲                                       │
       └───────────────────────────────────────┘
```

**Правила:**
1. Не писать продакшен-код без падающего теста
2. Писать минимальный код для прохождения теста
3. Рефакторить только после зелёного теста
4. Тесты в `src/tests/` — **locked**, не модифицировать после approval

### Code Style

| Аспект | Правило |
|--------|---------|
| **Модули** | ES6 `import`/`export` |
| **Классы** | PascalCase (`Ship`, `Asteroid`) |
| **Функции/переменные** | camelCase (`createAsteroid`, `gameState`) |
| **Константы** | UPPER_CASE (`MAX_BULLETS`, `SHIP_SPEED`) |
| **Приватные поля** | `#privateField` |
| **Документирование** | JSDoc для публичных методов |

### Testing Practices

- **Unit-тесты** для domain сущностей
- **Integration-тесты** для application слоя
- **Mock** для infrastructure зависимостей
- **Покрытие**: > 80% для критических модулей

### Git Workflow

Проект использует **Vibecraft** — AI-ассистированный workflow с фазами:
1. **Research** — анализ требований
2. **Design** — архитектурные решения
3. **Plan** — пошаговый план реализации
4. **Implement** — TDD реализация
5. **Review** — код ревью

---

## Key Domain Concepts

### Game Entities

| Сущность | Описание |
|----------|----------|
| **Ship** | Корабль игрока с вращением, тягой, инерцией |
| **Asteroid** | Астероиды 3 размеров (large → medium → small) |
| **Bullet** | Лазерные снаряды из пула (object pooling) |
| **UFO** | НЛО (большое/малое) с разным поведением |

### Value Objects

| VO | Описание |
|----|----------|
| **Vector2D** | 2D вектор для позиции, скорости, направления |
| **CollisionBox** | Круглая коллизия (позиция + радиус) |

### Services

| Service | Описание |
|---------|----------|
| **CollisionDetector** | Детекция столкновений между сущностями |

### Application Services

| Service | Описание |
|---------|----------|
| **Game** | Фасад игры, объединяет все слои |
| **GameLoop** | Игровой цикл с фиксированным timestep |
| **GameState** | Состояние игры (menu, playing, paused, gameover) |
| **ScoreManager** | Подсчёт очков и рекорды (localStorage) |
| **BulletPool** | Object pool для пуль (оптимизация) |

---

## Game Mechanics

### Управление

| Действие | Механика |
|----------|----------|
| **Вращение** | Поворот корабля влево/вправо |
| **Тяга** | Ускорение в направлении носа с инерцией |
| **Стрельба** | Лазерные снаряды (edge detection) |
| **Пауза** | Toggle паузы по нажатию |

### Физика

- **Инерция** — корабль сохраняет скорость после ускорения
- **Трение** — коэффициент 0.99 для замедления
- **Замкнутый мир** — объекты «заворачиваются» с краёв экрана

### Система очков

| Объект | Очки |
|--------|------|
| Крупный астероид | 20 |
| Средний астероид | 50 |
| Мелкий астероид | 100 |
| Большое НЛО | 200 |
| Малое НЛО | 1000 |

---

## Vibecraft Integration

### Local Launcher

```batch
vibecraft-local.bat
```

Запускает Vibecraft из локальной виртуальной среды (`.vibecraft-venv/`).

### Agents

Проект использует AI-агентов для различных задач:
- `researcher` — анализ требований
- `architect` — архитектурные решения
- `planner` — планирование фаз
- `tdd_writer` — написание тестов
- `implementer` — реализация кода
- `code_reviewer` — ревью кода
- `game_designer` — игровой дизайн

### Skills

- `research_skill` — исследование
- `design_skill` — проектирование
- `plan_skill` — планирование
- `implement_skill` — реализация
- `review_skill` — ревью

---

## Quality Metrics

| Метрика | Цель |
|---------|------|
| **Покрытие тестами** | > 80% |
| **ESLint ошибок** | 0 |
| **Размер бандла** | < 100 KB (minified) |
| **Производительность** | 60 FPS |

---

## Important Notes

### Immutable Contracts

- Тесты в `src/tests/` — **locked** после tdd_writer approval
- ADR решения финальны, если новый ADR явно не переопределяет
- Стек из `docs/stack.md` применяется ко всем агентам

### Architecture Decision Records (ADR)

- **ADR-001**: Vanilla JavaScript Without Frameworks
- **ADR-002**: Clean Architecture with 4 Layers
- **ADR-003**: TDD with Jest and jsdom
- **ADR-004**: Fixed Timestep Game Loop
- **ADR-005**: Canvas 2D API for Rendering
- **ADR-006**: ES Modules for Code Organization
- **ADR-007**: Object Pooling for Bullets and Asteroids
- **ADR-008**: localStorage for High Scores
- **ADR-009**: Event-Based Input Handling
- **ADR-010**: Collision Detection with Circle Approximation

### Context Switching

Для продолжения работы в новом чате:
```bash
vibecraft context --skill <skill_name>
```

Или вручную приложить:
1. `docs/context.md`
2. `.vibecraft/skills/<current_skill>.yaml`
3. `.vibecraft/agents/<relevant_agent>.md`
4. `docs/plans/phase_<N>.md`

---

## References

- [Stack Documentation](docs/stack.md)
- [Research](docs/research.md)
- [Architecture](docs/design/architecture.md)
- [Context](docs/context.md)
