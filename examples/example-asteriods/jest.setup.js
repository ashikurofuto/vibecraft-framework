/**
 * Jest setup for ES modules
 * Ensures jest globals are available in test files
 */
import { jest } from '@jest/globals';

// Глобальный jest для работы в ES modules контексте
global.jest = jest;

// Синхронизируем localStorage между global и window для тестов
// Это позволяет тестам использовать global.localStorage и видеть его в коде
if (typeof window !== 'undefined' && typeof global !== 'undefined') {
    // Создаём общий mock storage если ещё не создан
    if (!global.__mockStorage) {
        global.__mockStorage = {
            _data: {},
            getItem: function(key) { return this._data[key] || null; },
            setItem: function(key, value) { this._data[key] = String(value); },
            removeItem: function(key) { delete this._data[key]; },
            clear: function() { this._data = {}; }
        };
    }
    
    // Синхронизируем window.localStorage с global.localStorage
    Object.defineProperty(window, 'localStorage', {
        get: function() { return global.__mockStorage; },
        configurable: true
    });
    
    Object.defineProperty(global, 'localStorage', {
        get: function() { return global.__mockStorage; },
        configurable: true
    });
}
