# Architecture: Asteroids Game

**Version:** 1.0  
**Status:** Accepted  
**Last Updated:** 2026-02-25  
**Phase:** Design

---

## 📋 Overview

Этот документ описывает архитектуру игры Asteroids, используя **C4 модель** (Context, Container, Component, Code) и **Architecture Decision Records (ADR)** для ключевых решений.

### Архитектурные принципы

1. **Clean Architecture** — зависимости направлены внутрь к домену
2. **SOLID** — каждый класс следует принципам SOLID
3. **Testability First** — архитектура поддерживает TDD
4. **Explicit Dependencies** — все зависимости явные
5. **Single Responsibility** — один класс = одна ответственность

---

## 🏗️ C4 Model

### Level 1: System Context Diagram

```mermaid
C4Context
    title System Context Diagram — Asteroids Game

    Person(player, "Игрок", "Человек, играющий в игру")
    System_Ext(browser, "Веб-браузер", "Chrome/Firefox/Safari/Edge с поддержкой ES2022+")
    
    System_Boundary(asteroids, "Asteroids Game") {
        System(game_system, "Asteroids Game", "Веб-игра на Vanilla JavaScript")
    }

    Rel(player, browser, "Использует")
    Rel(browser, game_system, "Запускает и рендерит")

    UpdateRelStyle(player, browser, $offsetY="-30")
    UpdateRelStyle(browser, game_system, $offsetY="30")
```

**Описание:**
- **Игрок** взаимодействует с **веб-браузером**
- **Браузер** загружает и выполняет код игры
- **Asteroids Game** — единая система без внешних зависимостей

---

### Level 2: Container Diagram

```mermaid
C4Container
    title Container Diagram — Asteroids Game

    Person(player, "Игрок", "Человек, играющий в игру")
    
    Container_Boundary(game_boundary, "Asteroids Game") {
        Container(ui, "UI Layer", "HTML/CSS/JS", "Интерфейс, меню, HUD")
        Container(presentation, "Presentation Layer", "JavaScript", "Рендеринг Canvas, обработка ввода")
        Container(application, "Application Layer", "JavaScript", "Игровой цикл, состояние, правила")
        Container(domain, "Domain Layer", "JavaScript", "Сущности: Ship, Asteroid, Bullet, UFO")
        Container(infrastructure, "Infrastructure Layer", "JavaScript", "Storage, Audio, LocalStorage")
    }

    Rel(player, ui, "Взаимодействует")
    Rel(ui, presentation, "Управляет отображением")
    Rel(presentation, application, "Отправляет ввод, получает состояние")
    Rel(application, domain, "Использует сущности и правила")
    Rel(application, infrastructure, "Сохраняет/загружает данные")
    Rel(infrastructure, domain, "Сериализует сущности")

    UpdateRelStyle(player, ui, $offsetY="-40")
    UpdateRelStyle(ui, presentation, $offsetX="-60")
    UpdateRelStyle(presentation, application, $offsetX="60")
    UpdateRelStyle(application, domain, $offsetX="-60")
    UpdateRelStyle(application, infrastructure, $offsetX="60")
    UpdateRelStyle(infrastructure, domain, $offsetX="-60")
```

**Контейнеры:**

| Контейнер | Технология | Ответственность |
|-----------|------------|-----------------|
| **UI Layer** | HTML/CSS | Меню, HUD, экраны Game Over/Pause |
| **Presentation Layer** | JavaScript + Canvas 2D API | Рендеринг графики, обработка input |
| **Application Layer** | JavaScript | Game loop, GameState, ScoreManager |
| **Domain Layer** | JavaScript | Ship, Asteroid, Bullet, UFO, Vector2D |
| **Infrastructure Layer** | JavaScript + Web APIs | Storage, AudioController, LocalStorage |

---

### Level 3: Component Diagram

#### Domain Layer Components

```mermaid
C4Component
    title Domain Layer Components

    Container_Boundary(domain, "Domain Layer") {
        Component(ship, "Ship", "Entity", "Игрок: позиция, вращение, тяга")
        Component(asteroid, "Asteroid", "Entity", "Астероид: размер, фрагментация")
        Component(bullet, "Bullet", "Entity", "Лазер: позиция, lifetime")
        Component(ufo, "UFO", "Entity", "НЛО: AI, стрельба")
        Component(vector2d, "Vector2D", "Value Object", "2D вектор для физики")
        Component(collision, "CollisionBox", "Value Object", "Хитбокс для коллизий")
        Component(detector, "CollisionDetector", "Service", "Обнаружение столкновений")
    }

    Rel(ship, vector2d, "Использует")
    Rel(asteroid, vector2d, "Использует")
    Rel(bullet, vector2d, "Использует")
    Rel(ufo, vector2d, "Использует")
    Rel(detector, collision, "Использует")
    Rel(detector, ship, "Проверяет")
    Rel(detector, asteroid, "Проверяет")
```

#### Application Layer Components

```mermaid
C4Component
    title Application Layer Components

    Container_Boundary(application, "Application Layer") {
        Component(game, "Game", "Facade", "Основной интерфейс игры")
        Component(gameloop, "GameLoop", "Service", "Цикл: update() + render()")
        Component(state, "GameState", "State", "Состояние: menu/playing/paused/gameover")
        Component(score, "ScoreManager", "Service", "Подсчёт очков, рекорды")
    }

    Rel(game, gameloop, "Управляет")
    Rel(game, state, "Изменяет")
    Rel(game, score, "Использует")
    Rel(gameloop, state, "Читает")
```

#### Presentation Layer Components

```mermaid
C4Component
    title Presentation Layer Components

    Container_Boundary(presentation, "Presentation Layer") {
        Component(renderer, "Renderer", "Service", "Отрисовка всех объектов")
        Component(input, "InputHandler", "Service", "Обработка клавиатуры")
        Component(ui_ctrl, "UIController", "Controller", "Обновление UI элементов")
    }

    Rel(renderer, input, "Получает ввод")
    Rel(ui_ctrl, renderer, "Триггерит рендер")
```

#### Infrastructure Layer Components

```mermaid
C4Component
    title Infrastructure Layer Components

    Container_Boundary(infrastructure, "Infrastructure Layer") {
        Component(storage, "Storage", "Repository", "Абстракция над localStorage")
        Component(audio, "AudioController", "Service", "Звуковые эффекты")
    }

    Rel(storage, audio, "Не зависит")
```

---

### Level 4: Code Level (Key Classes)

#### Domain Entities

```mermaid
classDiagram
    class Vector2D {
        +number x
        +number y
        +add(other: Vector2D): Vector2D
        +subtract(other: Vector2D): Vector2D
        +multiply(scalar: number): Vector2D
        +magnitude(): number
        +normalize(): Vector2D
        +static distance(a: Vector2D, b: Vector2D): number
    }

    class CollisionBox {
        +Vector2D center
        +number radius
        +contains(point: Vector2D): boolean
        +intersects(other: CollisionBox): boolean
    }

    class Ship {
        -Vector2D #position
        -Vector2D #velocity
        -number #rotation
        -number #lives
        -boolean #isThrusting
        +update(deltaTime: number): void
        +rotate(direction: number): void
        +thrust(): void
        +fire(): Bullet
        +getCollisionBox(): CollisionBox
    }

    class Asteroid {
        -Vector2D #position
        -Vector2D #velocity
        -AsteroidSize #size
        +update(deltaTime: number): void
        +split(): Asteroid[]
        +getCollisionBox(): CollisionBox
        +getPoints(): number
    }

    class Bullet {
        -Vector2D #position
        -Vector2D #velocity
        -number #lifetime
        -boolean #isAlive
        +update(deltaTime: number): void
        +getCollisionBox(): CollisionBox
    }

    class UFO {
        -Vector2D #position
        -Vector2D #velocity
        -UFOPattern #pattern
        -number #shootCooldown
        +update(deltaTime: number): void
        +tryFire(): Bullet
        +getCollisionBox(): CollisionBox
    }

    Vector2D --* CollisionBox
    Vector2D --* Ship
    Vector2D --* Asteroid
    Vector2D --* Bullet
    Vector2D --* UFO
    CollisionBox --* Ship
    CollisionBox --* Asteroid
    CollisionBox --* Bullet
    CollisionBox --* UFO
```

#### Application Services

```mermaid
classDiagram
    class GameState {
        +GameStateEnum state
        +number level
        +number score
        +number highScore
        +isPlaying(): boolean
        +isPaused(): boolean
        +isGameOver(): boolean
        +start(): void
        +pause(): void
        +resume(): void
        +gameOver(): void
        +nextLevel(): void
    }

    class GameLoop {
        -number #lastTime
        -number #accumulator
        -number #fixedTimestep
        -Function #updateCallback
        -Function #renderCallback
        +start(): void
        +stop(): void
        +tick(currentTime: number): void
    }

    class ScoreManager {
        -number #currentScore
        -number #highScore
        +addScore(points: number): void
        +getCurrentScore(): number
        +getHighScore(): number
        +saveHighScore(): void
    }

    class Game {
        -GameState #state
        -GameLoop #loop
        -ScoreManager #score
        -Ship #ship
        -Asteroid[] #asteroids
        -Bullet[] #bullets
        -UFO[] #ufos
        +initialize(): void
        +start(): void
        +update(deltaTime: number): void
        +render(): void
        +handleInput(input: Input): void
    }

    GameState --* Game
    GameLoop --* Game
    ScoreManager --* Game
```

---

## 📝 Architecture Decision Records (ADRs)

---

### ADR-001: Vanilla JavaScript Without Frameworks

**Status:** Accepted

**Context:**
Необходимо выбрать технологию для реализации игры. Современные фреймворки (React, Vue, Phaser) предоставляют готовые решения, но добавляют сложность и размер бандла.

**Decision:**
Использовать **Vanilla JavaScript (ES2022+)** без фреймворков.

**Consequences:**
- ✅ Минимальный размер бандла (<100 KB)
- ✅ Полный контроль над кодом
- ✅ Образовательная ценность (чистая архитектура)
- ❌ Больше кода для написания
- ❌ Нет готовых решений для常见 задач

---

### ADR-002: Clean Architecture with 4 Layers

**Status:** Accepted

**Context:**
Необходимо организовать код так, чтобы обеспечить тестируемость, поддерживаемость и соблюдение SOLID принципов.

**Decision:**
Использовать **Clean Architecture** с 4 слоями:
1. **Domain** — сущности и бизнес-правила
2. **Application** — игровой цикл, состояние
3. **Presentation** — рендеринг и ввод
4. **Infrastructure** — storage, audio

**Consequences:**
- ✅ Зависимости направлены внутрь (к домену)
- ✅ Domain слой не зависит от внешних библиотек
- ✅ Легко тестировать каждый слой изолированно
- ❌ Требует дисциплины от разработчиков
- ❌ Больше файлов и импортов

---

### ADR-003: TDD with Jest and jsdom

**Status:** Accepted

**Context:**
Необходимо обеспечить высокое качество кода и возможность рефакторинга без страха сломать функциональность.

**Decision:**
Использовать **TDD (Test-Driven Development)** с фреймворком **Jest** и средой **jsdom**.

**Consequences:**
- ✅ Покрытие тестами >80%
- ✅ Тесты пишутся ДО кода (RED→GREEN→REFACTOR)
- ✅ jsdom позволяет тестировать DOM-зависимости
- ❌ Замедляет начальную разработку
- ❌ Требует моков для Canvas API

---

### ADR-004: Fixed Timestep Game Loop

**Status:** Accepted

**Context:**
Игровой цикл должен обеспечивать стабильную физику независимо от частоты кадров рендеринга.

**Decision:**
Использовать **фиксированный timestep (1/60 сек)** для физики с накоплением времени (accumulator pattern).

```javascript
const FIXED_TIMESTEP = 1 / 60; // 16.67ms

update(accumulator) {
    while (accumulator >= FIXED_TIMESTEP) {
        this.physicsUpdate(FIXED_TIMESTEP);
        accumulator -= FIXED_TIMESTEP;
    }
}
```

**Consequences:**
- ✅ Детерминированная физика
- ✅ Стабильные коллизии
- ✅ 60 FPS на поддерживаемых устройствах
- ❌ Сложнее реализация чем requestAnimationFrame напрямую

---

### ADR-005: Canvas 2D API for Rendering

**Status:** Accepted

**Context:**
Необходимо выбрать способ рендеринга графики. WebGL мощнее, но сложнее. DOM-элементы медленнее.

**Decision:**
Использовать **Canvas 2D API** с геометрическими примитивами (линии, пути).

**Consequences:**
- ✅ Простой API
- ✅ Хорошая производительность для 2D
- ✅ Аутентичный векторный стиль
- ❌ Нет аппаратного ускорения как WebGL
- ❌ Нужно рисовать всё кодом (нет спрайтов)

---

### ADR-006: ES Modules for Code Organization

**Status:** Accepted

**Context:**
Необходимо организовать код в модули для тестируемости и поддерживаемости.

**Decision:**
Использовать **ES6 Modules** (`import`/`export`) для всех файлов.

**Consequences:**
- ✅ Нативная поддержка в браузерах
- ✅ Статический анализ импортов
- ✅ Tree-shaking для сборщиков
- ❌ Требует сборщик или современный браузер

---

### ADR-007: Object Pooling for Bullets and Asteroids

**Status:** Accepted

**Context:**
Частое создание/удаление объектов вызывает garbage collection паузы.

**Decision:**
Использовать **Object Pool pattern** для пуль и астероидов.

```javascript
class BulletPool {
    constructor(size = 50) {
        this.pool = Array(size).fill(null).map(() => new Bullet());
        this.available = new Set(range(size));
    }
    
    acquire() {
        const id = this.available.values().next().value;
        if (id !== undefined) {
            this.available.delete(id);
            return this.pool[id];
        }
        return null; // Pool exhausted
    }
    
    release(bullet) {
        this.available.add(bullet.id);
        bullet.reset();
    }
}
```

**Consequences:**
- ✅ Минимизация GC пауз
- ✅ Предсказуемая производительность
- ❌ Усложняет код
- ❌ Нужно управлять состоянием объектов

---

### ADR-008: localStorage for High Scores

**Status:** Accepted

**Context:**
Необходимо сохранять рекорды между сессиями. IndexedDB мощнее, но сложнее.

**Decision:**
Использовать **localStorage** для хранения топ-5 рекордов.

**Consequences:**
- ✅ Простой API
- ✅ Синхронное чтение/запись
- ✅ Достаточно для 5 записей
- ❌ Лимит 5-10 MB (не критично)
- ❌ Блокирует основной поток при записи

---

### ADR-009: Event-Based Input Handling

**Status:** Accepted

**Context:**
Необходимо обрабатывать ввод с клавиатуры. Polling проще, но event-based эффективнее.

**Decision:**
Использовать **event-based подход** с накоплением состояния.

```javascript
class InputHandler {
    constructor() {
        this.keys = new Set();
        window.addEventListener('keydown', (e) => this.keys.add(e.code));
        window.addEventListener('keyup', (e) => this.keys.delete(e.code));
    }
    
    isPressed(code) {
        return this.keys.has(code);
    }
    
    wasJustPressed(code) {
        // Track previous frame state for edge detection
    }
}
```

**Consequences:**
- ✅ Отзывчивое управление
- ✅ Поддержка мультитача (для future touch support)
- ❌ Нужно отслеживать состояние между кадрами

---

### ADR-010: Collision Detection with Circle Approximation

**Status:** Accepted

**Context:**
Точная коллизия для многоугольников сложна. Нужно простое и быстрое решение.

**Decision:**
Использовать **круговые хитбоксы (CollisionBox)** для всех объектов.

```javascript
class CollisionBox {
    constructor(center, radius) {
        this.center = center; // Vector2D
        this.radius = radius;
    }
    
    intersects(other) {
        const distance = Vector2D.distance(this.center, other.center);
        return distance < (this.radius + other.radius);
    }
}
```

**Consequences:**
- ✅ O(1) проверка столкновений
- ✅ Простая реализация
- ❌ Менее точно для треугольника корабля
- ✅ Достаточно для аркадной игры

---

## 🔒 Layer Boundaries

### Dependency Rules

```mermaid
graph TD
    subgraph "Dependency Direction →"
        UI[UI Layer] --> PRE[Presentation]
        PRE --> APP[Application]
        APP --> DOM[Domain]
        APP --> INF[Infrastructure]
        INF --> DOM
    end
    
    style DOM fill:#90EE90
    style APP fill:#87CEEB
    style PRE fill:#FFB6C1
    style INF fill:#DDA0DD
    style UI fill:#F0E68C
```

### What Can Cross Boundaries

| From → To | Allowed | What Can Cross |
|-----------|---------|----------------|
| **Presentation → Domain** | ✅ | Читать сущности, вызывать методы |
| **Presentation → Application** | ✅ | Вызывать Game методы |
| **Application → Domain** | ✅ | Создавать/изменять сущности |
| **Application → Infrastructure** | ✅ | Сохранять/загружать данные |
| **Infrastructure → Domain** | ✅ | Сериализовать сущности |
| **Domain → Any** | ❌ | Никаких зависимостей наружу |
| **Infrastructure → Presentation** | ❌ | Никаких UI зависимостей |

### Interface Contracts

#### Domain → Application

```javascript
// Domain exports (pure, no dependencies)
export { Ship } from './entities/Ship.js';
export { Asteroid } from './entities/Asteroid.js';
export { Bullet } from './entities/Bullet.js';
export { UFO } from './entities/UFO.js';
export { Vector2D } from './value-objects/Vector2D.js';
export { CollisionBox } from './value-objects/CollisionBox.js';
export { CollisionDetector } from './services/CollisionDetector.js';
```

#### Application → Presentation

```javascript
// Application предоставляет интерфейс для Presentation
class Game {
    // Presentation вызывает эти методы
    handleInput(input) { }  // InputHandler → Game
    getState() { }          // Renderer читает состояние
    getScore() { }          // UIController читает счёт
}
```

#### Application → Infrastructure

```javascript
// Infrastructure реализует интерфейсы для Application
class Storage {
    saveHighScore(score) { }
    getHighScore() { }
}

class AudioController {
    playShoot() { }
    playExplosion() { }
}
```

---

## 📊 Quality Attributes

| Attribute | Strategy |
|-----------|----------|
| **Performance** | Fixed timestep, object pooling, requestAnimationFrame |
| **Testability** | Dependency injection, pure functions in domain |
| **Maintainability** | Clean Architecture, ES Modules, JSDoc |
| **Extensibility** | Open/Closed principle, component-based design |
| **Reliability** | TDD >80% coverage, error boundaries |

---

## 🗺️ File Structure

```
src/
├── domain/
│   ├── entities/
│   │   ├── Ship.js
│   │   ├── Asteroid.js
│   │   ├── Bullet.js
│   │   └── UFO.js
│   ├── value-objects/
│   │   ├── Vector2D.js
│   │   └── CollisionBox.js
│   └── services/
│       └── CollisionDetector.js
├── application/
│   ├── Game.js
│   ├── GameLoop.js
│   ├── GameState.js
│   └── ScoreManager.js
├── infrastructure/
│   ├── Storage.js
│   └── AudioController.js
├── presentation/
│   ├── Renderer.js
│   ├── InputHandler.js
│   └── UIController.js
└── index.js
```

---

**Architecture Status:** ✅ Accepted  
**Next Phase:** Plan (Implementation Planning)  
**Architect Agent:** Complete
