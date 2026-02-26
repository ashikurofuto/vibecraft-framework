/**
 * Tests for InputHandler
 * 
 * @description Тесты для компонента обработки ввода с клавиатуры
 * @module InputHandler
 * @see src/presentation/InputHandler.js
 */

import { jest } from '@jest/globals';

describe('InputHandler', () => {
    let InputHandler;
    let inputHandler;
    let mockWindow;
    let listeners;

    // Моки для клавиш
    const KEYS = {
        ARROW_UP: 'ArrowUp',
        ARROW_DOWN: 'ArrowDown',
        ARROW_LEFT: 'ArrowLeft',
        ARROW_RIGHT: 'ArrowRight',
        KEY_W: 'KeyW',
        KEY_A: 'KeyA',
        KEY_S: 'KeyS',
        KEY_D: 'KeyD',
        SPACE: 'Space',
        KEY_P: 'KeyP',
        KEY_H: 'KeyH',
        KEY_R: 'KeyR'
    };

    beforeEach(async () => {
        // Динамический импорт для изоляции тестов
        InputHandler = (await import('../../../src/presentation/InputHandler.js')).InputHandler;

        // Создаём мок window с отслеживанием event listeners
        listeners = { keydown: [], keyup: [] };
        mockWindow = {
            addEventListener: jest.fn((event, handler) => {
                if (event === 'keydown' || event === 'keyup') {
                    listeners[event].push(handler);
                }
            }),
            removeEventListener: jest.fn()
        };

        inputHandler = new InputHandler(mockWindow);
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('constructor', () => {
        test('should register keydown event listener', () => {
            expect(mockWindow.addEventListener).toHaveBeenCalledWith(
                'keydown',
                expect.any(Function)
            );
        });

        test('should register keyup event listener', () => {
            expect(mockWindow.addEventListener).toHaveBeenCalledWith(
                'keyup',
                expect.any(Function)
            );
        });

        test('should use default window if not provided', async () => {
            const DefaultInputHandler = (await import('../../../src/presentation/InputHandler.js')).InputHandler;
            // При создании без параметров должен использоваться window по умолчанию
            const handler = new DefaultInputHandler();
            expect(handler).toBeDefined();
        });
    });

    describe('isPressed', () => {
        test('should return true for pressed key', () => {
            const event = { code: KEYS.ARROW_UP, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(event));

            expect(inputHandler.isPressed(KEYS.ARROW_UP)).toBe(true);
        });

        test('should return false for released key', () => {
            // Нажимаем клавишу
            const keydownEvent = { code: KEYS.ARROW_UP, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(keydownEvent));

            // Отпускаем клавишу
            const keyupEvent = { code: KEYS.ARROW_UP };
            listeners.keyup.forEach(fn => fn(keyupEvent));

            expect(inputHandler.isPressed(KEYS.ARROW_UP)).toBe(false);
        });

        test('should return false for unpressed key', () => {
            expect(inputHandler.isPressed(KEYS.ARROW_UP)).toBe(false);
        });

        test('should track multiple keys simultaneously', () => {
            const event1 = { code: KEYS.ARROW_UP, preventDefault: jest.fn() };
            const event2 = { code: KEYS.SPACE, preventDefault: jest.fn() };

            listeners.keydown.forEach(fn => fn(event1));
            listeners.keydown.forEach(fn => fn(event2));

            expect(inputHandler.isPressed(KEYS.ARROW_UP)).toBe(true);
            expect(inputHandler.isPressed(KEYS.SPACE)).toBe(true);
        });

        test('should call preventDefault on keydown events', () => {
            const preventDefault = jest.fn();
            const event = { code: KEYS.ARROW_UP, preventDefault };

            listeners.keydown.forEach(fn => fn(event));

            expect(preventDefault).toHaveBeenCalled();
        });
    });

    describe('wasJustPressed (edge detection)', () => {
        test('should return true when key was just pressed in current frame', () => {
            const event = { code: KEYS.SPACE, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(event));

            expect(inputHandler.wasJustPressed(KEYS.SPACE)).toBe(true);
        });

        test('should return false when key was held from previous frame', () => {
            const event = { code: KEYS.SPACE, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(event));

            // Завершаем кадр — текущее состояние становится предыдущим
            inputHandler.endFrame();

            // Клавиша всё ещё нажата, но не "только что"
            expect(inputHandler.wasJustPressed(KEYS.SPACE)).toBe(false);
        });

        test('should return false for unpressed key', () => {
            expect(inputHandler.wasJustPressed(KEYS.SPACE)).toBe(false);
        });

        test('should detect new key press after endFrame', () => {
            // Сначала нажимаем и завершаем кадр
            const event1 = { code: KEYS.ARROW_UP, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(event1));
            inputHandler.endFrame();

            // Отпускаем старую клавишу и нажимаем новую
            const keyupEvent = { code: KEYS.ARROW_UP };
            listeners.keyup.forEach(fn => fn(keyupEvent));

            const event2 = { code: KEYS.SPACE, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(event2));

            expect(inputHandler.wasJustPressed(KEYS.ARROW_UP)).toBe(false);
            expect(inputHandler.wasJustPressed(KEYS.SPACE)).toBe(true);
        });
    });

    describe('endFrame', () => {
        test('should save current key state as previous state', () => {
            const event = { code: KEYS.ARROW_UP, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(event));

            inputHandler.endFrame();

            // После endFrame wasJustPressed должен вернуть false
            expect(inputHandler.wasJustPressed(KEYS.ARROW_UP)).toBe(false);
        });

        test('should allow detection of new key presses in next frame', () => {
            inputHandler.endFrame();

            const event = { code: KEYS.SPACE, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(event));

            expect(inputHandler.wasJustPressed(KEYS.SPACE)).toBe(true);
        });
    });

    describe('getState', () => {
        test('should return input state object with all actions', () => {
            const state = inputHandler.getState();

            expect(state).toHaveProperty('thrust');
            expect(state).toHaveProperty('rotateLeft');
            expect(state).toHaveProperty('rotateRight');
            expect(state).toHaveProperty('fire');
            expect(state).toHaveProperty('hyperspace');
            expect(state).toHaveProperty('pause');
        });

        test('should map ArrowUp and KeyW to thrust', () => {
            const eventUp = { code: KEYS.ARROW_UP, preventDefault: jest.fn() };
            const eventW = { code: KEYS.KEY_W, preventDefault: jest.fn() };

            listeners.keydown.forEach(fn => fn(eventUp));
            let state = inputHandler.getState();
            expect(state.thrust).toBe(true);

            listeners.keyup.forEach(fn => fn({ code: KEYS.ARROW_UP }));
            listeners.keydown.forEach(fn => fn(eventW));
            state = inputHandler.getState();
            expect(state.thrust).toBe(true);
        });

        test('should map ArrowLeft and KeyA to rotateLeft', () => {
            const eventLeft = { code: KEYS.ARROW_LEFT, preventDefault: jest.fn() };
            const eventA = { code: KEYS.KEY_A, preventDefault: jest.fn() };

            listeners.keydown.forEach(fn => fn(eventLeft));
            let state = inputHandler.getState();
            expect(state.rotateLeft).toBe(true);

            listeners.keyup.forEach(fn => fn({ code: KEYS.ARROW_LEFT }));
            listeners.keydown.forEach(fn => fn(eventA));
            state = inputHandler.getState();
            expect(state.rotateLeft).toBe(true);
        });

        test('should map ArrowRight and KeyD to rotateRight', () => {
            const eventRight = { code: KEYS.ARROW_RIGHT, preventDefault: jest.fn() };
            const eventD = { code: KEYS.KEY_D, preventDefault: jest.fn() };

            listeners.keydown.forEach(fn => fn(eventRight));
            let state = inputHandler.getState();
            expect(state.rotateRight).toBe(true);

            listeners.keyup.forEach(fn => fn({ code: KEYS.ARROW_RIGHT }));
            listeners.keydown.forEach(fn => fn(eventD));
            state = inputHandler.getState();
            expect(state.rotateRight).toBe(true);
        });

        test('should map Space to fire', () => {
            const event = { code: KEYS.SPACE, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(event));

            const state = inputHandler.getState();
            expect(state.fire).toBe(true);
        });

        test('should map KeyH to hyperspace', () => {
            const event = { code: KEYS.KEY_H, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(event));

            const state = inputHandler.getState();
            expect(state.hyperspace).toBe(true);
        });

        test('should map KeyP to pause', () => {
            const event = { code: KEYS.KEY_P, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(event));

            const state = inputHandler.getState();
            expect(state.pause).toBe(true);
        });

        test('should return all false when no keys pressed', () => {
            const state = inputHandler.getState();

            expect(state.thrust).toBe(false);
            expect(state.rotateLeft).toBe(false);
            expect(state.rotateRight).toBe(false);
            expect(state.fire).toBe(false);
            expect(state.hyperspace).toBe(false);
            expect(state.pause).toBe(false);
        });

        test('should handle multiple simultaneous inputs', () => {
            const thrustEvent = { code: KEYS.ARROW_UP, preventDefault: jest.fn() };
            const fireEvent = { code: KEYS.SPACE, preventDefault: jest.fn() };

            listeners.keydown.forEach(fn => fn(thrustEvent));
            listeners.keydown.forEach(fn => fn(fireEvent));

            const state = inputHandler.getState();
            expect(state.thrust).toBe(true);
            expect(state.fire).toBe(true);
        });
    });

    describe('key mappings', () => {
        const keyMappings = [
            { code: KEYS.ARROW_UP, action: 'thrust', description: 'ArrowUp → thrust' },
            { code: KEYS.KEY_W, action: 'thrust', description: 'KeyW → thrust' },
            { code: KEYS.ARROW_LEFT, action: 'rotateLeft', description: 'ArrowLeft → rotateLeft' },
            { code: KEYS.KEY_A, action: 'rotateLeft', description: 'KeyA → rotateLeft' },
            { code: KEYS.ARROW_RIGHT, action: 'rotateRight', description: 'ArrowRight → rotateRight' },
            { code: KEYS.KEY_D, action: 'rotateRight', description: 'KeyD → rotateRight' },
            { code: KEYS.SPACE, action: 'fire', description: 'Space → fire' },
            { code: KEYS.KEY_H, action: 'hyperspace', description: 'KeyH → hyperspace' },
            { code: KEYS.KEY_P, action: 'pause', description: 'KeyP → pause' }
        ];

        test.each(keyMappings)('$description', ({ code, action }) => {
            const event = { code, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(event));

            const state = inputHandler.getState();
            expect(state[action]).toBe(true);
        });
    });

    describe('input state transitions', () => {
        test('should correctly track key press and release cycle', () => {
            // Начальное состояние
            expect(inputHandler.isPressed(KEYS.SPACE)).toBe(false);
            expect(inputHandler.wasJustPressed(KEYS.SPACE)).toBe(false);

            // Нажатие
            const keydownEvent = { code: KEYS.SPACE, preventDefault: jest.fn() };
            listeners.keydown.forEach(fn => fn(keydownEvent));

            expect(inputHandler.isPressed(KEYS.SPACE)).toBe(true);
            expect(inputHandler.wasJustPressed(KEYS.SPACE)).toBe(true);

            // Завершение кадра
            inputHandler.endFrame();

            expect(inputHandler.isPressed(KEYS.SPACE)).toBe(true);
            expect(inputHandler.wasJustPressed(KEYS.SPACE)).toBe(false);

            // Отпускание
            const keyupEvent = { code: KEYS.SPACE };
            listeners.keyup.forEach(fn => fn(keyupEvent));

            expect(inputHandler.isPressed(KEYS.SPACE)).toBe(false);
            expect(inputHandler.wasJustPressed(KEYS.SPACE)).toBe(false);
        });
    });
});
