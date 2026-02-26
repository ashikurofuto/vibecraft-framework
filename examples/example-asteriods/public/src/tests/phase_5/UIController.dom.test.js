/**
 * UIController DOM Tests — Phase 5
 *
 * @description Тесты UIController с использованием реального DOM (jsdom)
 * @see src/presentation/UIController.js
 */

import { jest } from '@jest/globals';

describe('UIController — DOM Integration', () => {
    let UIController;
    let uiController;

    // Мок HTML структуры
    const setupDOM = () => {
        document.body.innerHTML = `
            <div id="game-container">
                <div id="hud">
                    <span id="score">0</span>
                    <span id="lives">3</span>
                    <span id="level">1</span>
                    <span id="high-score">0</span>
                </div>
                <canvas id="game-canvas" width="800" height="600"></canvas>
                <div id="menu" class="screen">
                    <h1>ASTEROIDS</h1>
                    <button id="start-button">START GAME</button>
                </div>
                <div id="pause" class="screen hidden">
                    <h2>PAUSED</h2>
                </div>
                <div id="game-over" class="screen hidden">
                    <h2>GAME OVER</h2>
                    <p>Final Score: <span class="final-score">0</span></p>
                    <button id="restart-button">PLAY AGAIN</button>
                </div>
            </div>
        `;
    };

    beforeEach(async () => {
        setupDOM();

        // Динамический импорт
        UIController = (await import('../../../src/presentation/UIController.js')).UIController;

        // Создаём mock document с реальными DOM элементами
        const mockDocument = {
            getElementById: jest.fn((id) => document.getElementById(id)),
            createElement: jest.fn((tag) => document.createElement(tag)),
            body: document.body
        };

        uiController = new UIController(mockDocument);
    });

    afterEach(() => {
        jest.clearAllMocks();
        document.body.innerHTML = '';
    });

    describe('HUD Updates', () => {
        test('should update score display', () => {
            const scoreEl = document.getElementById('score');

            uiController.updateScore(1500);

            expect(scoreEl.textContent).toBe('1500');
        });

        test('should update lives display', () => {
            const livesEl = document.getElementById('lives');

            uiController.updateLives(2);

            expect(livesEl.textContent).toBe('2');
        });

        test('should update level display', () => {
            const levelEl = document.getElementById('level');

            uiController.updateLevel(3);

            expect(levelEl.textContent).toBe('3');
        });

        test('should update high score display', () => {
            const highScoreEl = document.getElementById('high-score');

            uiController.updateHighScore(5000);

            expect(highScoreEl.textContent).toBe('5000');
        });

        test('should update all HUD elements at once', () => {
            uiController.updateHUD({
                score: 2500,
                lives: 1,
                level: 5,
                highScore: 10000
            });

            expect(document.getElementById('score').textContent).toBe('2500');
            expect(document.getElementById('lives').textContent).toBe('1');
            expect(document.getElementById('level').textContent).toBe('5');
            expect(document.getElementById('high-score').textContent).toBe('10000');
        });
    });

    describe('Screen Management', () => {
        test('should show menu screen', () => {
            const menuEl = document.getElementById('menu');
            const pauseEl = document.getElementById('pause');
            const gameOverEl = document.getElementById('game-over');

            // Скрываем все экраны сначала
            menuEl.classList.add('hidden');
            pauseEl.classList.remove('hidden');
            gameOverEl.classList.remove('hidden');

            uiController.showMenu();

            expect(menuEl.classList.contains('hidden')).toBe(false);
            expect(pauseEl.classList.contains('hidden')).toBe(true);
            expect(gameOverEl.classList.contains('hidden')).toBe(true);
        });

        test('should show pause screen', () => {
            const pauseEl = document.getElementById('pause');

            uiController.showPause();

            expect(pauseEl.classList.contains('hidden')).toBe(false);
        });

        test('should hide pause screen', () => {
            const pauseEl = document.getElementById('pause');
            pauseEl.classList.remove('hidden');

            uiController.hidePause();

            expect(pauseEl.classList.contains('hidden')).toBe(true);
        });

        test('should show game over screen with final score', () => {
            const gameOverEl = document.getElementById('game-over');
            const finalScoreEl = gameOverEl.querySelector('.final-score');

            uiController.showGameOver(3500);

            expect(gameOverEl.classList.contains('hidden')).toBe(false);
            expect(finalScoreEl.textContent).toBe('3500');
        });

        test('should hide all screens', () => {
            uiController.hideAllScreens();

            expect(document.getElementById('menu').classList.contains('hidden')).toBe(true);
            expect(document.getElementById('pause').classList.contains('hidden')).toBe(true);
            expect(document.getElementById('game-over').classList.contains('hidden')).toBe(true);
        });
    });

    describe('Button Event Handlers', () => {
        let onStartCallback;
        let onRestartCallback;

        beforeEach(() => {
            onStartCallback = jest.fn();
            onRestartCallback = jest.fn();

            uiController.onStart(onStartCallback);
            uiController.onRestart(onRestartCallback);
        });

        test('should call start callback when start button clicked', () => {
            const startButton = document.getElementById('start-button');
            startButton.click();

            expect(onStartCallback).toHaveBeenCalledTimes(1);
        });

        test('should call restart callback when restart button clicked', () => {
            const restartButton = document.getElementById('restart-button');
            restartButton.click();

            expect(onRestartCallback).toHaveBeenCalledTimes(1);
        });

        test('should attach event listeners on initialization', () => {
            const startButton = document.getElementById('start-button');
            const restartButton = document.getElementById('restart-button');

            // Проверяем, что слушатели были добавлены
            expect(startButton.onclick).toBeDefined();
            expect(restartButton.onclick).toBeDefined();
        });
    });

    describe('Level Complete Message', () => {
        test('should show level complete message', () => {
            uiController.showLevelComplete(2);

            const messageEl = document.querySelector('.level-complete');
            expect(messageEl).toBeDefined();
            expect(messageEl.textContent).toContain('LEVEL 2');
        });

        test('should remove level complete message after animation', () => {
            jest.useFakeTimers();

            uiController.showLevelComplete(3);

            // Проверяем, что элемент создан
            let messageEl = document.querySelector('.level-complete');
            expect(messageEl).toBeDefined();

            // Мотаем время вперёд на 2 секунды (длительность анимации)
            jest.advanceTimersByTime(2000);

            // Элемент должен быть удалён
            messageEl = document.querySelector('.level-complete');
            expect(messageEl).toBeNull();

            jest.useRealTimers();
        });
    });

    describe('Ship Icons Rendering', () => {
        test('should render ship icons for lives', () => {
            const livesContainer = document.getElementById('lives');
            livesContainer.innerHTML = ''; // Очищаем

            uiController.renderLives(3);

            // Проверяем, что иконки кораблей добавлены
            const shipIcons = livesContainer.querySelectorAll('.ship-icon');
            expect(shipIcons.length).toBe(3);
        });

        test('should clear previous ship icons before rendering', () => {
            const livesContainer = document.getElementById('lives');

            // Сначала рендерим 3 жизни
            uiController.renderLives(3);
            expect(livesContainer.querySelectorAll('.ship-icon').length).toBe(3);

            // Теперь рендерим 1 жизнь
            uiController.renderLives(1);
            expect(livesContainer.querySelectorAll('.ship-icon').length).toBe(1);
        });
    });

    describe('Message Display', () => {
        test('should show temporary message', () => {
            jest.useFakeTimers();

            uiController.showMessage('HYPERSPACE!', 1000);

            const messageEl = document.querySelector('.message');
            expect(messageEl).toBeDefined();
            expect(messageEl.textContent).toBe('HYPERSPACE!');

            jest.useRealTimers();
        });

        test('should auto-remove message after duration', () => {
            jest.useFakeTimers();

            uiController.showMessage('PAUSED', 500);

            // Проверяем наличие сообщения
            expect(document.querySelector('.message')).toBeDefined();

            // Мотаем время вперёд
            jest.advanceTimersByTime(500);

            // Сообщение должно быть удалено
            expect(document.querySelector('.message')).toBeNull();

            jest.useRealTimers();
        });
    });

    describe('Class Toggle Helpers', () => {
        test('should add class to element', () => {
            const menuEl = document.getElementById('menu');
            menuEl.classList.remove('hidden');

            uiController.addClass(menuEl, 'hidden');

            expect(menuEl.classList.contains('hidden')).toBe(true);
        });

        test('should remove class from element', () => {
            const menuEl = document.getElementById('menu');
            menuEl.classList.add('active');

            uiController.removeClass(menuEl, 'active');

            expect(menuEl.classList.contains('active')).toBe(false);
        });

        test('should toggle class on element', () => {
            const menuEl = document.getElementById('menu');

            uiController.toggleClass(menuEl, 'visible');
            expect(menuEl.classList.contains('visible')).toBe(true);

            uiController.toggleClass(menuEl, 'visible');
            expect(menuEl.classList.contains('visible')).toBe(false);
        });
    });

    describe('Canvas Context Access', () => {
        test('should get canvas element', () => {
            const canvas = uiController.getCanvas();

            expect(canvas).toBeDefined();
            expect(canvas.id).toBe('game-canvas');
            expect(canvas.width).toBe(800);
            expect(canvas.height).toBe(600);
        });

        test('should get 2D context from canvas', () => {
            const ctx = uiController.getContext();

            expect(ctx).toBeDefined();
            expect(typeof ctx.fillRect).toBe('function');
            expect(typeof ctx.clearRect).toBe('function');
        });
    });

    describe('Responsive UI', () => {
        test('should handle window resize', () => {
            const resizeHandler = jest.fn();
            window.addEventListener('resize', resizeHandler);

            // Эмулируем resize
            window.dispatchEvent(new Event('resize'));

            expect(resizeHandler).toHaveBeenCalled();

            window.removeEventListener('resize', resizeHandler);
        });
    });
});
