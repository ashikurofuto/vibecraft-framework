# Phase 4 Tests — Presentation Layer

**Phase:** 4  
**Layer:** Presentation  
**Status:** Ready for Approval  
**Created:** 2026-02-26

---

## Overview

Этот набор тестов покрывает **Presentation Layer** игры Asteroids — слой, отвечающий за:
- Обработку ввода с клавиатуры
- Рендеринг графики через Canvas 2D API
- Управление UI элементами (HUD, меню, экраны паузы/Game Over)

---

## Test Files

### 1. InputHandler.test.js

**Тестируемый компонент:** `src/presentation/InputHandler.js`

**Что проверяется:**
- Регистрация event listeners (keydown/keyup)
- Отслеживание состояния клавиш (`isPressed`)
- Edge detection для однократных действий (`wasJustPressed`)
- Завершение кадра и сохранение предыдущего состояния (`endFrame`)
- Получение агрегированного состояния ввода (`getState`)
- Маппинг клавиш на игровые действия

**Клавиши:**
| Клавиша | Действие |
|---------|----------|
| ArrowUp / W | Thrust (тяга) |
| ArrowLeft / A | Rotate Left (вращение влево) |
| ArrowRight / D | Rotate Right (вращение вправо) |
| Space | Fire (огонь) |
| H | Hyperspace (гиперпространство) |
| P | Pause (пауза) |

**Количество тестов:** 25+

---

### 2. Renderer.test.js

**Тестируемый компонент:** `src/presentation/Renderer.js`

**Что проверяется:**
- Очистка canvas чёрным фоном
- Настройка стиля отрисовки (белые линии, толщина 2px)
- Отрисовка корабля (треугольник с трансформациями)
- Отрисовка астероидов (многоугольники)
- Отрисовка пуль (линии)
- Отрисовка НЛО (эллипсы)
- Отрисовка взрывов (расходящиеся линии)
- Сохранение/восстановление состояния контекста
- Трансформации (translate, rotate)

**Графические примитивы:**
| Сущность | Примитивы |
|----------|-----------|
| Ship | 3 линии (треугольник) |
| Asteroid | 6-8 линий (многоугольник) |
| Bullet | 1 линия |
| UFO | 2 эллипса + линии |
| Explosion | 12 расходящихся линий |

**Количество тестов:** 40+

---

### 3. UIController.test.js

**Тестируемый компонент:** `src/presentation/UIController.js`

**Что проверяется:**
- Обновление HUD элементов (score, lives, level, highScore)
- Управление видимостью экранов (menu, pause, gameOver)
- Отображение сообщения о завершении уровня
- Регистрация обработчиков кнопок (start, restart)
- Переходы между состояниями UI

**DOM элементы:**
| ID | Элемент |
|----|---------|
| score | Текущий счёт |
| lives | Жизни |
| level | Уровень |
| high-score | Рекорд |
| menu | Главное меню |
| pause | Экран паузы |
| game-over | Экран завершения игры |
| start-button | Кнопка старта |
| restart-button | Кнопка перезапуска |

**Количество тестов:** 40+

---

## Mock Objects

### canvas.js

Создаёт мок для Canvas API:
- `createMockCanvas(width, height)` — мок HTMLCanvasElement
- `createMockCanvasContext()` — мок CanvasRenderingContext2D
- `createMockOffscreenCanvas(width, height)` — мок OffscreenCanvas

**Использование:**
```javascript
import { createMockCanvas } from '../__mocks__/canvas.js';

const canvas = createMockCanvas(800, 600);
const ctx = canvas._getMockContext();
```

---

## Running Tests

### Запуск всех тестов Phase 4
```bash
npm test -- src/tests/phase_4/
```

### Запуск с покрытием
```bash
npm run test:coverage -- src/tests/phase_4/
```

### Запуск в режиме watch
```bash
npm run test:watch -- src/tests/phase_4/
```

### Запуск отдельных файлов
```bash
# InputHandler
npm test -- src/tests/phase_4/InputHandler.test.js

# Renderer
npm test -- src/tests/phase_4/Renderer.test.js

# UIController
npm test -- src/tests/phase_4/UIController.test.js
```

---

## Expected Results (RED Phase)

**До реализации** все тесты должны **FAIL**:

```
FAIL src/tests/phase_4/InputHandler.test.js
  ● InputHandler › constructor › should register keydown event listener
    Cannot find module '../../src/presentation/InputHandler.js'

FAIL src/tests/phase_4/Renderer.test.js
  ● Renderer › constructor › should store canvas reference
    Cannot find module '../../src/presentation/Renderer.js'

FAIL src/tests/phase_4/UIController.test.js
  ● UIController › constructor › should store document reference
    Cannot find module '../../src/presentation/UIController.js'
```

Это **ожидаемое поведение** в TDD процессе (RED phase).

---

## Coverage Goals

| Component | Goal |
|-----------|------|
| InputHandler | >80% |
| Renderer | >80% |
| UIController | >80% |

---

## What Is Covered

### InputHandler
- ✅ Регистрация event listeners
- ✅ Отслеживание состояния клавиш
- ✅ Edge detection (wasJustPressed)
- ✅ Маппинг клавиш на действия
- ✅ Мультитач (одновременное нажатие нескольких клавиш)
- ✅ PreventDefault для keydown событий

### Renderer
- ✅ Очистка canvas
- ✅ Настройка стиля отрисовки
- ✅ Отрисовка корабля с трансформациями
- ✅ Отрисовка астероидов (многоугольники)
- ✅ Отрисовка пуль
- ✅ Отрисовка НЛО
- ✅ Отрисовка взрывов
- ✅ Сохранение/восстановление контекста
- ✅ Отрисовка множественных сущностей

### UIController
- ✅ Обновление HUD элементов
- ✅ Показ/скрытие меню
- ✅ Показ/скрытие паузы
- ✅ Показ/скрытие Game Over экрана
- ✅ Сообщение о завершении уровня
- ✅ Обработчики кнопок start/restart
- ✅ Переходы между состояниями UI

---

## What Is NOT Covered

### InputHandler
- ❌ Тестирование с реальным DOM (используются моки)
- ❌ Тестирование touch событий (для future mobile support)
- ❌ Тестирование gamepad API

### Renderer
- ❌ Визуальная проверка графики (только вызовы методов)
- ❌ Производительность отрисовки (FPS, batch rendering)
- ❌ Анимация тяги двигателя (пульсация)
- ❌ Сглаживание и антиалиасинг

### UIController
- ❌ Стилизация CSS (только display property)
- ❌ Анимации переходов между экранами
- ❌ Звуковые эффекты UI

---

## Implementation Requirements

Для прохождения тестов необходимо реализовать:

### InputHandler
```javascript
export class InputHandler {
    constructor(windowObj = window) {
        this.keys = new Set();
        this.previousKeys = new Set();
        // ... регистрация event listeners
    }

    isPressed(code) { /* ... */ }
    wasJustPressed(code) { /* ... */ }
    endFrame() { /* ... */ }
    getState() { /* ... */ }
}
```

### Renderer
```javascript
export class Renderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = canvas.width;
        this.height = canvas.height;
    }

    render(gameState) { /* ... */ }
    drawShip(ship) { /* ... */ }
    drawAsteroid(asteroid) { /* ... */ }
    drawBullet(bullet) { /* ... */ }
    drawUFO(ufo) { /* ... */ }
    drawExplosion(position) { /* ... */ }
}
```

### UIController
```javascript
export class UIController {
    constructor(documentObj = document) {
        // ... получение элементов по ID
    }

    updateScore(score) { /* ... */ }
    updateLives(lives) { /* ... */ }
    updateLevel(level) { /* ... */ }
    updateHighScore(score) { /* ... */ }
    showMenu() { /* ... */ }
    hideMenu() { /* ... */ }
    showPause() { /* ... */ }
    hidePause() { /* ... */ }
    showGameOver(score) { /* ... */ }
    hideGameOver() { /* ... */ }
    showLevelComplete(level) { /* ... */ }
    on(event, callback) { /* ... */ }
}
```

---

## TDD Workflow

1. **RED** — Запустить тесты, убедиться что все FAIL
2. **GREEN** — Реализовать код для прохождения тестов
3. **REFACTOR** — Улучшить код, сохранив прохождение тестов

---

## Approval Status

- [x] Tests written
- [ ] Tests approved by human
- [ ] Tests locked (immutable)
- [ ] Implementation started
- [ ] Implementation complete (GREEN phase)
- [ ] Code reviewed

---

**Tests Ready for Approval**  
**Files:** InputHandler.test.js, Renderer.test.js, UIController.test.js  
**Coverage Intention:** Все публичные методы и основные сценарии использования  
**Awaiting human approval before implementation begins.**
