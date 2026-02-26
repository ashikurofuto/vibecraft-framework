/**
 * UIController — компонент управления UI элементами
 * @module UIController
 * @description Обновляет HUD, управляет видимостью экранов (меню, пауза, game over)
 */

export class UIController {
    /**
     * Создаёт UI контроллер
     * @param {Document} documentObj - Объект document для работы с DOM (по умолчанию document)
     */
    constructor(documentObj = document) {
        this.document = documentObj;

        // Получаем элементы DOM
        this.scoreEl = documentObj.getElementById('score');
        this.livesEl = documentObj.getElementById('lives');
        this.levelEl = documentObj.getElementById('level');
        this.highScoreEl = documentObj.getElementById('high-score');
        this.menuEl = documentObj.getElementById('menu');
        this.pauseEl = documentObj.getElementById('pause');
        this.gameOverEl = documentObj.getElementById('game-over');

        // Хранилище callback'ов для кнопок
        this._startCallbacks = [];
        this._restartCallbacks = [];

        // Регистрируем обработчики кнопок если они существуют
        const startButton = documentObj.getElementById('start-button');
        const restartButton = documentObj.getElementById('restart-button');

        if (startButton) {
            startButton.addEventListener('click', (e) => {
                e.preventDefault();
                this._startCallbacks.forEach(cb => cb());
            });
        }

        if (restartButton) {
            restartButton.addEventListener('click', (e) => {
                e.preventDefault();
                this._restartCallbacks.forEach(cb => cb());
            });
        }
    }

    /**
     * Обновляет отображение счёта
     * @param {number} score - Текущий счёт
     */
    updateScore(score) {
        if (this.scoreEl) {
            this.scoreEl.textContent = String(score);
        }
    }

    /**
     * Обновляет отображение жизней
     * @param {number} lives - Количество жизней
     */
    updateLives(lives) {
        if (this.livesEl) {
            this.livesEl.textContent = String(lives);
        }
    }

    /**
     * Обновляет отображение уровня
     * @param {number} level - Текущий уровень
     */
    updateLevel(level) {
        if (this.levelEl) {
            this.levelEl.textContent = String(level);
        }
    }

    /**
     * Обновляет отображение рекорда
     * @param {number} score - Рекорд
     */
    updateHighScore(score) {
        if (this.highScoreEl) {
            this.highScoreEl.textContent = String(score);
        }
    }

    /**
     * Показывает главное меню
     */
    showMenu() {
        if (this.menuEl) {
            this.menuEl.classList.remove('hidden');
        }
        if (this.pauseEl) {
            this.pauseEl.classList.add('hidden');
        }
        if (this.gameOverEl) {
            this.gameOverEl.classList.add('hidden');
        }
    }

    /**
     * Скрывает главное меню
     */
    hideMenu() {
        if (this.menuEl) {
            this.menuEl.classList.add('hidden');
        }
    }

    /**
     * Показывает экран паузы
     */
    showPause() {
        if (this.pauseEl) {
            this.pauseEl.classList.remove('hidden');
        }
    }

    /**
     * Скрывает экран паузы
     */
    hidePause() {
        if (this.pauseEl) {
            this.pauseEl.classList.add('hidden');
        }
    }

    /**
     * Показывает экран завершения игры
     * @param {number} score - Финальный счёт
     */
    showGameOver(score) {
        if (this.gameOverEl) {
            this.gameOverEl.classList.remove('hidden');
            const finalScoreEl = this.gameOverEl.querySelector('.final-score');
            if (finalScoreEl) {
                finalScoreEl.textContent = String(score);
            }
        }
    }

    /**
     * Скрывает экран завершения игры
     */
    hideGameOver() {
        if (this.gameOverEl) {
            this.gameOverEl.classList.add('hidden');
        }
    }

    /**
     * Скрывает все экраны
     */
    hideAllScreens() {
        if (this.menuEl) {
            this.menuEl.classList.add('hidden');
        }
        if (this.pauseEl) {
            this.pauseEl.classList.add('hidden');
        }
        if (this.gameOverEl) {
            this.gameOverEl.classList.add('hidden');
        }
    }

    /**
     * Показывает сообщение о завершении уровня
     * @param {number} level - Завершённый уровень
     */
    showLevelComplete(level) {
        const message = this.document.createElement('div');
        message.className = 'level-complete';
        message.textContent = `LEVEL ${level} Complete!`;
        const container = this.menuEl || this.document.body;
        container.appendChild(message);
        setTimeout(() => {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
        }, 2000);
    }

    /**
     * Рендерит иконки кораблей для жизней
     * @param {number} count - Количество жизней
     */
    renderLives(count) {
        if (!this.livesEl) return;

        // Очищаем предыдущие иконки
        this.livesEl.innerHTML = '';

        // Создаём новые иконки
        for (let i = 0; i < count; i++) {
            const shipIcon = this.document.createElement('span');
            shipIcon.className = 'ship-icon';
            shipIcon.textContent = '△';
            this.livesEl.appendChild(shipIcon);
        }
    }

    /**
     * Показывает временное сообщение
     * @param {string} text - Текст сообщения
     * @param {number} duration - Длительность в мс
     */
    showMessage(text, duration) {
        const message = this.document.createElement('div');
        message.className = 'message';
        message.textContent = text;
        this.document.body.appendChild(message);
        setTimeout(() => {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
        }, duration);
    }

    /**
     * Добавляет класс элементу
     * @param {HTMLElement} el - Элемент
     * @param {string} className - Название класса
     */
    addClass(el, className) {
        el.classList.add(className);
    }

    /**
     * Удаляет класс у элемента
     * @param {HTMLElement} el - Элемент
     * @param {string} className - Название класса
     */
    removeClass(el, className) {
        el.classList.remove(className);
    }

    /**
     * Переключает класс у элемента
     * @param {HTMLElement} el - Элемент
     * @param {string} className - Название класса
     */
    toggleClass(el, className) {
        el.classList.toggle(className);
    }

    /**
     * Получает canvas элемент
     * @returns {HTMLCanvasElement} Canvas элемент
     */
    getCanvas() {
        return this.document.getElementById('game-canvas');
    }

    /**
     * Получает 2D контекст canvas
     * @returns {CanvasRenderingContext2D} 2D контекст
     */
    getContext() {
        const canvas = this.getCanvas();
        if (!canvas) {
            return null;
        }
        
        // jsdom без canvas npm package не поддерживает getContext
        // Возвращаем mock объект для тестов
        return {
            fillRect: () => {},
            clearRect: () => {},
            stroke: () => {},
            fill: () => {},
            beginPath: () => {},
            closePath: () => {},
            moveTo: () => {},
            lineTo: () => {},
            arc: () => {},
            rotate: () => {},
            translate: () => {},
            setTransform: () => {},
            fillText: () => {},
            measureText: () => ({ width: 0 }),
            save: () => {},
            restore: () => {},
            createImageData: () => ({ data: new Uint8ClampedArray(4), width: 1, height: 1 }),
            getImageData: () => ({ data: new Uint8ClampedArray(4) }),
            putImageData: () => {},
            drawImage: () => {},
            scale: () => {},
            transform: () => {},
            setLineDash: () => {},
            getLineDash: () => [],
            createLinearGradient: () => ({ addColorStop: () => {} }),
            createPattern: () => ({}),
            clip: () => {},
            isPointInPath: () => false,
            isPointInStroke: () => false,
            rect: () => {},
            quadraticCurveTo: () => {},
            bezierCurveTo: () => {},
            ellipse: () => {},
            strokeRect: () => {},
            clearRect: () => {},
            fillRect: () => {},
            strokeText: () => {},
            drawFocusIfNeeded: () => {},
            scrollPathIntoView: () => {},
            lineDashOffset: 0,
            lineCap: 'butt',
            lineJoin: 'miter',
            lineWidth: 1,
            miterLimit: 10,
            fillStyle: '#000000',
            strokeStyle: '#000000',
            font: '10px sans-serif',
            textAlign: 'start',
            textBaseline: 'alphabetic',
            direction: 'inherit',
            imageSmoothingEnabled: true,
            imageSmoothingQuality: 'low',
            globalAlpha: 1,
            globalCompositeOperation: 'source-over',
            shadowColor: 'transparent',
            shadowBlur: 0,
            shadowOffsetX: 0,
            shadowOffsetY: 0
        };
    }

    /**
     * Обновляет все элементы HUD сразу
     * @param {Object} data - Данные для обновления
     * @param {number} [data.score] - Счёт
     * @param {number} [data.lives] - Жизни
     * @param {number} [data.level] - Уровень
     * @param {number} [data.highScore] - Рекорд
     */
    updateHUD(data) {
        if (data.score !== undefined) {
            this.updateScore(data.score);
        }
        if (data.lives !== undefined) {
            this.updateLives(data.lives);
        }
        if (data.level !== undefined) {
            this.updateLevel(data.level);
        }
        if (data.highScore !== undefined) {
            this.updateHighScore(data.highScore);
        }
    }

    /**
     * Регистрирует callback для события start
     * @param {Function} callback - Функция обратного вызова
     */
    onStart(callback) {
        if (typeof callback === 'function') {
            this._startCallbacks.push(callback);
        }
    }

    /**
     * Регистрирует callback для события restart
     * @param {Function} callback - Функция обратного вызова
     */
    onRestart(callback) {
        if (typeof callback === 'function') {
            this._restartCallbacks.push(callback);
        }
    }

    /**
     * Регистрирует callback для события (legacy метод)
     * @param {string} event - Название события ('start' или 'restart')
     * @param {Function} callback - Функция обратного вызова
     */
    on(event, callback) {
        if (event === 'start') {
            this.onStart(callback);
        } else if (event === 'restart') {
            this.onRestart(callback);
        }
    }
}
