/**
 * InputHandler Event Tests — Phase 5
 *
 * @description Тесты InputHandler с реальными keyboard событиями (jsdom)
 * @see src/presentation/InputHandler.js
 */

import { jest } from '@jest/globals';

describe('InputHandler — Event Integration', () => {
    let InputHandler;
    let inputHandler;
    let mockWindow;
    let eventListeners;

    beforeEach(async () => {
        // Динамический импорт
        InputHandler = (await import('../../../src/presentation/InputHandler.js')).InputHandler;

        // Создаём mock window с реальной системой событий
        eventListeners = {
            keydown: [],
            keyup: []
        };

        mockWindow = {
            addEventListener: jest.fn((event, handler) => {
                if (event === 'keydown' || event === 'keyup') {
                    eventListeners[event].push(handler);
                }
            }),
            removeEventListener: jest.fn()
        };

        inputHandler = new InputHandler(mockWindow);
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Event Listener Registration', () => {
        test('should register keydown event listener on init', () => {
            expect(mockWindow.addEventListener).toHaveBeenCalledWith(
                'keydown',
                expect.any(Function)
            );
        });

        test('should register keyup event listener on init', () => {
            expect(mockWindow.addEventListener).toHaveBeenCalledWith(
                'keyup',
                expect.any(Function)
            );
        });

        test('should have both listeners registered', () => {
            expect(eventListeners.keydown.length).toBe(1);
            expect(eventListeners.keyup.length).toBe(1);
        });
    });

    describe('Key Press Detection', () => {
        test('should detect ArrowUp key press', () => {
            const keydownEvent = new KeyboardEvent('keydown', { code: 'ArrowUp' });
            eventListeners.keydown.forEach(fn => fn(keydownEvent));

            expect(inputHandler.isPressed('ArrowUp')).toBe(true);
        });

        test('should detect ArrowDown key release', () => {
            // Нажимаем
            const keydownEvent = new KeyboardEvent('keydown', { code: 'ArrowDown' });
            eventListeners.keydown.forEach(fn => fn(keydownEvent));

            // Отпускаем
            const keyupEvent = new KeyboardEvent('keyup', { code: 'ArrowDown' });
            eventListeners.keyup.forEach(fn => fn(keyupEvent));

            expect(inputHandler.isPressed('ArrowDown')).toBe(false);
        });

        test('should return false for unpressed key', () => {
            expect(inputHandler.isPressed('ArrowLeft')).toBe(false);
        });

        test('should track multiple keys simultaneously', () => {
            const arrowUpEvent = new KeyboardEvent('keydown', { code: 'ArrowUp' });
            const spaceEvent = new KeyboardEvent('keydown', { code: 'Space' });

            eventListeners.keydown.forEach(fn => fn(arrowUpEvent));
            eventListeners.keydown.forEach(fn => fn(spaceEvent));

            expect(inputHandler.isPressed('ArrowUp')).toBe(true);
            expect(inputHandler.isPressed('Space')).toBe(true);
        });
    });

    describe('Key Mappings', () => {
        const keyMappings = [
            { code: 'ArrowUp', expected: 'thrust' },
            { code: 'ArrowDown', expected: 'thrust' },
            { code: 'KeyW', expected: 'thrust' },
            { code: 'KeyS', expected: 'thrust' },
            { code: 'ArrowLeft', expected: 'rotateLeft' },
            { code: 'KeyA', expected: 'rotateLeft' },
            { code: 'ArrowRight', expected: 'rotateRight' },
            { code: 'KeyD', expected: 'rotateRight' },
            { code: 'Space', expected: 'fire' },
            { code: 'KeyP', expected: 'pause' },
            { code: 'KeyH', expected: 'hyperspace' }
        ];

        test.each(keyMappings)(
            'should map $code to $expected',
            ({ code, expected }) => {
                const keydownEvent = new KeyboardEvent('keydown', { code });
                eventListeners.keydown.forEach(fn => fn(keydownEvent));

                const state = inputHandler.getState();
                expect(state[expected]).toBe(true);
            }
        );
    });

    describe('Edge Detection (wasJustPressed)', () => {
        test('should detect first frame of key press', () => {
            const spaceEvent = new KeyboardEvent('keydown', { code: 'Space' });

            // Первое нажатие
            eventListeners.keydown.forEach(fn => fn(spaceEvent));

            expect(inputHandler.wasJustPressed('Space')).toBe(true);
        });

        test('should not trigger wasJustPressed on held key', () => {
            const spaceEvent = new KeyboardEvent('keydown', { code: 'Space' });

            // Первое нажатие
            eventListeners.keydown.forEach(fn => fn(spaceEvent));
            inputHandler.endFrame(); // Завершаем кадр

            // Клавиша всё ещё зажата (новое событие keydown не приходит)
            // wasJustPressed должен вернуть false
            expect(inputHandler.wasJustPressed('Space')).toBe(false);
        });

        test('should reset after key release and press again', () => {
            const spaceEvent = new KeyboardEvent('keydown', { code: 'Space' });
            const spaceUpEvent = new KeyboardEvent('keyup', { code: 'Space' });

            // Нажимаем
            eventListeners.keydown.forEach(fn => fn(spaceEvent));
            expect(inputHandler.wasJustPressed('Space')).toBe(true);

            // Завершаем кадр
            inputHandler.endFrame();

            // Отпускаем
            eventListeners.keyup.forEach(fn => fn(spaceUpEvent));
            inputHandler.endFrame();

            // Снова нажимаем
            eventListeners.keydown.forEach(fn => fn(spaceEvent));
            expect(inputHandler.wasJustPressed('Space')).toBe(true);
        });
    });

    describe('Input State Object', () => {
        test('should get complete input state', () => {
            const thrustEvent = new KeyboardEvent('keydown', { code: 'ArrowUp' });
            const rotateEvent = new KeyboardEvent('keydown', { code: 'ArrowLeft' });

            eventListeners.keydown.forEach(fn => fn(thrustEvent));
            eventListeners.keydown.forEach(fn => fn(rotateEvent));

            const state = inputHandler.getState();

            expect(state).toEqual({
                thrust: true,
                rotateLeft: true,
                rotateRight: false,
                fire: false,
                pause: false,
                hyperspace: false
            });
        });

        test('should return default state when no keys pressed', () => {
            const state = inputHandler.getState();

            expect(state).toEqual({
                thrust: false,
                rotateLeft: false,
                rotateRight: false,
                fire: false,
                pause: false,
                hyperspace: false
            });
        });
    });

    describe('Prevent Default Behavior', () => {
        test('should call preventDefault on arrow keys', () => {
            const preventDefaultMock = jest.fn();
            const arrowUpEvent = {
                code: 'ArrowUp',
                preventDefault: preventDefaultMock
            };

            eventListeners.keydown.forEach(fn => fn(arrowUpEvent));

            expect(preventDefaultMock).toHaveBeenCalled();
        });

        test('should call preventDefault on space key', () => {
            const preventDefaultMock = jest.fn();
            const spaceEvent = {
                code: 'Space',
                preventDefault: preventDefaultMock
            };

            eventListeners.keydown.forEach(fn => fn(spaceEvent));

            expect(preventDefaultMock).toHaveBeenCalled();
        });

        test('should not call preventDefault on unrelated keys', () => {
            const preventDefaultMock = jest.fn();
            const enterEvent = {
                code: 'Enter',
                preventDefault: preventDefaultMock
            };

            eventListeners.keydown.forEach(fn => fn(enterEvent));

            expect(preventDefaultMock).not.toHaveBeenCalled();
        });
    });

    describe('Input Reset', () => {
        test('should clear all keys on reset', () => {
            const spaceEvent = new KeyboardEvent('keydown', { code: 'Space' });
            eventListeners.keydown.forEach(fn => fn(spaceEvent));

            expect(inputHandler.isPressed('Space')).toBe(true);

            inputHandler.reset();

            expect(inputHandler.isPressed('Space')).toBe(false);
        });

        test('should reset previous frame state', () => {
            const spaceEvent = new KeyboardEvent('keydown', { code: 'Space' });
            eventListeners.keydown.forEach(fn => fn(spaceEvent));

            inputHandler.endFrame();
            inputHandler.reset();

            expect(inputHandler.wasJustPressed('Space')).toBe(false);
        });
    });

    describe('Continuous Input Stream', () => {
        test('should handle rapid key presses', () => {
            const spaceEvent = new KeyboardEvent('keydown', { code: 'Space' });
            const spaceUpEvent = new KeyboardEvent('keyup', { code: 'Space' });

            // Быстрые нажатия (3 раза)
            for (let i = 0; i < 3; i++) {
                eventListeners.keydown.forEach(fn => fn(spaceEvent));
                expect(inputHandler.wasJustPressed('Space')).toBe(true);

                inputHandler.endFrame();

                eventListeners.keyup.forEach(fn => fn(spaceUpEvent));
                inputHandler.endFrame();
            }
        });

        test('should handle overlapping key presses', () => {
            // Нажимаем ArrowUp
            const upEvent = new KeyboardEvent('keydown', { code: 'ArrowUp' });
            eventListeners.keydown.forEach(fn => fn(upEvent));

            // Не отпуская, нажимаем Space
            const spaceEvent = new KeyboardEvent('keydown', { code: 'Space' });
            eventListeners.keydown.forEach(fn => fn(spaceEvent));

            const state = inputHandler.getState();
            expect(state.thrust).toBe(true);
            expect(state.fire).toBe(true);

            // Отпускаем только ArrowUp
            const upUpEvent = new KeyboardEvent('keyup', { code: 'ArrowUp' });
            eventListeners.keyup.forEach(fn => fn(upUpEvent));

            const newState = inputHandler.getState();
            expect(newState.thrust).toBe(false);
            expect(newState.fire).toBe(true);
        });
    });

    describe('Frame Management', () => {
        test('should track previous frame state', () => {
            const spaceEvent = new KeyboardEvent('keydown', { code: 'Space' });

            eventListeners.keydown.forEach(fn => fn(spaceEvent));
            inputHandler.endFrame();

            // Space всё ещё зажат в новом кадре
            expect(inputHandler.isPressed('Space')).toBe(true);
            // Но wasJustPressed должен быть false, так как это не первый кадр
            expect(inputHandler.wasJustPressed('Space')).toBe(false);
        });

        test('should clear previous frame on reset', () => {
            const spaceEvent = new KeyboardEvent('keydown', { code: 'Space' });
            eventListeners.keydown.forEach(fn => fn(spaceEvent));

            inputHandler.endFrame();
            inputHandler.reset();

            // После сброса предыдущее состояние должно быть очищено
            expect(inputHandler.isPressed('Space')).toBe(false);
        });
    });
});
