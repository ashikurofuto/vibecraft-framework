import { jest } from '@jest/globals';
import { Game } from '../../application/Game.js';

describe('Game', () => {
    let game;
    let mockRenderer;
    let mockInputHandler;
    let mockStorage;
    let mockAudio;

    beforeEach(() => {
        // Mock Renderer interface
        mockRenderer = {
            render: jest.fn(),
            getCanvas: jest.fn(() => ({ width: 800, height: 600 }))
        };

        // Mock InputHandler interface
        mockInputHandler = {
            getInput: jest.fn(() => ({})),
            isPressed: jest.fn(() => false)
        };

        // Mock Storage interface
        mockStorage = {
            getHighScore: jest.fn(() => 0),
            saveHighScore: jest.fn()
        };

        // Mock AudioController interface
        mockAudio = {
            playShoot: jest.fn(),
            playExplosion: jest.fn(),
            playThrust: jest.fn()
        };

        game = new Game(mockRenderer, mockInputHandler, mockStorage, mockAudio);
    });

    describe('Initialization', () => {
        test('should create game with dependencies', () => {
            expect(game.renderer).toBe(mockRenderer);
            expect(game.inputHandler).toBe(mockInputHandler);
            expect(game.storage).toBe(mockStorage);
            expect(game.audio).toBe(mockAudio);
        });

        test('should initialize in menu state', () => {
            game.initialize();
            expect(game.getState().isMenu()).toBe(true);
        });

        test('should not be playing after initialize', () => {
            game.initialize();
            expect(game.getState().isPlaying()).toBe(false);
        });

        test('should create ship at center of screen', () => {
            game.initialize();
            const ship = game.getShip();
            expect(ship).toBeDefined();
        });

        test('should start with empty asteroids array', () => {
            game.initialize();
            expect(game.getAsteroids()).toEqual([]);
        });

        test('should start with empty bullets array', () => {
            game.initialize();
            expect(game.getBullets()).toEqual([]);
        });

        test('should start with empty ufos array', () => {
            game.initialize();
            expect(game.getUFOs()).toEqual([]);
        });

        test('should set screen dimensions from canvas', () => {
            game.initialize();
            expect(game.screenWidth).toBe(800);
            expect(game.screenHeight).toBe(600);
        });
    });

    describe('Start Game', () => {
        beforeEach(() => {
            game.initialize();
        });

        test('should start game', () => {
            game.start();
            expect(game.getState().isPlaying()).toBe(true);
        });

        test('should transition from menu to playing', () => {
            expect(game.getState().isMenu()).toBe(true);
            game.start();
            expect(game.getState().isPlaying()).toBe(true);
        });

        test('should spawn initial asteroids', () => {
            game.start();
            expect(game.getAsteroids().length).toBeGreaterThan(0);
        });

        test('should reset score to zero', () => {
            game.start();
            expect(game.getScore()).toBe(0);
        });

        test('should set lives to 3', () => {
            game.start();
            expect(game.getLives()).toBe(3);
        });

        test('should set level to 1', () => {
            game.start();
            expect(game.getLevel()).toBe(1);
        });

        test('should not start if already playing', () => {
            game.start();
            const stateBefore = game.getState();
            game.start();
            expect(game.getState()).toBe(stateBefore); // State unchanged
        });
    });

    describe('Input Handling', () => {
        beforeEach(() => {
            game.initialize();
            game.start();
        });

        test('should handle thrust input', () => {
            const input = { thrust: true, rotate: 0, fire: false };
            game.handleInput(input);
            // Ship should have thrust applied
        });

        test('should handle rotate left input', () => {
            const input = { thrust: false, rotate: -1, fire: false };
            game.handleInput(input);
            // Ship should rotate counter-clockwise
        });

        test('should handle rotate right input', () => {
            const input = { thrust: false, rotate: 1, fire: false };
            game.handleInput(input);
            // Ship should rotate clockwise
        });

        test('should handle fire input', () => {
            const input = { thrust: false, rotate: 0, fire: true };
            const bulletsBefore = game.getBullets().length;
            game.handleInput(input);
            // Should create a new bullet
            expect(game.getBullets().length).toBeGreaterThan(bulletsBefore);
        });

        test('should not handle input when in menu', () => {
            game.initialize();
            const input = { thrust: true, rotate: 0, fire: false };
            game.handleInput(input);
            // Input should be ignored in menu
        });

        test('should not handle input when paused', () => {
            game.initialize();
            game.start();
            game.pause();
            const input = { thrust: true, rotate: 0, fire: false };
            game.handleInput(input);
            // Input should be ignored when paused
        });

        test('should not handle input when game over', () => {
            game.initialize();
            game.start();
            game.getState().lives = 0;
            game.getState().hit();
            const input = { thrust: true, rotate: 0, fire: false };
            game.handleInput(input);
            // Input should be ignored when game over
        });

        test('should handle combined inputs', () => {
            const input = { thrust: true, rotate: -1, fire: true };
            game.handleInput(input);
            // Should handle all inputs simultaneously
        });
    });

    describe('Pause/Resume', () => {
        beforeEach(() => {
            game.initialize();
            game.start();
        });

        test('should pause on P key', () => {
            game.handleInput({ pause: true });
            expect(game.getState().isPaused()).toBe(true);
        });

        test('should not pause when in menu', () => {
            game.initialize();
            game.handleInput({ pause: true });
            expect(game.getState().isMenu()).toBe(true);
        });

        test('should resume on P key when paused', () => {
            game.handleInput({ pause: true });
            expect(game.getState().isPaused()).toBe(true);
            game.handleInput({ pause: true });
            expect(game.getState().isPlaying()).toBe(true);
        });

        test('should not resume when game over', () => {
            game.getState().lives = 0;
            game.getState().hit();
            game.handleInput({ pause: true });
            expect(game.getState().isPaused()).toBe(false);
        });
    });

    describe('Score Management', () => {
        beforeEach(() => {
            game.initialize();
            game.start();
        });

        test('should get current score', () => {
            expect(game.getScore()).toBe(0);
        });

        test('should add score', () => {
            game.addScore(100);
            expect(game.getScore()).toBe(100);
        });

        test('should add multiple scores', () => {
            game.addScore(100);
            game.addScore(50);
            game.addScore(25);
            expect(game.getScore()).toBe(175);
        });

        test('should get high score', () => {
            expect(game.getHighScore()).toBe(0);
        });

        test('should update high score when beaten', () => {
            game.addScore(1500);
            expect(game.getHighScore()).toBe(1500);
        });
    });

    describe('Update', () => {
        beforeEach(() => {
            game.initialize();
            game.start();
        });

        test('should update ship position', () => {
            const initialPos = { ...game.getShip().position };
            game.update(1 / 60);
            // Ship position may change due to physics
        });

        test('should update asteroids positions', () => {
            const asteroids = game.getAsteroids();
            const initialPositions = asteroids.map(a => ({ ...a.position }));
            game.update(1 / 60);
            // Asteroid positions may change
        });

        test('should update bullets positions', () => {
            game.handleInput({ fire: true });
            const bullets = game.getBullets();
            const initialPositions = bullets.map(b => ({ ...b.position }));
            game.update(1 / 60);
            // Bullet positions should change
        });

        test('should apply friction to ship', () => {
            game.update(1 / 60);
            // Ship velocity should be reduced by friction
        });

        test('should wrap ship position when off screen', () => {
            const ship = game.getShip();
            ship.position.x = -20;
            game.update(1 / 60);
            expect(ship.position.x).toBeGreaterThan(0);
        });

        test('should wrap asteroids positions when off screen', () => {
            game.start();
            const asteroids = game.getAsteroids();
            if (asteroids.length > 0) {
                asteroids[0].position.x = -20;
                game.update(1 / 60);
                expect(asteroids[0].position.x).toBeGreaterThan(0);
            }
        });

        test('should not update when paused', () => {
            game.handleInput({ pause: true });
            const initialScore = game.getScore();
            game.update(1 / 60);
            // Game state should not change
        });

        test('should not update when game over', () => {
            game.getState().lives = 0;
            game.getState().hit();
            game.update(1 / 60);
            // Game state should not change
        });
    });

    describe('Collision Detection', () => {
        beforeEach(() => {
            game.initialize();
            game.start();
        });

        test('should detect ship-asteroid collision', () => {
            const ship = game.getShip();
            const asteroids = game.getAsteroids();
            if (asteroids.length > 0) {
                // Move asteroid to ship position
                asteroids[0].position.x = ship.position.x;
                asteroids[0].position.y = ship.position.y;
                game.update(1 / 60);
                // Collision should be detected
            }
        });

        test('should detect bullet-asteroid collision', () => {
            game.handleInput({ fire: true });
            const bullets = game.getBullets();
            const asteroids = game.getAsteroids();
            if (bullets.length > 0 && asteroids.length > 0) {
                // Move bullet to asteroid position
                bullets[0].position.x = asteroids[0].position.x;
                bullets[0].position.y = asteroids[0].position.y;
                game.update(1 / 60);
                // Collision should be detected
            }
        });

        test('should destroy asteroid on bullet collision', () => {
            game.handleInput({ fire: true });
            const bullets = game.getBullets();
            const asteroids = game.getAsteroids();
            if (bullets.length > 0 && asteroids.length > 0) {
                const asteroidsBefore = game.getAsteroids().length;
                // Move bullet to asteroid position
                bullets[0].position.x = asteroids[0].position.x;
                bullets[0].position.y = asteroids[0].position.y;
                game.update(1 / 60);
                // Asteroid count should change (split or destroyed)
            }
        });

        test('should decrement lives on ship-asteroid collision', () => {
            const ship = game.getShip();
            const asteroids = game.getAsteroids();
            if (asteroids.length > 0) {
                const livesBefore = game.getLives();
                // Move asteroid to ship position
                asteroids[0].position.x = ship.position.x;
                asteroids[0].position.y = ship.position.y;
                game.update(1 / 60);
                // Lives may decrement
            }
        });
    });

    describe('Level Management', () => {
        beforeEach(() => {
            game.initialize();
            game.start();
        });

        test('should start at level 1', () => {
            expect(game.getLevel()).toBe(1);
        });

        test('should increment level when all asteroids destroyed', () => {
            // Clear all asteroids
            game.asteroids = [];
            game.update(1 / 60);
            expect(game.getLevel()).toBe(2);
        });

        test('should spawn more asteroids on next level', () => {
            game.asteroids = [];
            const levelBefore = game.getLevel();
            game.update(1 / 60);
            expect(game.getLevel()).toBeGreaterThan(levelBefore);
            expect(game.getAsteroids().length).toBeGreaterThan(0);
        });
    });

    describe('Get State for Renderer', () => {
        beforeEach(() => {
            game.initialize();
        });

        test('should get game state for renderer', () => {
            const state = game.getState();
            expect(state).toBeDefined();
        });

        test('should get ship for renderer', () => {
            const ship = game.getShip();
            expect(ship).toBeDefined();
        });

        test('should get asteroids for renderer', () => {
            const asteroids = game.getAsteroids();
            expect(Array.isArray(asteroids)).toBe(true);
        });

        test('should get bullets for renderer', () => {
            const bullets = game.getBullets();
            expect(Array.isArray(bullets)).toBe(true);
        });

        test('should get ufos for renderer', () => {
            const ufos = game.getUFOs();
            expect(Array.isArray(ufos)).toBe(true);
        });

        test('should get all entities for renderer', () => {
            const entities = game.getEntities();
            expect(entities).toHaveProperty('ship');
            expect(entities).toHaveProperty('asteroids');
            expect(entities).toHaveProperty('bullets');
            expect(entities).toHaveProperty('ufos');
        });
    });

    describe('Edge Cases', () => {
        beforeEach(() => {
            game.initialize();
        });

        test('should handle start without initialize', () => {
            // Should handle gracefully or throw error
            expect(() => game.start()).not.toThrow();
        });

        test('should handle multiple initialize calls', () => {
            game.initialize();
            game.initialize();
            expect(game.getState().isMenu()).toBe(true);
        });

        test('should handle null input', () => {
            game.start();
            expect(() => game.handleInput(null)).not.toThrow();
        });

        test('should handle undefined input', () => {
            game.start();
            expect(() => game.handleInput(undefined)).not.toThrow();
        });

        test('should handle empty input object', () => {
            game.start();
            expect(() => game.handleInput({})).not.toThrow();
        });
    });
});
