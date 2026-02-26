/**
 * InputHandler — компонент обработки ввода с клавиатуры
 * @module InputHandler
 * @description Обрабатывает нажатия клавиш, отслеживает состояние и предоставляет
 * агрегированное состояние ввода для игры
 */

export class InputHandler {
    /**
     * Создаёт обработчик ввода
     * @param {Window} windowObj - Объект window для подписки на события (по умолчанию window)
     */
    constructor(windowObj = window) {
        this.window = windowObj;
        this.keys = new Set();
        this.previousKeys = new Set();

        // Подписка на события клавиатуры
        this.window.addEventListener('keydown', (e) => {
            // Вызываем preventDefault только для игровых клавиш
            const gameKeys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Space', 'KeyW', 'KeyA', 'KeyS', 'KeyD', 'KeyP', 'KeyH'];
            if (gameKeys.includes(e.code)) {
                e.preventDefault();
            }
            this.keys.add(e.code);
        });

        this.window.addEventListener('keyup', (e) => {
            this.keys.delete(e.code);
        });
    }

    /**
     * Проверяет, нажата ли клавиша в текущий момент
     * @param {string} code - Код клавиши (например, 'ArrowUp', 'Space')
     * @returns {boolean} true если клавиша нажата
     */
    isPressed(code) {
        return this.keys.has(code);
    }

    /**
     * Проверяет, была ли клавиша нажата только что в текущем кадре
     * (edge detection для однократных действий)
     * @param {string} code - Код клавиши
     * @returns {boolean} true если клавиша была нажата в текущем кадре
     */
    wasJustPressed(code) {
        return this.keys.has(code) && !this.previousKeys.has(code);
    }

    /**
     * Завершает текущий кадр — сохраняет состояние клавиш как предыдущее
     * Вызывается в конце каждого кадра игры
     */
    endFrame() {
        this.previousKeys = new Set(this.keys);
    }

    /**
     * Сбрасывает все состояния клавиш
     * Вызывается при перезапуске игры или при необходимости очистить ввод
     */
    reset() {
        this.keys.clear();
        this.previousKeys.clear();
    }

    /**
     * Получает агрегированное состояние ввода
     * @returns {Object} Объект с состояниями действий
     * @returns {boolean} return.thrust - Тяга (ArrowUp / ArrowDown / W / S)
     * @returns {boolean} return.rotateLeft - Вращение влево (ArrowLeft / A)
     * @returns {boolean} return.rotateRight - Вращение вправо (ArrowRight / D)
     * @returns {boolean} return.fire - Огонь (Space)
     * @returns {boolean} return.hyperspace - Гиперпространство (H)
     * @returns {boolean} return.pause - Пауза (P)
     */
    getState() {
        return {
            thrust: this.isPressed('ArrowUp') || this.isPressed('ArrowDown') || this.isPressed('KeyW') || this.isPressed('KeyS'),
            rotateLeft: this.isPressed('ArrowLeft') || this.isPressed('KeyA'),
            rotateRight: this.isPressed('ArrowRight') || this.isPressed('KeyD'),
            fire: this.isPressed('Space'),
            hyperspace: this.isPressed('KeyH'),
            pause: this.isPressed('KeyP')
        };
    }
}
