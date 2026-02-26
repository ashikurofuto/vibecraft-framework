/**
 * Менеджер очков и рекордов
 * @description Отвечает за подсчёт текущих очков, отслеживание рекорда
 * и сохранение/загрузку рекорда через Storage
 */
export class ScoreManager {
    /**
     * @param {Object} storage - Storage интерфейс для сохранения рекордов
     */
    constructor(storage) {
        this.storage = storage;
        this.currentScore = 0;
        this.highScore = 0;
        
        // Загружаем рекорд при инициализации
        try {
            const loadedHighScore = storage.getHighScore();
            this.highScore = loadedHighScore || 0;
        } catch (e) {
            // Игнорируем ошибки storage, используем 0
            this.highScore = 0;
        }
    }

    /**
     * Получение текущего счёта
     * @returns {number}
     */
    getCurrentScore() {
        return this.currentScore;
    }

    /**
     * Получение рекорда
     * @returns {number}
     */
    getHighScore() {
        return this.highScore;
    }

    /**
     * Добавление очков
     * @param {number} points - количество очков
     */
    addScore(points) {
        this.currentScore += points;

        // Обновляем рекорд если текущий счёт превысил его
        if (this.currentScore > this.highScore) {
            this.highScore = this.currentScore;
            this.saveHighScore(); // ✅ Автоматически сохраняем рекорд
        }
    }

    /**
     * Сохранение рекорда в storage
     */
    saveHighScore() {
        try {
            this.storage.saveHighScore(this.highScore);
        } catch (e) {
            // Игнорируем ошибки сохранения
        }
    }

    /**
     * Сброс текущего счёта
     */
    reset() {
        this.currentScore = 0;
    }

    /**
     * Начало новой игры (сброс с сохранением рекорда)
     */
    newGame() {
        // Сохраняем рекорд если он был побит
        if (this.currentScore > this.highScore) {
            this.highScore = this.currentScore;
            try {
                this.storage.saveHighScore(this.highScore);
            } catch (e) {
                // Игнорируем ошибки
            }
        }
        this.reset();
    }
}
