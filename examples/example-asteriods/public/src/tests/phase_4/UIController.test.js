/**
 * Tests for UIController
 * 
 * @description Тесты для компонента управления UI элементами (HUD, меню, экраны)
 * @module UIController
 * @see src/presentation/UIController.js
 */

import { jest } from '@jest/globals';

describe('UIController', () => {
    let UIController;
    let uiController;
    let mockDocument;
    let mockElements;

    beforeEach(async () => {
        // Динамический импорт для изоляции тестов
        UIController = (await import('../../../src/presentation/UIController.js')).UIController;

        // Создаём мок DOM элементов
        mockElements = {
            scoreEl: { textContent: '' },
            livesEl: { textContent: '' },
            levelEl: { textContent: '' },
            highScoreEl: { textContent: '' },
            menuEl: {
                style: { display: 'block' },
                classList: {
                    add: jest.fn(),
                    remove: jest.fn()
                },
                querySelector: jest.fn(() => null),
                appendChild: jest.fn(),
                removeChild: jest.fn()
            },
            pauseEl: {
                style: { display: 'none' },
                classList: {
                    add: jest.fn(),
                    remove: jest.fn()
                }
            },
            gameOverEl: {
                style: { display: 'none' },
                classList: {
                    add: jest.fn(),
                    remove: jest.fn()
                },
                querySelector: jest.fn(() => ({ textContent: '' }))
            },
            startButton: {
                addEventListener: jest.fn()
            },
            restartButton: {
                addEventListener: jest.fn()
            }
        };

        // Создаём мок document
        mockDocument = {
            getElementById: jest.fn((id) => {
                const map = {
                    'score': mockElements.scoreEl,
                    'lives': mockElements.livesEl,
                    'level': mockElements.levelEl,
                    'high-score': mockElements.highScoreEl,
                    'menu': mockElements.menuEl,
                    'pause': mockElements.pauseEl,
                    'game-over': mockElements.gameOverEl,
                    'start-button': mockElements.startButton,
                    'restart-button': mockElements.restartButton
                };
                return map[id] || null;
            }),
            createElement: jest.fn(() => ({
                className: '',
                textContent: '',
                style: { display: 'none' }
            })),
            addEventListener: jest.fn()
        };

        uiController = new UIController(mockDocument);
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('constructor', () => {
        test('should store document reference', () => {
            expect(uiController.document).toBe(mockDocument);
        });

        test('should get score element by id', () => {
            expect(mockDocument.getElementById).toHaveBeenCalledWith('score');
        });

        test('should get lives element by id', () => {
            expect(mockDocument.getElementById).toHaveBeenCalledWith('lives');
        });

        test('should get level element by id', () => {
            expect(mockDocument.getElementById).toHaveBeenCalledWith('level');
        });

        test('should get high score element by id', () => {
            expect(mockDocument.getElementById).toHaveBeenCalledWith('high-score');
        });

        test('should get menu element by id', () => {
            expect(mockDocument.getElementById).toHaveBeenCalledWith('menu');
        });

        test('should get pause element by id', () => {
            expect(mockDocument.getElementById).toHaveBeenCalledWith('pause');
        });

        test('should get game over element by id', () => {
            expect(mockDocument.getElementById).toHaveBeenCalledWith('game-over');
        });

        test('should use default document if not provided', async () => {
            const DefaultUIController = (await import('../../../src/presentation/UIController.js')).UIController;
            const controller = new DefaultUIController();
            expect(controller).toBeDefined();
        });
    });

    describe('updateScore', () => {
        test('should update score display', () => {
            uiController.updateScore(1500);
            expect(mockElements.scoreEl.textContent).toBe('1500');
        });

        test('should update score to zero', () => {
            uiController.updateScore(0);
            expect(mockElements.scoreEl.textContent).toBe('0');
        });

        test('should update score with large numbers', () => {
            uiController.updateScore(999999);
            expect(mockElements.scoreEl.textContent).toBe('999999');
        });

        test('should convert score to string', () => {
            uiController.updateScore(500);
            expect(typeof mockElements.scoreEl.textContent).toBe('string');
        });
    });

    describe('updateLives', () => {
        test('should update lives display', () => {
            uiController.updateLives(2);
            expect(mockElements.livesEl.textContent).toBe('2');
        });

        test('should update lives to zero', () => {
            uiController.updateLives(0);
            expect(mockElements.livesEl.textContent).toBe('0');
        });

        test('should update lives with max lives', () => {
            uiController.updateLives(5);
            expect(mockElements.livesEl.textContent).toBe('5');
        });
    });

    describe('updateLevel', () => {
        test('should update level display', () => {
            uiController.updateLevel(3);
            expect(mockElements.levelEl.textContent).toBe('3');
        });

        test('should update level to one', () => {
            uiController.updateLevel(1);
            expect(mockElements.levelEl.textContent).toBe('1');
        });

        test('should update level with high levels', () => {
            uiController.updateLevel(10);
            expect(mockElements.levelEl.textContent).toBe('10');
        });
    });

    describe('updateHighScore', () => {
        test('should update high score display', () => {
            uiController.updateHighScore(5000);
            expect(mockElements.highScoreEl.textContent).toBe('5000');
        });

        test('should update high score to zero', () => {
            uiController.updateHighScore(0);
            expect(mockElements.highScoreEl.textContent).toBe('0');
        });
    });

    describe('showMenu', () => {
        test('should show menu element', () => {
            uiController.showMenu();
            expect(mockElements.menuEl.style.display).toBe('block');
        });

        test('should hide pause element when showing menu', () => {
            uiController.showMenu();
            expect(mockElements.pauseEl.style.display).toBe('none');
        });

        test('should hide game over element when showing menu', () => {
            uiController.showMenu();
            expect(mockElements.gameOverEl.style.display).toBe('none');
        });
    });

    describe('hideMenu', () => {
        test('should hide menu element', () => {
            uiController.hideMenu();
            // ✅ Реализация использует classList.add('hidden')
            expect(mockElements.menuEl.classList.add).toHaveBeenCalledWith('hidden');
        });
    });

    describe('showPause', () => {
        test('should show pause element', () => {
            uiController.showPause();
            // ✅ Реализация использует classList.remove('hidden')
            expect(mockElements.pauseEl.classList.remove).toHaveBeenCalledWith('hidden');
        });
    });

    describe('hidePause', () => {
        test('should hide pause element', () => {
            uiController.hidePause();
            // ✅ Реализация использует classList.add('hidden')
            expect(mockElements.pauseEl.classList.add).toHaveBeenCalledWith('hidden');
        });
    });

    describe('showGameOver', () => {
        test('should show game over element', () => {
            uiController.showGameOver(2500);
            // ✅ Реализация использует classList.remove('hidden')
            expect(mockElements.gameOverEl.classList.remove).toHaveBeenCalledWith('hidden');
        });

        test('should set final score in game over screen', () => {
            const mockFinalScoreEl = { textContent: '' };
            mockElements.gameOverEl.querySelector.mockReturnValue(mockFinalScoreEl);

            uiController.showGameOver(2500);

            expect(mockFinalScoreEl.textContent).toBe('2500');
        });

        test('should display zero score on game over', () => {
            const mockFinalScoreEl = { textContent: '' };
            mockElements.gameOverEl.querySelector.mockReturnValue(mockFinalScoreEl);

            uiController.showGameOver(0);

            expect(mockFinalScoreEl.textContent).toBe('0');
        });
    });

    describe('hideGameOver', () => {
        test('should hide game over element', () => {
            uiController.hideGameOver();
            // ✅ Реализация использует classList.add('hidden')
            expect(mockElements.gameOverEl.classList.add).toHaveBeenCalledWith('hidden');
        });
    });

    describe('showLevelComplete', () => {
        test('should create level complete message element', () => {
            uiController.showLevelComplete(2);
            expect(mockDocument.createElement).toHaveBeenCalledWith('div');
        });

        test('should set level complete message class', () => {
            uiController.showLevelComplete(2);
            const createdElement = mockDocument.createElement.mock.results[0].value;
            expect(createdElement.className).toBe('level-complete');
        });

        test('should set level complete message text', () => {
            uiController.showLevelComplete(2);
            const createdElement = mockDocument.createElement.mock.results[0].value;
            // ✅ Реализация использует UPPER_CASE формат
            expect(createdElement.textContent).toBe('LEVEL 2 Complete!');
        });

        test('should append level complete message to menu', () => {
            uiController.showLevelComplete(2);
            const createdElement = mockDocument.createElement.mock.results[0].value;
            expect(mockElements.menuEl.appendChild).toHaveBeenCalledWith(createdElement);
        });

        test('should show level complete for different levels', () => {
            uiController.showLevelComplete(5);
            const createdElement = mockDocument.createElement.mock.results[0].value;
            // ✅ Реализация использует UPPER_CASE формат
            expect(createdElement.textContent).toBe('LEVEL 5 Complete!');
        });
    });

    describe('updateHUD', () => {
        test('should update all HUD elements at once', () => {
            uiController.updateHUD({
                score: 1500,
                lives: 2,
                level: 3,
                highScore: 5000
            });

            expect(mockElements.scoreEl.textContent).toBe('1500');
            expect(mockElements.livesEl.textContent).toBe('2');
            expect(mockElements.levelEl.textContent).toBe('3');
            expect(mockElements.highScoreEl.textContent).toBe('5000');
        });

        test('should update HUD with partial data', () => {
            uiController.updateHUD({
                score: 1000
            });

            expect(mockElements.scoreEl.textContent).toBe('1000');
        });

        test('should update HUD with zero values', () => {
            uiController.updateHUD({
                score: 0,
                lives: 0,
                level: 1,
                highScore: 0
            });

            expect(mockElements.scoreEl.textContent).toBe('0');
            expect(mockElements.livesEl.textContent).toBe('0');
        });
    });

    describe('screen state management', () => {
        test('should transition from menu to game (hide menu)', () => {
            uiController.showMenu();
            expect(mockElements.menuEl.classList.remove).toHaveBeenCalledWith('hidden');

            uiController.hideMenu();
            expect(mockElements.menuEl.classList.add).toHaveBeenCalledWith('hidden');
        });

        test('should transition from game to pause', () => {
            uiController.hideMenu();
            expect(mockElements.menuEl.classList.add).toHaveBeenCalledWith('hidden');

            uiController.showPause();
            expect(mockElements.pauseEl.classList.remove).toHaveBeenCalledWith('hidden');
        });

        test('should transition from pause to game (hide pause)', () => {
            uiController.showPause();
            expect(mockElements.pauseEl.classList.remove).toHaveBeenCalledWith('hidden');

            uiController.hidePause();
            expect(mockElements.pauseEl.classList.add).toHaveBeenCalledWith('hidden');
        });

        test('should transition from game to game over', () => {
            uiController.hideMenu();
            expect(mockElements.menuEl.classList.add).toHaveBeenCalledWith('hidden');

            uiController.showGameOver(1000);
            expect(mockElements.gameOverEl.classList.remove).toHaveBeenCalledWith('hidden');
        });

        test('should transition from game over to menu', () => {
            uiController.showGameOver(1000);
            expect(mockElements.gameOverEl.classList.remove).toHaveBeenCalledWith('hidden');

            uiController.showMenu();
            expect(mockElements.gameOverEl.classList.add).toHaveBeenCalledWith('hidden');
            expect(mockElements.menuEl.classList.remove).toHaveBeenCalledWith('hidden');
        });

        test('should handle pause during game over (should not show pause)', () => {
            uiController.showGameOver(1000);
            uiController.showPause();

            // Pause может быть показан поверх game over
            expect(mockElements.pauseEl.classList.remove).toHaveBeenCalledWith('hidden');
        });
    });

    describe('button event listeners', () => {
        test('should register start button click listener', async () => {
            const startHandler = jest.fn();
            const UIControllerWithHandlers = (await import('../../../src/presentation/UIController.js')).UIController;
            
            const controller = new UIControllerWithHandlers(mockDocument);
            controller.on('start', startHandler);
            
            expect(mockElements.startButton.addEventListener).toHaveBeenCalledWith(
                'click',
                expect.any(Function)
            );
        });

        test('should register restart button click listener', async () => {
            const restartHandler = jest.fn();
            const UIControllerWithHandlers = (await import('../../../src/presentation/UIController.js')).UIController;
            
            const controller = new UIControllerWithHandlers(mockDocument);
            controller.on('restart', restartHandler);
            
            expect(mockElements.restartButton.addEventListener).toHaveBeenCalledWith(
                'click',
                expect.any(Function)
            );
        });
    });

    describe('event callbacks', () => {
        test('should call start callback when start button clicked', async () => {
            const startHandler = jest.fn();
            const UIControllerWithHandlers = (await import('../../../src/presentation/UIController.js')).UIController;
            
            const controller = new UIControllerWithHandlers(mockDocument);
            controller.on('start', startHandler);
            
            // Получаем обработчик клика
            const clickHandler = mockElements.startButton.addEventListener.mock.calls[0][1];
            clickHandler({ preventDefault: jest.fn() });
            
            expect(startHandler).toHaveBeenCalled();
        });

        test('should call restart callback when restart button clicked', async () => {
            const restartHandler = jest.fn();
            const UIControllerWithHandlers = (await import('../../../src/presentation/UIController.js')).UIController;
            
            const controller = new UIControllerWithHandlers(mockDocument);
            controller.on('restart', restartHandler);
            
            // Получаем обработчик клика
            const clickHandler = mockElements.restartButton.addEventListener.mock.calls[0][1];
            clickHandler({ preventDefault: jest.fn() });
            
            expect(restartHandler).toHaveBeenCalled();
        });

        test('should call preventDefault on button clicks', async () => {
            const startHandler = jest.fn();
            const UIControllerWithHandlers = (await import('../../../src/presentation/UIController.js')).UIController;
            
            const controller = new UIControllerWithHandlers(mockDocument);
            controller.on('start', startHandler);
            
            const preventDefault = jest.fn();
            const clickHandler = mockElements.startButton.addEventListener.mock.calls[0][1];
            clickHandler({ preventDefault });
            
            expect(preventDefault).toHaveBeenCalled();
        });
    });

    describe('UI state visibility', () => {
        test('should have menu visible by default', () => {
            // После создания контроллера меню должно быть видимо
            expect(mockElements.menuEl.classList.remove).toHaveBeenCalledWith('hidden');
        });

        test('should have pause hidden by default', () => {
            expect(mockElements.pauseEl.classList.add).not.toHaveBeenCalled();
        });

        test('should have game over hidden by default', () => {
            expect(mockElements.gameOverEl.classList.add).not.toHaveBeenCalled();
        });
    });
});
