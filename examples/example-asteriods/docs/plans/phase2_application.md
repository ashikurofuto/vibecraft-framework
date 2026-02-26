# Phase 2: Application Layer Implementation

**Status:** Pending  
**Duration:** 5 дней  
**Priority:** High  
**Dependencies:** Phase 1 (Domain Layer) complete

---

## 📋 Overview

Реализация прикладного слоя — игровой цикл, управление состоянием, подсчёт очков.

### Components

| Component | File | Tests |
|-----------|------|-------|
| GameState | `src/application/GameState.js` | `test/application/GameState.test.js` |
| ScoreManager | `src/application/ScoreManager.js` | `test/application/ScoreManager.test.js` |
| GameLoop | `src/application/GameLoop.js` | `test/application/GameLoop.test.js` |
| Game | `src/application/Game.js` | `test/application/Game.test.js` |

---

## 🎯 Tasks

### Task 2.1: GameState

**Responsibilities:**
- Управление состоянием игры (menu, playing, paused, gameover)
- Отслеживание уровня, очков, жизней
- Переходы между состояниями

**TDD Workflow:**

```javascript
// test/application/GameState.test.js
import { GameState } from '../src/application/GameState.js';

describe('GameState', () => {
    test('should start in menu state', () => {
        const state = new GameState();
        expect(state.isMenu()).toBe(true);
        expect(state.isPlaying()).toBe(false);
    });

    test('should transition to playing on start', () => {
        const state = new GameState();
        state.start();
        expect(state.isPlaying()).toBe(true);
        expect(state.isMenu()).toBe(false);
    });

    test('should pause when playing', () => {
        const state = new GameState();
        state.start();
        state.pause();
        expect(state.isPaused()).toBe(true);
    });

    test('should resume when paused', () => {
        const state = new GameState();
        state.start();
        state.pause();
        state.resume();
        expect(state.isPlaying()).toBe(true);
    });

    test('should decrement lives on hit', () => {
        const state = new GameState();
        state.start();
        expect(state.lives).toBe(3);
        state.hit();
        expect(state.lives).toBe(2);
    });

    test('should trigger game over when lives reach 0', () => {
        const state = new GameState();
        state.start();
        state.lives = 1;
        state.hit();
        expect(state.isGameOver()).toBe(true);
    });

    test('should increment level on level complete', () => {
        const state = new GameState();
        state.start();
        expect(state.level).toBe(1);
        state.nextLevel();
        expect(state.level).toBe(2);
    });

    test('should not pause when in menu', () => {
        const state = new GameState();
        state.pause();
        expect(state.isMenu()).toBe(true); // stays in menu
    });
});
```

**Implementation:**

```javascript
// src/application/GameState.js
export class GameState {
    constructor() {
        this.state = 'menu'; // 'menu' | 'playing' | 'paused' | 'gameover'
        this.level = 1;
        this.lives = 3;
        this.score = 0;
        this.highScore = 0;
    }

    isMenu() { return this.state === 'menu'; }
    isPlaying() { return this.state === 'playing'; }
    isPaused() { return this.state === 'paused'; }
    isGameOver() { return this.state === 'gameover'; }

    start() {
        this.state = 'playing';
        this.level = 1;
        this.lives = 3;
        this.score = 0;
    }

    pause() {
        if (this.state === 'playing') {
            this.state = 'paused';
        }
    }

    resume() {
        if (this.state === 'paused') {
            this.state = 'playing';
        }
    }

    hit() {
        this.lives--;
        if (this.lives <= 0) {
            this.state = 'gameover';
        }
    }

    nextLevel() {
        this.level++;
    }

    addScore(points) {
        this.score += points;
        if (this.score > this.highScore) {
            this.highScore = this.score;
        }
    }
}
```

---

### Task 2.2: ScoreManager

**Responsibilities:**
- Подсчёт текущих очков
- Отслеживание рекорда
- Сохранение/загрузка рекорда

**TDD Workflow:**

```javascript
// test/application/ScoreManager.test.js
import { ScoreManager } from '../src/application/ScoreManager.js';

describe('ScoreManager', () => {
    let scoreManager;
    let mockStorage;

    beforeEach(() => {
        mockStorage = {
            saveHighScore: jest.fn(),
            getHighScore: jest.fn(() => 1000)
        };
        scoreManager = new ScoreManager(mockStorage);
    });

    test('should start with zero score', () => {
        expect(scoreManager.getCurrentScore()).toBe(0);
    });

    test('should load high score from storage', () => {
        expect(scoreManager.getHighScore()).toBe(1000);
    });

    test('should add score', () => {
        scoreManager.addScore(100);
        expect(scoreManager.getCurrentScore()).toBe(100);
    });

    test('should update high score when exceeded', () => {
        scoreManager.addScore(1500);
        expect(scoreManager.getHighScore()).toBe(1500);
        expect(mockStorage.saveHighScore).toHaveBeenCalledWith(1500);
    });

    test('should not update high score when not exceeded', () => {
        scoreManager.addScore(500);
        expect(mockStorage.saveHighScore).not.toHaveBeenCalled();
    });

    test('should reset score on new game', () => {
        scoreManager.addScore(100);
        scoreManager.reset();
        expect(scoreManager.getCurrentScore()).toBe(0);
    });
});
```

---

### Task 2.3: GameLoop

**Responsibilities:**
- Фиксированный timestep (1/60 сек)
- Accumulator pattern для физики
- Управление циклом update/render

**TDD Workflow:**

```javascript
// test/application/GameLoop.test.js
import { GameLoop } from '../src/application/GameLoop.js';

describe('GameLoop', () => {
    let gameLoop;
    let mockUpdate;
    let mockRender;

    beforeEach(() => {
        mockUpdate = jest.fn();
        mockRender = jest.fn();
        gameLoop = new GameLoop(mockUpdate, mockRender);
    });

    test('should start loop', () => {
        gameLoop.start();
        expect(gameLoop.isRunning).toBe(true);
    });

    test('should stop loop', () => {
        gameLoop.start();
        gameLoop.stop();
        expect(gameLoop.isRunning).toBe(false);
    });

    test('should call update with fixed timestep', () => {
        gameLoop.start();
        gameLoop.tick(1000); // currentTime
        expect(mockUpdate).toHaveBeenCalledWith(1/60);
    });

    test('should accumulate time for multiple updates', () => {
        gameLoop.start();
        gameLoop.tick(1000);
        gameLoop.tick(1000 + 50); // 50ms later
        // Should have accumulated enough for 3 updates
        expect(mockUpdate).toHaveBeenCalledTimes(3);
    });

    test('should call render after updates', () => {
        gameLoop.start();
        gameLoop.tick(1000);
        expect(mockRender).toHaveBeenCalled();
    });
});
```

**Implementation:**

```javascript
// src/application/GameLoop.js
export class GameLoop {
    constructor(updateCallback, renderCallback) {
        this.updateCallback = updateCallback;
        this.renderCallback = renderCallback;
        this.lastTime = 0;
        this.accumulator = 0;
        this.fixedTimestep = 1 / 60; // 16.67ms
        this.isRunning = false;
        this.animationFrameId = null;
    }

    start() {
        this.isRunning = true;
        this.lastTime = performance.now();
        this.tick(this.lastTime);
    }

    stop() {
        this.isRunning = false;
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
    }

    tick(currentTime) {
        if (!this.isRunning) return;

        let deltaTime = (currentTime - this.lastTime) / 1000;
        this.lastTime = currentTime;

        // Cap deltaTime to prevent spiral of death
        if (deltaTime > 0.25) deltaTime = 0.25;

        this.accumulator += deltaTime;

        while (this.accumulator >= this.fixedTimestep) {
            this.updateCallback(this.fixedTimestep);
            this.accumulator -= this.fixedTimestep;
        }

        this.renderCallback();

        this.animationFrameId = requestAnimationFrame((t) => this.tick(t));
    }
}
```

---

### Task 2.4: Game (Facade)

**Responsibilities:**
- Объединяет все слои
- Основной интерфейс для Presentation
- Управление сущностями

**TDD Workflow:**

```javascript
// test/application/Game.test.js
import { Game } from '../src/application/Game.js';

describe('Game', () => {
    let game;
    let mockRenderer;
    let mockInputHandler;
    let mockStorage;
    let mockAudio;

    beforeEach(() => {
        mockRenderer = { render: jest.fn() };
        mockInputHandler = { getInput: jest.fn(() => ({})) };
        mockStorage = { getHighScore: jest.fn(() => 0) };
        mockAudio = { playShoot: jest.fn() };

        game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
    });

    test('should initialize in menu state', () => {
        game.initialize();
        expect(game.getState().isMenu()).toBe(true);
    });

    test('should start game', () => {
        game.initialize();
        game.start();
        expect(game.getState().isPlaying()).toBe(true);
    });

    test('should handle input when playing', () => {
        game.initialize();
        game.start();
        game.handleInput({ thrust: true });
        // Ship should be thrusting
    });

    test('should not handle input when paused', () => {
        game.initialize();
        game.start();
        game.pause();
        game.handleInput({ thrust: true });
        // Input should be ignored
    });

    test('should pause on P key', () => {
        game.initialize();
        game.start();
        game.handleInput({ pause: true });
        expect(game.getState().isPaused()).toBe(true);
    });

    test('should get current score', () => {
        game.initialize();
        game.start();
        game.addScore(100);
        expect(game.getScore()).toBe(100);
    });

    test('should get game state for renderer', () => {
        game.initialize();
        game.start();
        const state = game.getState();
        expect(state).toBeDefined();
    });
});
```

---

## ✅ Definition of Done

- [ ] Все 4 модуля реализованы
- [ ] Все тесты написаны ДО кода (TDD)
- [ ] Покрытие тестами >85%
- [ ] Все тесты проходят: `npm test`
- [ ] Нет ESLint ошибок
- [ ] GameState корректно управляет переходами
- [ ] GameLoop использует fixed timestep (1/60s)
- [ ] Game интегрирует все компоненты

---

## 📁 Files to Create

```
src/application/
├── GameState.js
├── ScoreManager.js
├── GameLoop.js
└── Game.js

test/application/
├── GameState.test.js
├── ScoreManager.test.js
├── GameLoop.test.js
└── Game.test.js
```

---

**Phase 2 Status:** Waiting for Phase 1 completion  
**Next:** Phase 1 → Phase 2
