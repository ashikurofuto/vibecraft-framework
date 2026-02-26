/**
 * Управление состоянием игры
 * @description Отвечает за переходы между состояниями (menu, playing, paused, gameover),
 * отслеживание уровня, очков, жизней
 */
export class GameState {
    /**
     * @param {Object} callbacks - Callback functions for state changes
     * @param {Function} [callbacks.onGameOver] - Called when game over
     */
    constructor(callbacks = {}) {
        this.state = 'menu';
        this.level = 1;
        this.lives = 3;
        this.score = 0;
        this.highScore = 0;
        this.callbacks = callbacks;
    }

    /**
     * Проверка состояния menu
     * @returns {boolean}
     */
    isMenu() {
        return this.state === 'menu';
    }

    /**
     * Проверка состояния playing
     * @returns {boolean}
     */
    isPlaying() {
        return this.state === 'playing';
    }

    /**
     * Проверка состояния paused
     * @returns {boolean}
     */
    isPaused() {
        return this.state === 'paused';
    }

    /**
     * Проверка состояния gameover
     * @returns {boolean}
     */
    isGameOver() {
        return this.state === 'gameover';
    }

    /**
     * Начало новой игры
     */
    start() {
        this.state = 'playing';
        this.level = 1;
        this.lives = 3;
        this.score = 0;
    }

    /**
     * Пауза игры (только если playing)
     */
    pause() {
        if (this.state === 'playing') {
            this.state = 'paused';
        }
    }

    /**
     * Возобновление игры (только если paused)
     */
    resume() {
        if (this.state === 'paused') {
            this.state = 'playing';
        }
    }

    /**
     * Получение урона (потеря жизни)
     */
    hit() {
        if (this.state === 'playing' || this.state === 'paused') {
            this.lives = Math.max(0, this.lives - 1);
            if (this.lives <= 0) {
                this.state = 'gameover';
                if (this.callbacks.onGameOver) {
                    this.callbacks.onGameOver();
                }
            }
        }
    }

    /**
     * Переход на следующий уровень
     */
    nextLevel() {
        if (this.state === 'playing') {
            this.level++;
        }
    }

    /**
     * Добавление очков
     * @param {number} points - количество очков
     */
    addScore(points) {
        if (this.state === 'playing') {
            this.score += points;
            if (this.score > this.highScore) {
                this.highScore = this.score;
            }
        }
    }

    /**
     * Завершение игры (game over)
     */
    gameOver() {
        this.state = 'gameover';
        if (this.callbacks.onGameOver) {
            this.callbacks.onGameOver();
        }
    }
}
