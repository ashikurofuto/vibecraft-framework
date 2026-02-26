import { jest } from '@jest/globals';
import { ScoreManager } from '../../application/ScoreManager.js';

describe('ScoreManager', () => {
    let scoreManager;
    let mockStorage;

    beforeEach(() => {
        // Mock Storage interface
        mockStorage = {
            saveHighScore: jest.fn(),
            getHighScore: jest.fn(() => 0)
        };
        scoreManager = new ScoreManager(mockStorage);
    });

    describe('Initial State', () => {
        test('should start with zero current score', () => {
            expect(scoreManager.getCurrentScore()).toBe(0);
        });

        test('should load high score from storage on initialization', () => {
            expect(mockStorage.getHighScore).toHaveBeenCalledTimes(1);
        });

        test('should return loaded high score', () => {
            expect(scoreManager.getHighScore()).toBe(0);
        });

        test('should use high score from storage if exists', () => {
            mockStorage.getHighScore = jest.fn(() => 5000);
            scoreManager = new ScoreManager(mockStorage);
            expect(scoreManager.getHighScore()).toBe(5000);
        });
    });

    describe('Adding Score', () => {
        test('should add score to current score', () => {
            scoreManager.addScore(100);
            expect(scoreManager.getCurrentScore()).toBe(100);
        });

        test('should add multiple scores cumulatively', () => {
            scoreManager.addScore(100);
            scoreManager.addScore(50);
            scoreManager.addScore(25);
            expect(scoreManager.getCurrentScore()).toBe(175);
        });

        test('should add score for asteroid destruction (large)', () => {
            scoreManager.addScore(20);
            expect(scoreManager.getCurrentScore()).toBe(20);
        });

        test('should add score for asteroid destruction (medium)', () => {
            scoreManager.addScore(50);
            expect(scoreManager.getCurrentScore()).toBe(50);
        });

        test('should add score for asteroid destruction (small)', () => {
            scoreManager.addScore(100);
            expect(scoreManager.getCurrentScore()).toBe(100);
        });

        test('should add score for UFO destruction (large)', () => {
            scoreManager.addScore(200);
            expect(scoreManager.getCurrentScore()).toBe(200);
        });

        test('should add score for UFO destruction (small)', () => {
            scoreManager.addScore(1000);
            expect(scoreManager.getCurrentScore()).toBe(1000);
        });

        test('should handle zero score addition', () => {
            scoreManager.addScore(0);
            expect(scoreManager.getCurrentScore()).toBe(0);
        });

        test('should handle negative score addition', () => {
            scoreManager.addScore(-50);
            expect(scoreManager.getCurrentScore()).toBe(-50);
        });
    });

    describe('High Score Tracking', () => {
        test('should update high score when current exceeds it', () => {
            scoreManager.addScore(1500);
            expect(scoreManager.getHighScore()).toBe(1500);
        });

        test('should call storage.saveHighScore when high score is beaten', () => {
            scoreManager.addScore(1500);
            expect(mockStorage.saveHighScore).toHaveBeenCalledWith(1500);
        });

        test('should not update high score when current does not exceed it', () => {
            mockStorage.getHighScore = jest.fn(() => 2000);
            scoreManager = new ScoreManager(mockStorage);
            scoreManager.addScore(500);
            expect(scoreManager.getHighScore()).toBe(2000);
        });

        test('should not call saveHighScore when high score is not beaten', () => {
            mockStorage.getHighScore = jest.fn(() => 2000);
            scoreManager = new ScoreManager(mockStorage);
            scoreManager.addScore(500);
            expect(mockStorage.saveHighScore).not.toHaveBeenCalled();
        });

        test('should update high score multiple times as score increases', () => {
            scoreManager.addScore(500);
            expect(scoreManager.getHighScore()).toBe(500);
            
            scoreManager.addScore(600);
            expect(scoreManager.getHighScore()).toBe(1100);
            expect(mockStorage.saveHighScore).toHaveBeenCalledTimes(2);
        });

        test('should match current score to high score when beaten', () => {
            scoreManager.addScore(1500);
            expect(scoreManager.getCurrentScore()).toBe(1500);
            expect(scoreManager.getHighScore()).toBe(1500);
        });
    });

    describe('Reset', () => {
        test('should reset current score to zero', () => {
            scoreManager.addScore(500);
            scoreManager.reset();
            expect(scoreManager.getCurrentScore()).toBe(0);
        });

        test('should preserve high score on reset', () => {
            mockStorage.getHighScore = jest.fn(() => 2000);
            scoreManager = new ScoreManager(mockStorage);
            scoreManager.addScore(500);
            scoreManager.reset();
            expect(scoreManager.getHighScore()).toBe(2000);
        });

        test('should not call saveHighScore on reset', () => {
            scoreManager.addScore(500);
            mockStorage.saveHighScore.mockClear();
            scoreManager.reset();
            expect(mockStorage.saveHighScore).not.toHaveBeenCalled();
        });

        test('should allow adding score after reset', () => {
            scoreManager.addScore(500);
            scoreManager.reset();
            scoreManager.addScore(100);
            expect(scoreManager.getCurrentScore()).toBe(100);
        });
    });

    describe('New Game', () => {
        test('should reset score for new game', () => {
            scoreManager.addScore(1000);
            scoreManager.newGame();
            expect(scoreManager.getCurrentScore()).toBe(0);
        });

        test('should preserve high score for new game', () => {
            mockStorage.getHighScore = jest.fn(() => 5000);
            scoreManager = new ScoreManager(mockStorage);
            scoreManager.addScore(1000);
            scoreManager.newGame();
            expect(scoreManager.getHighScore()).toBe(5000);
        });

        test('should save high score if beaten before new game', () => {
            scoreManager.addScore(2000);
            scoreManager.newGame();
            expect(mockStorage.saveHighScore).toHaveBeenCalledWith(2000);
        });
    });

    describe('Edge Cases', () => {
        test('should handle very large scores', () => {
            scoreManager.addScore(999999);
            expect(scoreManager.getCurrentScore()).toBe(999999);
        });

        test('should handle storage returning null', () => {
            mockStorage.getHighScore = jest.fn(() => null);
            scoreManager = new ScoreManager(mockStorage);
            expect(scoreManager.getHighScore()).toBe(0);
        });

        test('should handle storage returning undefined', () => {
            mockStorage.getHighScore = jest.fn(() => undefined);
            scoreManager = new ScoreManager(mockStorage);
            expect(scoreManager.getHighScore()).toBe(0);
        });

        test('should handle storage throwing error', () => {
            mockStorage.getHighScore = jest.fn(() => {
                throw new Error('Storage error');
            });
            // Should not crash the entire manager
            expect(() => new ScoreManager(mockStorage)).not.toThrow();
        });
    });
});
