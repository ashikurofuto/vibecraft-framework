/**
 * Integration Tests — Phase 5
 *
 * @description Тесты взаимодействия всех слоёв игры (Domain + Application + Infrastructure + Presentation)
 * @see src/application/Game.js
 * @see src/domain/entities/Ship.js
 * @see src/domain/entities/Asteroid.js
 * @see src/infrastructure/Storage.js
 * @see src/presentation/InputHandler.js
 */

import { jest } from '@jest/globals';

describe('Integration — Game Layers', () => {
    let Game;
    let Ship;
    let Asteroid;
    let GameState;
    let Storage;
    let Vector2D;

    let mockRenderer;
    let mockInputHandler;
    let mockStorage;
    let mockAudio;
    let game;

    beforeEach(async () => {
        // Динамический импорт для изоляции тестов
        const modules = await Promise.all([
            import('../../../src/application/Game.js'),
            import('../../../src/domain/entities/Ship.js'),
            import('../../../src/domain/entities/Asteroid.js'),
            import('../../../src/application/GameState.js'),
            import('../../../src/infrastructure/Storage.js'),
            import('../../../src/domain/value-objects/Vector2D.js')
        ]);

        Game = modules[0].Game;
        Ship = modules[1].Ship;
        Asteroid = modules[2].Asteroid;
        GameState = modules[3].GameState;
        Storage = modules[4].Storage;
        Vector2D = modules[5].Vector2D;

        // Mock Renderer
        mockRenderer = {
            render: jest.fn(),
            getCanvas: jest.fn(() => ({ width: 800, height: 600 }))
        };

        // Mock InputHandler
        mockInputHandler = {
            getInput: jest.fn(() => ({})),
            isPressed: jest.fn(() => false)
        };

        // Mock Storage
        mockStorage = {
            getHighScore: jest.fn(() => 0),
            saveHighScore: jest.fn()
        };

        // Mock AudioController
        mockAudio = {
            playShoot: jest.fn(),
            playExplosion: jest.fn(),
            playThrust: jest.fn()
        };
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Layer Integration', () => {
        test('should create Game with all dependencies injected', () => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);

            expect(game.renderer).toBe(mockRenderer);
            expect(game.inputHandler).toBe(mockInputHandler);
            expect(game.storage).toBe(mockStorage);
            expect(game.audio).toBe(mockAudio);
        });

        test('should initialize GameState through Game', () => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();

            const state = game.getState();
            expect(state).toBeDefined();
            expect(state.isMenu()).toBe(true);
        });

        test('should create Ship entity at screen center on initialize', () => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();

            const ship = game.getShip();
            expect(ship).toBeInstanceOf(Ship);
            expect(ship.position.x).toBe(400); // center of 800
            expect(ship.position.y).toBe(300); // center of 600
        });

        test('should spawn Asteroid entities on game start', () => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();
            game.start();

            const asteroids = game.getAsteroids();
            expect(asteroids.length).toBeGreaterThan(0);
            expect(asteroids[0]).toBeInstanceOf(Asteroid);
        });

        test('should use Storage to load high score on initialize', () => {
            mockStorage.getHighScore.mockReturnValue(5000);

            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();

            expect(mockStorage.getHighScore).toHaveBeenCalledTimes(1);
        });
    });

    describe('Input → Game State Flow', () => {
        beforeEach(() => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();
            game.start();
        });

        test('should process thrust input and update ship velocity', () => {
            const initialShip = game.getShip();
            const initialVelocity = initialShip.velocity.magnitude();

            mockInputHandler.getInput.mockReturnValue({ thrust: true });
            game.handleInput(mockInputHandler.getInput());

            const updatedShip = game.getShip();
            expect(updatedShip.velocity.magnitude()).toBeGreaterThan(initialVelocity);
        });

        test('should process rotate input and change ship rotation', () => {
            const initialRotation = game.getShip().rotation;

            mockInputHandler.getInput.mockReturnValue({ rotate: -1 });
            game.handleInput(mockInputHandler.getInput());

            const updatedShip = game.getShip();
            expect(updatedShip.rotation).not.toBe(initialRotation);
        });

        test('should process fire input and create bullet', () => {
            mockInputHandler.getInput.mockReturnValue({ fire: true });

            game.handleInput(mockInputHandler.getInput());

            const bullets = game.getBullets();
            expect(bullets.length).toBe(1);
        });

        test('should process pause input and change game state', () => {
            expect(game.getState().isPaused()).toBe(false);

            mockInputHandler.getInput.mockReturnValue({ pause: true });
            game.handleInput(mockInputHandler.getInput());

            expect(game.getState().isPaused()).toBe(true);
        });
    });

    describe('Collision → Score Flow', () => {
        beforeEach(() => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();
            game.start();
        });

        test('should add score when bullet hits asteroid', () => {
            const initialScore = game.getScore();

            // Симуляция: пуля попадает в астероид
            // В реальной игре это происходит в checkCollisions()
            const asteroids = game.getAsteroids();
            if (asteroids.length > 0) {
                const asteroid = asteroids[0];
                const points = asteroid.getPoints();

                // Эмулируем попадание через прямой вызов (для интеграционного теста)
                // В реальности это происходит автоматически в update()
                game.addScore(points);

                expect(game.getScore()).toBeGreaterThan(initialScore);
            }
        });

        test('should play explosion sound on collision', () => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();
            game.start();

            // Эмулируем попадание
            game.addScore(20);

            expect(mockAudio.playExplosion).toHaveBeenCalled();
        });
    });

    describe('GameState Transitions', () => {
        beforeEach(() => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
        });

        test('should transition: menu → playing → paused → playing', () => {
            game.initialize();
            expect(game.getState().isMenu()).toBe(true);

            game.start();
            expect(game.getState().isPlaying()).toBe(true);

            // Pause
            mockInputHandler.getInput.mockReturnValue({ pause: true });
            game.handleInput(mockInputHandler.getInput());
            expect(game.getState().isPaused()).toBe(true);

            // Resume
            mockInputHandler.getInput.mockReturnValue({ pause: true });
            game.handleInput(mockInputHandler.getInput());
            expect(game.getState().isPlaying()).toBe(true);
        });

        test('should transition to game over when lives depleted', () => {
            game.initialize();
            game.start();

            // Симулируем 3 попадания (жизни)
            const state = game.getState();
            state.lives = 0;
            state.gameOver();

            expect(state.isGameOver()).toBe(true);
        });

        test('should save high score on game over', () => {
            mockStorage.getHighScore.mockReturnValue(0);

            game.initialize();
            game.start();

            // Набираем очки
            game.addScore(1000);

            // Game over
            const state = game.getState();
            state.lives = 0;
            state.gameOver();

            expect(mockStorage.saveHighScore).toHaveBeenCalledWith(1000);
        });
    });

    describe('Level Progression', () => {
        beforeEach(() => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();
            game.start();
        });

        test('should increase level when all asteroids destroyed', () => {
            const initialLevel = game.getLevel();

            // Удаляем все астероиды (симуляция уничтожения)
            game.getAsteroids().length = 0;

            // Обновляем игру — должен сработать nextLevel()
            game.update(1 / 60);

            expect(game.getLevel()).toBeGreaterThan(initialLevel);
        });

        test('should spawn new asteroids on level up', () => {
            // Удаляем все астероиды
            game.getAsteroids().length = 0;

            // Обновляем игру
            game.update(1 / 60);

            const asteroids = game.getAsteroids();
            expect(asteroids.length).toBeGreaterThan(0);
        });
    });

    describe('Object Pool Integration', () => {
        beforeEach(() => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();
            game.start();
        });

        test('should reuse bullets from pool', () => {
            // Стреляем 5 раз
            for (let i = 0; i < 5; i++) {
                mockInputHandler.getInput.mockReturnValue({ fire: true });
                game.handleInput(mockInputHandler.getInput());

                // Сбрасываем флаг огня
                mockInputHandler.getInput.mockReturnValue({ fire: false });
                game.handleInput(mockInputHandler.getInput());
            }

            const bullets = game.getBullets();
            expect(bullets.length).toBe(5);
        });

        test('should not exceed max bullets', () => {
            // Стреляем больше максимума (50)
            for (let i = 0; i < 60; i++) {
                mockInputHandler.getInput.mockReturnValue({ fire: true });
                game.handleInput(mockInputHandler.getInput());
                mockInputHandler.getInput.mockReturnValue({ fire: false });
                game.handleInput(mockInputHandler.getInput());
            }

            const bullets = game.getBullets();
            expect(bullets.length).toBeLessThanOrEqual(50);
        });
    });

    describe('Screen Wrapping Integration', () => {
        beforeEach(() => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();
            game.start();
        });

        test('should wrap ship position when leaving screen', () => {
            const ship = game.getShip();

            // Устанавливаем позицию за пределами экрана
            ship.position.x = -10;
            ship.position.y = -10;

            // Обновляем игру
            game.update(1 / 60);

            // Позиция должна "завернуться"
            expect(ship.position.x).toBeGreaterThan(700); // 800 - 10
            expect(ship.position.y).toBeGreaterThan(500); // 600 - 10
        });

        test('should wrap asteroid positions', () => {
            const asteroids = game.getAsteroids();

            if (asteroids.length > 0) {
                const asteroid = asteroids[0];
                asteroid.position.x = 850; // За правым краем

                game.update(1 / 60);

                expect(asteroid.position.x).toBeLessThan(100); // Должен появиться слева
            }
        });
    });
});
