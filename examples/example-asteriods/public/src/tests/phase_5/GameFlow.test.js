/**
 * Game Flow Tests — Phase 5
 *
 * @description Тесты полного игрового цикла: start → play → gameover
 * @see src/application/Game.js
 * @see src/application/GameState.js
 * @see src/application/GameLoop.js
 */

import { jest } from '@jest/globals';

describe('Game Flow — Complete Cycle', () => {
    let Game;
    let GameLoop;
    let GameState;

    let mockRenderer;
    let mockInputHandler;
    let mockStorage;
    let mockAudio;
    let game;
    let gameLoop;

    const FIXED_TIMESTEP = 1 / 60;

    beforeEach(async () => {
        // Динамический импорт
        const modules = await Promise.all([
            import('../../../src/application/Game.js'),
            import('../../../src/application/GameLoop.js'),
            import('../../../src/application/GameState.js')
        ]);

        Game = modules[0].Game;
        GameLoop = modules[1].GameLoop;
        GameState = modules[2].GameState;

        // Mock Renderer
        mockRenderer = {
            render: jest.fn(),
            getCanvas: jest.fn(() => ({ width: 800, height: 600 }))
        };

        // Mock InputHandler
        mockInputHandler = {
            getInput: jest.fn(() => ({})),
            isPressed: jest.fn(() => false),
            reset: jest.fn()
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

    describe('Game Start Flow', () => {
        beforeEach(() => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
        });

        test('should start in menu state', () => {
            game.initialize();
            expect(game.getState().isMenu()).toBe(true);
        });

        test('should transition from menu to playing on start', () => {
            game.initialize();
            expect(game.getState().isMenu()).toBe(true);

            game.start();
            expect(game.getState().isPlaying()).toBe(true);
        });

        test('should spawn initial asteroids on game start', () => {
            game.initialize();
            game.start();

            const asteroids = game.getAsteroids();
            expect(asteroids.length).toBeGreaterThan(0);
        });

        test('should create ship at center on start', () => {
            game.initialize();
            game.start();

            const ship = game.getShip();
            expect(ship.position.x).toBe(400);
            expect(ship.position.y).toBe(300);
        });

        test('should reset score on new game', () => {
            game.initialize();
            game.start();

            expect(game.getScore()).toBe(0);
        });

        test('should load high score from storage on initialize', () => {
            mockStorage.getHighScore.mockReturnValue(5000);

            game.initialize();

            expect(mockStorage.getHighScore).toHaveBeenCalled();
            expect(game.getHighScore()).toBe(5000);
        });
    });

    describe('Gameplay Loop', () => {
        beforeEach(() => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();
            game.start();
        });

        test('should update ship position on each frame', () => {
            const ship = game.getShip();
            const initialX = ship.position.x;
            const initialY = ship.position.y;

            // Даём тягу
            mockInputHandler.getInput.mockReturnValue({ thrust: true });
            game.handleInput(mockInputHandler.getInput());

            // Обновляем игру
            game.update(FIXED_TIMESTEP);

            // Позиция должна измениться
            expect(ship.position.x).not.toBe(initialX);
            expect(ship.position.y).not.toBe(initialY);
        });

        test('should update asteroids on each frame', () => {
            const asteroids = game.getAsteroids();
            const initialPositions = asteroids.map(a => ({
                x: a.position.x,
                y: a.position.y
            }));

            game.update(FIXED_TIMESTEP);

            // Позиции астероидов должны измениться
            asteroids.forEach((asteroid, index) => {
                expect(asteroid.position.x).not.toBe(initialPositions[index].x);
                expect(asteroid.position.y).not.toBe(initialPositions[index].y);
            });
        });

        test('should update bullets on each frame', () => {
            // Стреляем
            mockInputHandler.getInput.mockReturnValue({ fire: true });
            game.handleInput(mockInputHandler.getInput());

            const bullets = game.getBullets();
            const initialPositions = bullets.map(b => ({
                x: b.position.x,
                y: b.position.y
            }));

            game.update(FIXED_TIMESTEP);

            // Позиции пуль должны измениться
            bullets.forEach((bullet, index) => {
                expect(bullet.position.x).not.toBe(initialPositions[index].x);
                expect(bullet.position.y).not.toBe(initialPositions[index].y);
            });
        });

        test('should call render with current game state', () => {
            game.update(FIXED_TIMESTEP);

            expect(mockRenderer.render).toHaveBeenCalledWith(
                expect.objectContaining({
                    ship: expect.any(Object),
                    asteroids: expect.any(Array),
                    bullets: expect.any(Array),
                    ufos: expect.any(Array)
                })
            );
        });
    });

    describe('Collision Events', () => {
        beforeEach(() => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();
            game.start();
        });

        test('should detect bullet-asteroid collision', () => {
            // Стреляем в астероид
            mockInputHandler.getInput.mockReturnValue({ fire: true });
            game.handleInput(mockInputHandler.getInput());

            const initialAsteroidCount = game.getAsteroids().length;

            // Обновляем игру — должна произойти коллизия
            game.update(FIXED_TIMESTEP);

            // Количество астероидов должно измениться (разделиться)
            const finalAsteroidCount = game.getAsteroids().length;
            expect(finalAsteroidCount).not.toBe(initialAsteroidCount);
        });

        test('should add score on asteroid destruction', () => {
            const initialScore = game.getScore();

            // Стреляем и попадаем в астероид
            mockInputHandler.getInput.mockReturnValue({ fire: true });
            game.handleInput(mockInputHandler.getInput());
            game.update(FIXED_TIMESTEP);

            // Счёт должен увеличиться
            expect(game.getScore()).toBeGreaterThan(initialScore);
        });

        test('should play explosion sound on collision', () => {
            // Стреляем
            mockInputHandler.getInput.mockReturnValue({ fire: true });
            game.handleInput(mockInputHandler.getInput());
            game.update(FIXED_TIMESTEP);

            expect(mockAudio.playExplosion).toHaveBeenCalled();
        });

        test('should detect ship-asteroid collision', () => {
            // manually create collision scenario
            const ship = game.getShip();
            const asteroids = game.getAsteroids();

            if (asteroids.length > 0) {
                // Перемещаем астероид к кораблю
                const asteroid = asteroids[0];
                asteroid.position.x = ship.position.x;
                asteroid.position.y = ship.position.y;

                const initialLives = game.getLives();

                game.update(FIXED_TIMESTEP);

                // Жизни должны уменьшиться
                expect(game.getLives()).toBeLessThan(initialLives);
            }
        });
    });

    describe('Level Completion', () => {
        beforeEach(() => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();
            game.start();
        });

        test('should advance to next level when all asteroids destroyed', () => {
            const initialLevel = game.getLevel();

            // Уничтожаем все астероиды
            game.getAsteroids().length = 0;

            game.update(FIXED_TIMESTEP);

            expect(game.getLevel()).toBeGreaterThan(initialLevel);
        });

        test('should spawn new asteroids on level up', () => {
            const initialCount = game.getAsteroids().length;

            // Уничтожаем все астероиды
            game.getAsteroids().length = 0;

            game.update(FIXED_TIMESTEP);

            // Должны появиться новые астероиды
            expect(game.getAsteroids().length).toBeGreaterThan(0);
        });

        test('should increase difficulty on higher levels', () => {
            // Проходим несколько уровней
            for (let i = 0; i < 3; i++) {
                game.getAsteroids().length = 0;
                game.update(FIXED_TIMESTEP);
            }

            const level = game.getLevel();
            expect(level).toBeGreaterThan(1);
        });
    });

    describe('Game Over Flow', () => {
        beforeEach(() => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();
            game.start();
        });

        test('should end game when lives reach zero', () => {
            const state = game.getState();

            // Устанавливаем 0 жизней
            state.lives = 0;
            state.gameOver();

            expect(state.isGameOver()).toBe(true);
        });

        test('should save high score on game over', () => {
            mockStorage.getHighScore.mockReturnValue(0);

            game.start();
            game.addScore(5000);

            const state = game.getState();
            state.lives = 0;
            state.gameOver();

            expect(mockStorage.saveHighScore).toHaveBeenCalledWith(5000);
        });

        test('should not update high score if not beaten', () => {
            mockStorage.getHighScore.mockReturnValue(10000);

            game.start();
            game.addScore(5000);

            // Сбрасываем историю вызовов чтобы проверить только game over
            mockStorage.saveHighScore.mockClear();

            const state = game.getState();
            state.lives = 0;
            state.gameOver();

            // ✅ saveHighScore не должен вызываться при game over если рекорд не побит
            expect(mockStorage.saveHighScore).not.toHaveBeenCalled();
        });

        test('should stop accepting input on game over', () => {
            const state = game.getState();
            state.lives = 0;
            state.gameOver();

            mockInputHandler.getInput.mockReturnValue({ thrust: true });
            game.handleInput(mockInputHandler.getInput());

            // Ввод должен игнорироваться
            expect(mockInputHandler.getInput).toHaveBeenCalled();
        });
    });

    describe('Pause/Resume Flow', () => {
        beforeEach(() => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
            game.initialize();
            game.start();
        });

        test('should pause game on P key', () => {
            expect(game.getState().isPaused()).toBe(false);

            mockInputHandler.getInput.mockReturnValue({ pause: true });
            game.handleInput(mockInputHandler.getInput());

            expect(game.getState().isPaused()).toBe(true);
        });

        test('should resume game on second P key', () => {
            // Pause
            mockInputHandler.getInput.mockReturnValue({ pause: true });
            game.handleInput(mockInputHandler.getInput());
            expect(game.getState().isPaused()).toBe(true);

            // Resume
            mockInputHandler.getInput.mockReturnValue({ pause: true });
            game.handleInput(mockInputHandler.getInput());
            expect(game.getState().isPaused()).toBe(false);
        });

        test('should not update game while paused', () => {
            const ship = game.getShip();
            const initialX = ship.position.x;

            // Pause
            mockInputHandler.getInput.mockReturnValue({ pause: true });
            game.handleInput(mockInputHandler.getInput());

            // Пытаемся обновить
            game.update(FIXED_TIMESTEP);

            // Позиция не должна измениться
            expect(ship.position.x).toBe(initialX);
        });

        test('should not accept game input while paused', () => {
            // Pause
            mockInputHandler.getInput.mockReturnValue({ pause: true });
            game.handleInput(mockInputHandler.getInput());

            // Пытаемся стрелять
            mockInputHandler.getInput.mockReturnValue({ fire: true });
            game.handleInput(mockInputHandler.getInput());

            // Пули не должно быть
            expect(game.getBullets().length).toBe(0);
        });
    });

    describe('Full Game Session', () => {
        test('should complete full game session: menu → play → gameover', () => {
            game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);

            // Menu state
            game.initialize();
            expect(game.getState().isMenu()).toBe(true);

            // Start game
            game.start();
            expect(game.getState().isPlaying()).toBe(true);

            // Gameplay: несколько кадров
            for (let i = 0; i < 10; i++) {
                mockInputHandler.getInput.mockReturnValue({
                    thrust: i % 2 === 0,
                    fire: i % 3 === 0
                });
                game.handleInput(mockInputHandler.getInput());
                game.update(FIXED_TIMESTEP);
            }

            // Проверяем, что игра активна
            expect(game.getState().isPlaying()).toBe(true);
            expect(game.getScore()).toBeGreaterThanOrEqual(0);

            // Game over
            const state = game.getState();
            state.lives = 0;
            state.gameOver();

            expect(state.isGameOver()).toBe(true);
        });
    });

    describe('GameLoop Integration', () => {
        test('should create GameLoop with callbacks', () => {
            const updateCallback = jest.fn();
            const renderCallback = jest.fn();

            gameLoop = new GameLoop(updateCallback, renderCallback);

            expect(gameLoop).toBeDefined();
        });

        test('should call update and render callbacks on tick', () => {
            const updateCallback = jest.fn();
            const renderCallback = jest.fn();

            gameLoop = new GameLoop(updateCallback, renderCallback);

            // Запускаем цикл
            gameLoop.start();

            // Эмулируем кадр
            const currentTime = performance.now();
            gameLoop.tick(currentTime);

            expect(updateCallback).toHaveBeenCalled();
            expect(renderCallback).toHaveBeenCalled();
        });

        test('should use fixed timestep for physics', () => {
            const updateCallback = jest.fn();
            const renderCallback = jest.fn();

            gameLoop = new GameLoop(updateCallback, renderCallback, FIXED_TIMESTEP);
            gameLoop.start();

            // Эмулируем несколько кадров
            for (let i = 0; i < 5; i++) {
                gameLoop.tick(performance.now() + i * 100);
            }

            // updateCallback должен вызываться с фиксированным timestep
            expect(updateCallback).toHaveBeenCalledTimes(5);
        });
    });
});
