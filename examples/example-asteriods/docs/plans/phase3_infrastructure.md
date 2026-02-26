# Phase 3: Infrastructure Layer Implementation

**Status:** Pending  
**Duration:** 2 дня  
**Priority:** High  
**Dependencies:** Phase 1 (Domain) complete

---

## 📋 Overview

Реализация инфраструктурного слоя — абстракции над localStorage и аудио.

### Components

| Component | File | Tests |
|-----------|------|-------|
| Storage | `src/infrastructure/Storage.js` | `test/infrastructure/Storage.test.js` |
| AudioController | `src/infrastructure/AudioController.js` | `test/infrastructure/AudioController.test.js` |
| Test Mocks | `test/__mocks__/` | — |

---

## 🎯 Tasks

### Task 3.1: Storage

**Responsibilities:**
- Абстракция над localStorage
- Сохранение/загрузка рекордов
- Обработка ошибок (localStorage unavailable)

**TDD Workflow:**

```javascript
// test/infrastructure/Storage.test.js
import { Storage } from '../../src/infrastructure/Storage.js';

describe('Storage', () => {
    let mockLocalStorage;
    let storedData = {};

    beforeEach(() => {
        storedData = {};
        mockLocalStorage = {
            getItem: jest.fn((key) => storedData[key] || null),
            setItem: jest.fn((key, value) => { storedData[key] = value; }),
            removeItem: jest.fn((key) => { delete storedData[key]; })
        };
        global.localStorage = mockLocalStorage;
    });

    test('should save high score', () => {
        Storage.saveHighScore(5000);
        expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
            'asteroids-highscore',
            expect.any(String)
        );
    });

    test('should load high score', () => {
        storedData['asteroids-highscore'] = JSON.stringify({
            score: 3000,
            date: '2026-02-25T00:00:00.000Z'
        });
        const score = Storage.getHighScore();
        expect(score).toBe(3000);
    });

    test('should return 0 when no high score exists', () => {
        const score = Storage.getHighScore();
        expect(score).toBe(0);
    });

    test('should handle localStorage errors gracefully', () => {
        mockLocalStorage.setItem.mockImplementation(() => {
            throw new Error('localStorage unavailable');
        });
        expect(() => Storage.saveHighScore(1000)).not.toThrow();
    });

    test('should handle parse errors gracefully', () => {
        storedData['asteroids-highscore'] = 'invalid-json';
        const score = Storage.getHighScore();
        expect(score).toBe(0);
    });

    test('should save high score with timestamp', () => {
        Storage.saveHighScore(5000);
        const callArgs = mockLocalStorage.setItem.mock.calls[0];
        const data = JSON.parse(callArgs[1]);
        expect(data.score).toBe(5000);
        expect(data.date).toBeDefined();
    });
});
```

**Implementation:**

```javascript
// src/infrastructure/Storage.js
export class Storage {
    static saveHighScore(score) {
        try {
            const data = {
                score,
                date: new Date().toISOString()
            };
            localStorage.setItem('asteroids-highscore', JSON.stringify(data));
        } catch (e) {
            console.warn('Failed to save high score:', e.message);
        }
    }

    static getHighScore() {
        try {
            const data = localStorage.getItem('asteroids-highscore');
            if (!data) return 0;
            return JSON.parse(data).score || 0;
        } catch (e) {
            console.warn('Failed to load high score:', e.message);
            return 0;
        }
    }
}
```

---

### Task 3.2: AudioController

**Responsibilities:**
- Генерация звуков через Web Audio API (без внешних файлов)
- Oscillators для звуков выстрелов, взрывов, тяги
- Управление громкостью

**TDD Workflow:**

```javascript
// test/infrastructure/AudioController.test.js
import { AudioController } from '../../src/infrastructure/AudioController.js';

describe('AudioController', () => {
    let audioController;
    let mockAudioContext;
    let mockOscillator;
    let mockGain;

    beforeEach(() => {
        mockOscillator = {
            start: jest.fn(),
            stop: jest.fn(),
            connect: jest.fn(),
            frequency: { value: 0 },
            type: ''
        };

        mockGain = {
            connect: jest.fn(),
            gain: { value: 1 }
        };

        mockAudioContext = {
            createOscillator: jest.fn(() => mockOscillator),
            createGain: jest.fn(() => mockGain)
        };

        audioController = new AudioController(mockAudioContext);
    });

    test('should play shoot sound', () => {
        audioController.playShoot();
        expect(mockAudioContext.createOscillator).toHaveBeenCalled();
        expect(mockOscillator.start).toHaveBeenCalled();
    });

    test('should play explosion sound', () => {
        audioController.playExplosion();
        expect(mockAudioContext.createOscillator).toHaveBeenCalled();
    });

    test('should play hit sound', () => {
        audioController.playHit();
        expect(mockAudioContext.createOscillator).toHaveBeenCalled();
    });

    test('should start thrust sound', () => {
        audioController.startThrust();
        expect(mockOscillator.start).toHaveBeenCalled();
    });

    test('should stop thrust sound', () => {
        audioController.startThrust();
        audioController.stopThrust();
        expect(mockOscillator.stop).toHaveBeenCalled();
    });

    test('should set volume', () => {
        audioController.setVolume(0.5);
        expect(mockGain.gain.value).toBe(0.5);
    });

    test('should handle audio context errors', () => {
        mockAudioContext.createOscillator.mockImplementation(() => {
            throw new Error('Audio not available');
        });
        expect(() => audioController.playShoot()).not.toThrow();
    });
});
```

**Implementation:**

```javascript
// src/infrastructure/AudioController.js
export class AudioController {
    constructor(audioContext = new (window.AudioContext || window.webkitAudioContext)()) {
        this.audioContext = audioContext;
        this.masterGain = this.audioContext.createGain();
        this.masterGain.connect(this.audioContext.destination);
        this.masterGain.gain.value = 0.3; // Default volume
        this.thrustOscillator = null;
    }

    setVolume(value) {
        this.masterGain.gain.value = Math.max(0, Math.min(1, value));
    }

    playShoot() {
        try {
            const osc = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();
            
            osc.connect(gain);
            gain.connect(this.masterGain);
            
            osc.type = 'square';
            osc.frequency.setValueAtTime(880, this.audioContext.currentTime);
            osc.frequency.exponentialRampToValueAtTime(110, this.audioContext.currentTime + 0.1);
            
            gain.gain.setValueAtTime(1, this.audioContext.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1);
            
            osc.start(this.audioContext.currentTime);
            osc.stop(this.audioContext.currentTime + 0.1);
        } catch (e) {
            console.warn('Failed to play shoot sound:', e.message);
        }
    }

    playExplosion() {
        try {
            const osc = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();
            
            osc.connect(gain);
            gain.connect(this.masterGain);
            
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(100, this.audioContext.currentTime);
            osc.frequency.exponentialRampToValueAtTime(10, this.audioContext.currentTime + 0.3);
            
            gain.gain.setValueAtTime(1, this.audioContext.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
            
            osc.start(this.audioContext.currentTime);
            osc.stop(this.audioContext.currentTime + 0.3);
        } catch (e) {
            console.warn('Failed to play explosion sound:', e.message);
        }
    }

    playHit() {
        try {
            const osc = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();
            
            osc.connect(gain);
            gain.connect(this.masterGain);
            
            osc.type = 'square';
            osc.frequency.setValueAtTime(220, this.audioContext.currentTime);
            osc.frequency.linearRampToValueAtTime(110, this.audioContext.currentTime + 0.2);
            
            gain.gain.setValueAtTime(1, this.audioContext.currentTime);
            gain.gain.linearRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2);
            
            osc.start(this.audioContext.currentTime);
            osc.stop(this.audioContext.currentTime + 0.2);
        } catch (e) {
            console.warn('Failed to play hit sound:', e.message);
        }
    }

    startThrust() {
        try {
            if (this.thrustOscillator) return;
            
            this.thrustOscillator = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();
            
            this.thrustOscillator.connect(gain);
            gain.connect(this.masterGain);
            
            this.thrustOscillator.type = 'sawtooth';
            this.thrustOscillator.frequency.value = 50;
            
            gain.gain.value = 0.3;
            
            this.thrustOscillator.start(this.audioContext.currentTime);
        } catch (e) {
            console.warn('Failed to start thrust sound:', e.message);
        }
    }

    stopThrust() {
        try {
            if (this.thrustOscillator) {
                this.thrustOscillator.stop(this.audioContext.currentTime);
                this.thrustOscillator = null;
            }
        } catch (e) {
            console.warn('Failed to stop thrust sound:', e.message);
        }
    }
}
```

---

### Task 3.3: Test Mocks

**Responsibilities:**
- Моки для Canvas API
- Моки для localStorage
- Моки для Web Audio API

**Files:**

```javascript
// test/__mocks__/canvas.js
export function createMockCanvas() {
    const canvas = {
        width: 800,
        height: 600,
        getContext: jest.fn(() => createMockContext())
    };
    return canvas;
}

function createMockContext() {
    return {
        fillStyle: '',
        strokeStyle: '',
        lineWidth: 1,
        fillRect: jest.fn(),
        clearRect: jest.fn(),
        beginPath: jest.fn(),
        closePath: jest.fn(),
        moveTo: jest.fn(),
        lineTo: jest.fn(),
        arc: jest.fn(),
        stroke: jest.fn(),
        fill: jest.fn(),
        save: jest.fn(),
        restore: jest.fn(),
        translate: jest.fn(),
        rotate: jest.fn(),
        scale: jest.fn(),
        setTransform: jest.fn(),
        createImageData: jest.fn(() => ({ data: new Array(4) })),
        putImageData: jest.fn(),
        setLineDash: jest.fn(),
        getLineDash: jest.fn(() => [])
    };
}
```

```javascript
// test/__mocks__/localStorage.js
export function createMockLocalStorage() {
    const store = {};
    return {
        getItem: jest.fn((key) => store[key] || null),
        setItem: jest.fn((key, value) => { store[key] = value; }),
        removeItem: jest.fn((key) => { delete store[key]; }),
        clear: jest.fn(() => { Object.keys(store).forEach(k => delete store[k]); })
    };
}
```

```javascript
// test/__mocks__/audio.js
export function createMockAudioContext() {
    return {
        createOscillator: jest.fn(() => ({
            start: jest.fn(),
            stop: jest.fn(),
            connect: jest.fn(),
            frequency: { value: 0, setValueAtTime: jest.fn(), exponentialRampToValueAtTime: jest.fn() },
            type: ''
        })),
        createGain: jest.fn(() => ({
            connect: jest.fn(),
            gain: { value: 1, setValueAtTime: jest.fn(), exponentialRampToValueAtTime: jest.fn() }
        })),
        currentTime: 0,
        destination: {}
    };
}
```

---

## ✅ Definition of Done

- [ ] Storage реализован с обработкой ошибок
- [ ] AudioController генерирует звуки через Web Audio API
- [ ] Test mocks созданы для Canvas, localStorage, Audio
- [ ] Покрытие тестами >80%
- [ ] Все тесты проходят
- [ ] Нет ESLint ошибок

---

## 📁 Files to Create

```
src/infrastructure/
├── Storage.js
└── AudioController.js

test/infrastructure/
├── Storage.test.js
└── AudioController.test.js

test/__mocks__/
├── canvas.js
├── localStorage.js
└── audio.js
```

---

**Phase 3 Status:** Waiting for Phase 1 completion  
**Next:** Phase 1 → Phase 3
