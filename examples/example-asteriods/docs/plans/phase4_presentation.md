# Phase 4: Presentation Layer Implementation

**Status:** Pending  
**Duration:** 4 дня  
**Priority:** High  
**Dependencies:** Phase 1 (Domain), Phase 2 (Application), Phase 3 (Infrastructure) complete

---

## 📋 Overview

Реализация слоя представления — рендеринг Canvas, обработка ввода, UI контроллер.

### Components

| Component | File | Tests |
|-----------|------|-------|
| InputHandler | `src/presentation/InputHandler.js` | `test/presentation/InputHandler.test.js` |
| Renderer | `src/presentation/Renderer.js` | `test/presentation/Renderer.test.js` |
| UIController | `src/presentation/UIController.js` | `test/presentation/UIController.test.js` |

---

## 🎯 Tasks

### Task 4.1: InputHandler

**Responsibilities:**
- Обработка клавиатуры (arrow keys, space, P, H)
- Накопление состояния клавиш
- Edge detection (wasJustPressed)

**TDD Workflow:**

```javascript
// test/presentation/InputHandler.test.js
import { InputHandler } from '../../src/presentation/InputHandler.js';

describe('InputHandler', () => {
    let inputHandler;
    let mockWindow;
    let listeners;

    beforeEach(() => {
        listeners = { keydown: [], keyup: [] };
        mockWindow = {
            addEventListener: jest.fn((event, handler) => {
                listeners[event].push(handler);
            }),
            removeEventListener: jest.fn()
        };
        inputHandler = new InputHandler(mockWindow);
    });

    test('should register keydown event', () => {
        const event = { code: 'ArrowUp', preventDefault: jest.fn() };
        listeners.keydown.forEach(fn => fn(event));
        expect(inputHandler.isPressed('ArrowUp')).toBe(true);
    });

    test('should register keyup event', () => {
        const keydownEvent = { code: 'ArrowUp', preventDefault: jest.fn() };
        listeners.keydown.forEach(fn => fn(keydownEvent));
        
        const keyupEvent = { code: 'ArrowUp' };
        listeners.keyup.forEach(fn => fn(keyupEvent));
        
        expect(inputHandler.isPressed('ArrowUp')).toBe(false);
    });

    test('should return false for unpressed key', () => {
        expect(inputHandler.isPressed('ArrowUp')).toBe(false);
    });

    test('should track previous frame state for edge detection', () => {
        // Simulate frame transition
        const keydownEvent = { code: 'Space', preventDefault: jest.fn() };
        listeners.keydown.forEach(fn => fn(keydownEvent));
        
        inputHandler.endFrame(); // Mark current state as previous
        
        expect(inputHandler.wasJustPressed('Space')).toBe(false);
        
        // New key press
        listeners.keydown.forEach(fn => fn(keydownEvent));
        expect(inputHandler.wasJustPressed('Space')).toBe(true);
    });

    test('should get input state object', () => {
        const keydownEvent = { code: 'ArrowUp', preventDefault: jest.fn() };
        listeners.keydown.forEach(fn => fn(keydownEvent));
        
        const state = inputHandler.getState();
        expect(state.thrust).toBe(true);
        expect(state.rotateLeft).toBe(false);
    });

    test('should map keys correctly', () => {
        const mappings = [
            { code: 'ArrowUp', expected: 'thrust' },
            { code: 'KeyW', expected: 'thrust' },
            { code: 'ArrowLeft', expected: 'rotateLeft' },
            { code: 'KeyA', expected: 'rotateLeft' },
            { code: 'ArrowRight', expected: 'rotateRight' },
            { code: 'KeyD', expected: 'rotateRight' },
            { code: 'Space', expected: 'fire' },
            { code: 'KeyH', expected: 'hyperspace' },
            { code: 'KeyP', expected: 'pause' }
        ];

        mappings.forEach(({ code, expected }) => {
            const event = { code, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(event));
            const state = inputHandler.getState();
            expect(state[expected]).toBe(true);
        });
    });
});
```

**Implementation:**

```javascript
// src/presentation/InputHandler.js
export class InputHandler {
    constructor(windowObj = window) {
        this.window = windowObj;
        this.keys = new Set();
        this.previousKeys = new Set();
        
        this.window.addEventListener('keydown', (e) => {
            this.keys.add(e.code);
            e.preventDefault();
        });
        
        this.window.addEventListener('keyup', (e) => {
            this.keys.delete(e.code);
        });
    }

    isPressed(code) {
        return this.keys.has(code);
    }

    wasJustPressed(code) {
        return this.keys.has(code) && !this.previousKeys.has(code);
    }

    endFrame() {
        this.previousKeys = new Set(this.keys);
    }

    getState() {
        return {
            rotateLeft: this.isPressed('ArrowLeft') || this.isPressed('KeyA'),
            rotateRight: this.isPressed('ArrowRight') || this.isPressed('KeyD'),
            thrust: this.isPressed('ArrowUp') || this.isPressed('KeyW'),
            fire: this.isPressed('Space'),
            hyperspace: this.isPressed('KeyH'),
            pause: this.isPressed('KeyP')
        };
    }
}
```

---

### Task 4.2: Renderer

**Responsibilities:**
- Отрисовка всех сущностей через Canvas 2D API
- Векторная графика (линии, пути)
- Трансформации (translate, rotate)

**TDD Workflow:**

```javascript
// test/presentation/Renderer.test.js
import { Renderer } from '../../src/presentation/Renderer.js';
import { createMockCanvas } from '../__mocks__/canvas.js';

describe('Renderer', () => {
    let renderer;
    let canvas;
    let ctx;

    beforeEach(() => {
        canvas = createMockCanvas();
        ctx = canvas.getContext();
        renderer = new Renderer(canvas);
    });

    test('should clear canvas on render', () => {
        renderer.render({ ship: null, asteroids: [], bullets: [], ufos: [] });
        expect(ctx.clearRect).toHaveBeenCalledWith(0, 0, 800, 600);
        expect(ctx.fillRect).toHaveBeenCalledWith(0, 0, 800, 600);
    });

    test('should set correct stroke style', () => {
        renderer.render({ ship: null, asteroids: [], bullets: [], ufos: [] });
        expect(ctx.strokeStyle).toBe('#FFFFFF');
        expect(ctx.lineWidth).toBe(2);
    });

    test('should draw ship at position', () => {
        const mockShip = {
            position: { x: 400, y: 300 },
            rotation: Math.PI / 4,
            getVertices: jest.fn(() => [
                { x: 0, y: -20 },
                { x: -15, y: 20 },
                { x: 15, y: 20 }
            ])
        };

        renderer.render({ ship: mockShip, asteroids: [], bullets: [], ufos: [] });

        expect(ctx.save).toHaveBeenCalled();
        expect(ctx.translate).toHaveBeenCalledWith(400, 300);
        expect(ctx.rotate).toHaveBeenCalledWith(Math.PI / 4);
        expect(ctx.beginPath).toHaveBeenCalled();
        expect(ctx.stroke).toHaveBeenCalled();
        expect(ctx.restore).toHaveBeenCalled();
    });

    test('should draw asteroids', () => {
        const mockAsteroid = {
            position: { x: 100, y: 100 },
            getVertices: jest.fn(() => [
                { x: 0, y: -30 },
                { x: 20, y: -20 },
                { x: 25, y: 10 },
                { x: 0, y: 30 },
                { x: -25, y: 10 },
                { x: -20, y: -20 }
            ])
        };

        renderer.render({ ship: null, asteroids: [mockAsteroid], bullets: [], ufos: [] });

        expect(ctx.translate).toHaveBeenCalledWith(100, 100);
        expect(ctx.stroke).toHaveBeenCalled();
    });

    test('should draw bullets', () => {
        const mockBullet = {
            position: { x: 200, y: 200 },
            direction: { x: 0, y: -1 }
        };

        renderer.render({ ship: null, asteroids: [], bullets: [mockBullet], ufos: [] });

        expect(ctx.beginPath).toHaveBeenCalled();
        expect(ctx.stroke).toHaveBeenCalled();
    });

    test('should draw UFO', () => {
        const mockUFO = {
            position: { x: 300, y: 100 }
        };

        renderer.render({ ship: null, asteroids: [], bullets: [], ufos: [mockUFO] });

        expect(ctx.beginPath).toHaveBeenCalled();
    });

    test('should draw explosion effect', () => {
        renderer.drawExplosion({ x: 400, y: 300 });
        expect(ctx.beginPath).toHaveBeenCalled();
    });
});
```

**Implementation:**

```javascript
// src/presentation/Renderer.js
export class Renderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = canvas.width;
        this.height = canvas.height;
    }

    render(gameState) {
        const { ctx, width, height } = this;
        const { ship, asteroids, bullets, ufos } = gameState;

        // Clear canvas with black background
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, width, height);

        // Set drawing style
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 2;

        // Draw entities
        if (ship) this.drawShip(ship);
        asteroids.forEach(a => this.drawAsteroid(a));
        bullets.forEach(b => this.drawBullet(b));
        ufos.forEach(u => this.drawUFO(u));
    }

    drawShip(ship) {
        const { ctx } = this;
        const vertices = ship.getVertices();

        ctx.save();
        ctx.translate(ship.position.x, ship.position.y);
        ctx.rotate(ship.rotation);

        ctx.beginPath();
        ctx.moveTo(vertices[0].x, vertices[0].y);
        ctx.lineTo(vertices[1].x, vertices[1].y);
        ctx.lineTo(vertices[2].x, vertices[2].y);
        ctx.closePath();
        ctx.stroke();

        // Draw thrust flame if thrusting
        if (ship.isThrusting) {
            this.drawThrust();
        }

        ctx.restore();
    }

    drawThrust() {
        const { ctx } = this;
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        ctx.moveTo(-5, 15);
        ctx.lineTo(0, 25 + Math.random() * 5);
        ctx.lineTo(5, 15);
        ctx.closePath();
        ctx.fill();
    }

    drawAsteroid(asteroid) {
        const { ctx } = this;
        const vertices = asteroid.getVertices();

        ctx.save();
        ctx.translate(asteroid.position.x, asteroid.position.y);

        ctx.beginPath();
        ctx.moveTo(vertices[0].x, vertices[0].y);
        for (let i = 1; i < vertices.length; i++) {
            ctx.lineTo(vertices[i].x, vertices[i].y);
        }
        ctx.closePath();
        ctx.stroke();

        ctx.restore();
    }

    drawBullet(bullet) {
        const { ctx } = this;

        ctx.beginPath();
        ctx.moveTo(bullet.position.x, bullet.position.y);
        ctx.lineTo(
            bullet.position.x - bullet.direction.x * 10,
            bullet.position.y - bullet.direction.y * 10
        );
        ctx.stroke();
    }

    drawUFO(ufo) {
        const { ctx } = this;

        ctx.save();
        ctx.translate(ufo.position.x, ufo.position.y);

        // Draw dome
        ctx.beginPath();
        ctx.arc(0, -5, 15, Math.PI, 0);
        ctx.stroke();

        // Draw base
        ctx.beginPath();
        ctx.ellipse(0, 5, 25, 8, 0, 0, Math.PI * 2);
        ctx.stroke();

        ctx.restore();
    }

    drawExplosion(position) {
        const { ctx } = this;
        const lines = 12;

        ctx.save();
        ctx.translate(position.x, position.y);

        for (let i = 0; i < lines; i++) {
            const angle = (i / lines) * Math.PI * 2;
            const length = 10 + Math.random() * 10;

            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(
                Math.cos(angle) * length,
                Math.sin(angle) * length
            );
            ctx.stroke();
        }

        ctx.restore();
    }
}
```

---

### Task 4.3: UIController

**Responsibilities:**
- Обновление HUD (score, lives, level)
- Отображение меню, паузы, Game Over
- Управление DOM элементами

**TDD Workflow:**

```javascript
// test/presentation/UIController.test.js
import { UIController } from '../../src/presentation/UIController.js';

describe('UIController', () => {
    let uiController;
    let mockDocument;
    let mockElements;

    beforeEach(() => {
        mockElements = {
            scoreEl: { textContent: '' },
            livesEl: { textContent: '' },
            levelEl: { textContent: '' },
            highScoreEl: { textContent: '' },
            menuEl: { style: { display: 'block' }, classList: { add: jest.fn(), remove: jest.fn() } },
            pauseEl: { style: { display: 'none' } },
            gameOverEl: { style: { display: 'none' } }
        };

        mockDocument = {
            getElementById: jest.fn((id) => {
                const map = {
                    'score': mockElements.scoreEl,
                    'lives': mockElements.livesEl,
                    'level': mockElements.levelEl,
                    'high-score': mockElements.highScoreEl,
                    'menu': mockElements.menuEl,
                    'pause': mockElements.pauseEl,
                    'game-over': mockElements.gameOverEl
                };
                return map[id];
            })
        };

        uiController = new UIController(mockDocument);
    });

    test('should update score display', () => {
        uiController.updateScore(1500);
        expect(mockElements.scoreEl.textContent).toBe('1500');
    });

    test('should update lives display', () => {
        uiController.updateLives(2);
        expect(mockElements.livesEl.textContent).toBe('2');
    });

    test('should update level display', () => {
        uiController.updateLevel(3);
        expect(mockElements.levelEl.textContent).toBe('3');
    });

    test('should update high score display', () => {
        uiController.updateHighScore(5000);
        expect(mockElements.highScoreEl.textContent).toBe('5000');
    });

    test('should show menu', () => {
        uiController.showMenu();
        expect(mockElements.menuEl.style.display).toBe('block');
        expect(mockElements.pauseEl.style.display).toBe('none');
        expect(mockElements.gameOverEl.style.display).toBe('none');
    });

    test('should show pause screen', () => {
        uiController.showPause();
        expect(mockElements.pauseEl.style.display).toBe('block');
    });

    test('should hide pause screen', () => {
        uiController.showPause();
        uiController.hidePause();
        expect(mockElements.pauseEl.style.display).toBe('none');
    });

    test('should show game over with score', () => {
        uiController.showGameOver(2500);
        expect(mockElements.gameOverEl.style.display).toBe('block');
    });

    test('should show level complete message', () => {
        uiController.showLevelComplete(2);
        // Should display "Level 2 Complete" message
    });
});
```

**Implementation:**

```javascript
// src/presentation/UIController.js
export class UIController {
    constructor(documentObj = document) {
        this.document = documentObj;
        
        this.scoreEl = documentObj.getElementById('score');
        this.livesEl = documentObj.getElementById('lives');
        this.levelEl = documentObj.getElementById('level');
        this.highScoreEl = documentObj.getElementById('high-score');
        this.menuEl = documentObj.getElementById('menu');
        this.pauseEl = documentObj.getElementById('pause');
        this.gameOverEl = documentObj.getElementById('game-over');
    }

    updateScore(score) {
        this.scoreEl.textContent = score;
    }

    updateLives(lives) {
        this.livesEl.textContent = lives;
    }

    updateLevel(level) {
        this.levelEl.textContent = level;
    }

    updateHighScore(score) {
        this.highScoreEl.textContent = score;
    }

    showMenu() {
        this.menuEl.style.display = 'block';
        this.pauseEl.style.display = 'none';
        this.gameOverEl.style.display = 'none';
    }

    hideMenu() {
        this.menuEl.style.display = 'none';
    }

    showPause() {
        this.pauseEl.style.display = 'block';
    }

    hidePause() {
        this.pauseEl.style.display = 'none';
    }

    showGameOver(score) {
        this.gameOverEl.style.display = 'block';
        this.gameOverEl.querySelector('.final-score').textContent = score;
    }

    hideGameOver() {
        this.gameOverEl.style.display = 'none';
    }

    showLevelComplete(level) {
        const message = document.createElement('div');
        message.className = 'level-complete';
        message.textContent = `Level ${level} Complete!`;
        this.menuEl.appendChild(message);
        setTimeout(() => message.remove(), 2000);
    }
}
```

---

## ✅ Definition of Done

- [ ] InputHandler обрабатывает все клавиши
- [ ] Renderer рисует все сущности через Canvas
- [ ] UIController обновляет HUD и экраны
- [ ] Покрытие тестами >80%
- [ ] Все тесты проходят
- [ ] Нет ESLint ошибок
- [ ] Интеграция с Game классом работает

---

## 📁 Files to Create

```
src/presentation/
├── InputHandler.js
├── Renderer.js
└── UIController.js

test/presentation/
├── InputHandler.test.js
├── Renderer.test.js
└── UIController.test.js
```

---

**Phase 4 Status:** Waiting for Phase 1-3 completion  
**Next:** Phase 1-3 → Phase 4 → Phase 5
