import { jest } from '@jest/globals';
import { GameState } from '../../application/GameState.js';

describe('GameState', () => {
    let gameState;

    beforeEach(() => {
        gameState = new GameState();
    });

    describe('Initial State', () => {
        test('should start in menu state', () => {
            expect(gameState.isMenu()).toBe(true);
        });

        test('should not be playing initially', () => {
            expect(gameState.isPlaying()).toBe(false);
        });

        test('should not be paused initially', () => {
            expect(gameState.isPaused()).toBe(false);
        });

        test('should not be game over initially', () => {
            expect(gameState.isGameOver()).toBe(false);
        });

        test('should start at level 1', () => {
            expect(gameState.level).toBe(1);
        });

        test('should start with 3 lives', () => {
            expect(gameState.lives).toBe(3);
        });

        test('should start with zero score', () => {
            expect(gameState.score).toBe(0);
        });

        test('should start with zero high score', () => {
            expect(gameState.highScore).toBe(0);
        });
    });

    describe('State Transitions', () => {
        test('should transition to playing on start', () => {
            gameState.start();
            expect(gameState.isPlaying()).toBe(true);
            expect(gameState.isMenu()).toBe(false);
        });

        test('should reset level to 1 on start', () => {
            gameState.level = 5;
            gameState.start();
            expect(gameState.level).toBe(1);
        });

        test('should reset lives to 3 on start', () => {
            gameState.lives = 1;
            gameState.start();
            expect(gameState.lives).toBe(3);
        });

        test('should reset score to 0 on start', () => {
            gameState.score = 500;
            gameState.start();
            expect(gameState.score).toBe(0);
        });

        test('should preserve high score on start', () => {
            gameState.highScore = 1000;
            gameState.start();
            expect(gameState.highScore).toBe(1000);
        });
    });

    describe('Pause/Resume', () => {
        test('should pause when playing', () => {
            gameState.start();
            gameState.pause();
            expect(gameState.isPaused()).toBe(true);
            expect(gameState.isPlaying()).toBe(false);
        });

        test('should not pause when in menu', () => {
            gameState.pause();
            expect(gameState.isMenu()).toBe(true);
            expect(gameState.isPaused()).toBe(false);
        });

        test('should not pause when already paused', () => {
            gameState.start();
            gameState.pause();
            gameState.pause();
            expect(gameState.isPaused()).toBe(true);
        });

        test('should not pause when game over', () => {
            gameState.start();
            gameState.lives = 0;
            gameState.hit();
            gameState.pause();
            expect(gameState.isPaused()).toBe(false);
            expect(gameState.isGameOver()).toBe(true);
        });

        test('should resume when paused', () => {
            gameState.start();
            gameState.pause();
            gameState.resume();
            expect(gameState.isPlaying()).toBe(true);
            expect(gameState.isPaused()).toBe(false);
        });

        test('should not resume when playing', () => {
            gameState.start();
            gameState.resume();
            expect(gameState.isPlaying()).toBe(true);
        });

        test('should not resume when in menu', () => {
            gameState.resume();
            expect(gameState.isMenu()).toBe(true);
        });
    });

    describe('Hit/Lives', () => {
        test('should decrement lives on hit', () => {
            gameState.start();
            gameState.hit();
            expect(gameState.lives).toBe(2);
        });

        test('should trigger game over when lives reach 0', () => {
            gameState.start();
            gameState.lives = 1;
            gameState.hit();
            expect(gameState.isGameOver()).toBe(true);
        });

        test('should not go below zero lives', () => {
            gameState.start();
            gameState.hit();
            gameState.hit();
            gameState.hit();
            gameState.hit();
            expect(gameState.lives).toBe(0);
        });

        test('should not trigger game over if lives still remaining', () => {
            gameState.start();
            gameState.hit();
            expect(gameState.isGameOver()).toBe(false);
            expect(gameState.lives).toBe(2);
        });

        test('should not allow hit in menu state', () => {
            gameState.hit();
            expect(gameState.lives).toBe(3); // unchanged
            expect(gameState.isMenu()).toBe(true);
        });
    });

    describe('Level Progression', () => {
        test('should increment level on level complete', () => {
            gameState.start();
            expect(gameState.level).toBe(1);
            gameState.nextLevel();
            expect(gameState.level).toBe(2);
        });

        test('should allow multiple level increments', () => {
            gameState.start();
            gameState.nextLevel();
            gameState.nextLevel();
            gameState.nextLevel();
            expect(gameState.level).toBe(4);
        });

        test('should not increment level in menu', () => {
            gameState.nextLevel();
            expect(gameState.level).toBe(1); // unchanged
        });
    });

    describe('Score Management', () => {
        test('should add score', () => {
            gameState.start();
            gameState.addScore(100);
            expect(gameState.score).toBe(100);
        });

        test('should add multiple scores', () => {
            gameState.start();
            gameState.addScore(100);
            gameState.addScore(50);
            gameState.addScore(25);
            expect(gameState.score).toBe(175);
        });

        test('should update high score when current exceeds it', () => {
            gameState.start();
            gameState.addScore(1500);
            expect(gameState.highScore).toBe(1500);
            expect(gameState.score).toBe(1500);
        });

        test('should not update high score when current does not exceed it', () => {
            gameState.start();
            gameState.highScore = 1000;
            gameState.addScore(500);
            expect(gameState.highScore).toBe(1000);
            expect(gameState.score).toBe(500);
        });

        test('should update high score multiple times as score increases', () => {
            gameState.start();
            gameState.addScore(500);
            expect(gameState.highScore).toBe(500);
            gameState.addScore(600);
            expect(gameState.highScore).toBe(1100);
            gameState.addScore(100);
            expect(gameState.highScore).toBe(1200);
        });

        test('should not add score in menu state', () => {
            gameState.addScore(100);
            expect(gameState.score).toBe(0);
        });
    });

    describe('Game Over', () => {
        test('should transition to game over on zero lives', () => {
            gameState.start();
            gameState.lives = 0;
            gameState.hit();
            expect(gameState.isGameOver()).toBe(true);
        });

        test('should not allow start from game over without reset', () => {
            gameState.start();
            gameState.lives = 0;
            gameState.hit();
            // Game over state should persist until new start()
            expect(gameState.isGameOver()).toBe(true);
        });

        test('should allow new game after game over', () => {
            gameState.start();
            gameState.lives = 0;
            gameState.hit();
            gameState.start(); // Start new game
            expect(gameState.isPlaying()).toBe(true);
            expect(gameState.lives).toBe(3);
        });
    });
});
