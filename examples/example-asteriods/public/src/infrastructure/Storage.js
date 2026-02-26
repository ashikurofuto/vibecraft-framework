/**
 * Storage — абстракция над localStorage для сохранения рекордов
 * Infrastructure Layer
 * 
 * @description Предоставляет методы для сохранения и загрузки высокого счёта
 * с обработкой ошибок localStorage
 */
export class Storage {
    /**
     * Ключ для хранения в localStorage
     * @private
     * @type {string}
     */
    static #STORAGE_KEY = 'asteroids-highscore';

    /**
     * Ссылка на localStorage (может быть заменена для тестирования)
     * @private
     * @type {Storage}
     */
    static #storage = null;

    /**
     * Получить текущий storage (localStorage или global.localStorage для тестов)
     * @private
     * @returns {Storage}
     */
    static #getStorage() {
        // Приоритет 1: Custom storage (для тестов через _setStorage)
        if (this.#storage) {
            return this.#storage;
        }
        
        // Приоритет 2: global.localStorage (для тестов где устанавливают global.localStorage)
        if (typeof global !== 'undefined' && global.localStorage) {
            return global.localStorage;
        }
        
        // Приоритет 3: window.localStorage (для browser/jsdom среды)
        if (typeof window !== 'undefined' && window.localStorage) {
            return window.localStorage;
        }
        
        // Приоритет 4: globalThis.localStorage
        if (typeof globalThis !== 'undefined' && globalThis.localStorage) {
            return globalThis.localStorage;
        }
        
        // Fallback: обычный localStorage
        return typeof localStorage !== 'undefined' ? localStorage : null;
    }

    /**
     * Установить storage для тестирования
     * @param {Storage} storage - Мок storage для тестов
     * @internal
     */
    static _setStorage(storage) {
        this.#storage = storage;
    }

    /**
     * Сбросить storage к localStorage
     * @internal
     */
    static _resetStorage() {
        this.#storage = null;
    }

    /**
     * Получить высокий счёт из localStorage
     * @returns {number} Высокий счёт или 0 если не существует
     */
    static getHighScore() {
        try {
            const data = this.#getStorage().getItem(this.#STORAGE_KEY);
            if (!data) {
                return 0;
            }
            const parsed = JSON.parse(data);
            return parsed.score || 0;
        } catch (e) {
            console.warn('Failed to load high score:', e.message);
            return 0;
        }
    }

    /**
     * Сохранить высокий счёт в localStorage
     * @param {number} score - Счёт для сохранения
     */
    static saveHighScore(score) {
        try {
            const data = {
                score,
                date: new Date().toISOString()
            };
            this.#getStorage().setItem(this.#STORAGE_KEY, JSON.stringify(data));
        } catch (e) {
            console.warn('Failed to save high score:', e.message);
        }
    }

    /**
     * Очистить высокий счёт из localStorage
     * @returns {boolean} true если успешно, false если ошибка
     */
    static clearHighScore() {
        try {
            this.#getStorage().removeItem(this.#STORAGE_KEY);
            return true;
        } catch (e) {
            console.warn('Failed to clear high score:', e.message);
            return false;
        }
    }

    /**
     * Получить дату установки высокого счёта
     * @returns {string|null} ISO дата или null если не существует
     */
    static getHighScoreDate() {
        try {
            const data = this.#getStorage().getItem(this.#STORAGE_KEY);
            if (!data) {
                return null;
            }
            const parsed = JSON.parse(data);
            return parsed.date || null;
        } catch (e) {
            console.warn('Failed to load high score date:', e.message);
            return null;
        }
    }
}
