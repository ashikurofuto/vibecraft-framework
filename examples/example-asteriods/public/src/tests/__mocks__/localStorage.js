/**
 * Mock для localStorage
 * Используется в тестах Infrastructure слоя
 */
import { jest } from '@jest/globals';

/**
 * Создаёт мок для localStorage
 * @returns {Object} Мок объекта localStorage с методами Jest
 */
export function createMockLocalStorage() {
    const store = {};

    return {
        getItem: jest.fn((key) => {
            return store[key] || null;
        }),

        setItem: jest.fn((key, value) => {
            store[key] = String(value);
        }),

        removeItem: jest.fn((key) => {
            delete store[key];
        }),

        clear: jest.fn(() => {
            Object.keys(store).forEach(k => delete store[k]);
        }),

        key: jest.fn((index) => {
            const keys = Object.keys(store);
            return keys[index] || null;
        }),

        get length() {
            return Object.keys(store).length;
        },

        // Метод для сброса состояния между тестами
        _reset: () => {
            Object.keys(store).forEach(k => delete store[k]);
            jest.clearAllMocks();
        },

        // Метод для установки начального состояния
        _setData: (data) => {
            Object.keys(data).forEach(key => {
                store[key] = data[key];
            });
        }
    };
}

/**
 * Создаёт недоступный localStorage (для тестирования обработки ошибок)
 * @returns {Object} Мок который выбрасывает ошибки
 */
export function createMockLocalStorageUnavailable() {
    return {
        getItem: jest.fn(() => {
            throw new Error('localStorage unavailable');
        }),
        setItem: jest.fn(() => {
            throw new Error('localStorage unavailable');
        }),
        removeItem: jest.fn(() => {
            throw new Error('localStorage unavailable');
        }),
        clear: jest.fn(() => {
            throw new Error('localStorage unavailable');
        })
    };
}

/**
 * Создаёт localStorage с невалидными данными
 * @param {string} invalidData - Данные для возврата
 * @returns {Object} Мок с невалидными данными
 */
export function createMockLocalStorageWithInvalidData(invalidData = 'invalid-json') {
    return {
        getItem: jest.fn(() => invalidData),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn()
    };
}
