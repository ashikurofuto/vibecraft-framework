/**
 * Тесты для Storage класса
 * Infrastructure Layer - Phase 3
 * 
 * Storage отвечает за абстракцию над localStorage для сохранения рекордов
 */

import { Storage } from '../../infrastructure/Storage.js';
import { 
    createMockLocalStorage,
    createMockLocalStorageUnavailable,
    createMockLocalStorageWithInvalidData
} from '../__mocks__/localStorage.js';

describe('Storage', () => {
    let mockLocalStorage;

    beforeEach(() => {
        mockLocalStorage = createMockLocalStorage();
        // Используем Storage._setStorage для правильной инъекции зависимости в ES modules
        Storage._setStorage(mockLocalStorage);
    });

    afterEach(() => {
        // Сбрасываем storage к localStorage по умолчанию
        Storage._resetStorage();
        mockLocalStorage._reset();
        jest.restoreAllMocks();
    });

    describe('getHighScore', () => {
        test('should return 0 when no high score exists', () => {
            const score = Storage.getHighScore();
            expect(score).toBe(0);
        });

        test('should return high score when it exists', () => {
            const testData = {
                score: 5000,
                date: '2026-02-25T00:00:00.000Z'
            };
            mockLocalStorage._setData({
                'asteroids-highscore': JSON.stringify(testData)
            });

            const score = Storage.getHighScore();
            expect(score).toBe(5000);
        });

        test('should return 0 when stored data is invalid JSON', () => {
            mockLocalStorage._setData({
                'asteroids-highscore': 'invalid-json-data'
            });

            const score = Storage.getHighScore();
            expect(score).toBe(0);
        });

        test('should return 0 when stored data has no score property', () => {
            const testData = {
                date: '2026-02-25T00:00:00.000Z'
            };
            mockLocalStorage._setData({
                'asteroids-highscore': JSON.stringify(testData)
            });

            const score = Storage.getHighScore();
            expect(score).toBe(0);
        });

        test('should return 0 when localStorage throws error', () => {
            global.localStorage = createMockLocalStorageUnavailable();
            
            const score = Storage.getHighScore();
            expect(score).toBe(0);
        });

        test('should handle null value from localStorage', () => {
            mockLocalStorage.getItem.mockReturnValue(null);
            
            const score = Storage.getHighScore();
            expect(score).toBe(0);
        });

        test('should handle empty string value from localStorage', () => {
            mockLocalStorage.getItem.mockReturnValue('');
            
            const score = Storage.getHighScore();
            expect(score).toBe(0);
        });
    });

    describe('saveHighScore', () => {
        test('should save high score to localStorage', () => {
            Storage.saveHighScore(5000);
            
            expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
                'asteroids-highscore',
                expect.any(String)
            );
        });

        test('should save high score as JSON with score property', () => {
            Storage.saveHighScore(5000);
            
            const callArgs = mockLocalStorage.setItem.mock.calls[0];
            const savedData = JSON.parse(callArgs[1]);
            
            expect(savedData.score).toBe(5000);
        });

        test('should save high score with timestamp', () => {
            const beforeSave = Date.now();
            Storage.saveHighScore(5000);
            const afterSave = Date.now();
            
            const callArgs = mockLocalStorage.setItem.mock.calls[0];
            const savedData = JSON.parse(callArgs[1]);
            const savedDate = new Date(savedData.date).getTime();
            
            expect(savedDate).toBeGreaterThanOrEqual(beforeSave);
            expect(savedDate).toBeLessThanOrEqual(afterSave);
        });

        test('should save high score with ISO date format', () => {
            Storage.saveHighScore(5000);
            
            const callArgs = mockLocalStorage.setItem.mock.calls[0];
            const savedData = JSON.parse(callArgs[1]);
            
            expect(savedData.date).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z$/);
        });

        test('should not throw when localStorage is unavailable', () => {
            global.localStorage = createMockLocalStorageUnavailable();
            
            expect(() => Storage.saveHighScore(5000)).not.toThrow();
        });

        test('should call setItem with correct key', () => {
            Storage.saveHighScore(5000);
            
            expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
                'asteroids-highscore',
                expect.any(String)
            );
        });

        test('should overwrite existing high score', () => {
            const oldData = {
                score: 3000,
                date: '2026-02-24T00:00:00.000Z'
            };
            mockLocalStorage._setData({
                'asteroids-highscore': JSON.stringify(oldData)
            });

            Storage.saveHighScore(5000);
            
            const score = Storage.getHighScore();
            expect(score).toBe(5000);
        });

        test('should save zero score', () => {
            Storage.saveHighScore(0);
            
            const callArgs = mockLocalStorage.setItem.mock.calls[0];
            const savedData = JSON.parse(callArgs[1]);
            
            expect(savedData.score).toBe(0);
        });
    });

    describe('clearHighScore', () => {
        test('should remove high score from localStorage', () => {
            mockLocalStorage._setData({
                'asteroids-highscore': JSON.stringify({ score: 5000, date: '2026-02-25T00:00:00.000Z' })
            });

            Storage.clearHighScore();
            
            expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('asteroids-highscore');
        });

        test('should return true after clearing', () => {
            const result = Storage.clearHighScore();
            expect(result).toBe(true);
        });

        test('should not throw when localStorage is unavailable', () => {
            Storage._setStorage(createMockLocalStorageUnavailable());

            expect(() => Storage.clearHighScore()).not.toThrow();
        });

        test('should return false when localStorage throws error', () => {
            Storage._setStorage(createMockLocalStorageUnavailable());

            const result = Storage.clearHighScore();
            expect(result).toBe(false);
        });
    });

    describe('getHighScoreDate', () => {
        test('should return null when no high score exists', () => {
            const date = Storage.getHighScoreDate();
            expect(date).toBeNull();
        });

        test('should return date when high score exists', () => {
            const testData = {
                score: 5000,
                date: '2026-02-25T12:30:00.000Z'
            };
            mockLocalStorage._setData({
                'asteroids-highscore': JSON.stringify(testData)
            });

            const date = Storage.getHighScoreDate();
            expect(date).toBe('2026-02-25T12:30:00.000Z');
        });

        test('should return null when date property is missing', () => {
            const testData = {
                score: 5000
            };
            mockLocalStorage._setData({
                'asteroids-highscore': JSON.stringify(testData)
            });

            const date = Storage.getHighScoreDate();
            expect(date).toBeNull();
        });

        test('should return null when stored data is invalid JSON', () => {
            mockLocalStorage._setData({
                'asteroids-highscore': 'invalid-json'
            });

            const date = Storage.getHighScoreDate();
            expect(date).toBeNull();
        });

        test('should return null when localStorage throws error', () => {
            global.localStorage = createMockLocalStorageUnavailable();
            
            const date = Storage.getHighScoreDate();
            expect(date).toBeNull();
        });
    });

    describe('Integration: save and load', () => {
        test('should load the same score that was saved', () => {
            Storage.saveHighScore(7500);
            const loadedScore = Storage.getHighScore();
            expect(loadedScore).toBe(7500);
        });

        test('should load the same date that was saved', () => {
            Storage.saveHighScore(7500);
            const savedDate = Storage.getHighScoreDate();
            expect(savedDate).not.toBeNull();
            expect(savedDate).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z$/);
        });

        test('should update high score when saving multiple times', () => {
            Storage.saveHighScore(3000);
            Storage.saveHighScore(5000);
            Storage.saveHighScore(7000);
            
            const score = Storage.getHighScore();
            expect(score).toBe(7000);
        });
    });
});
