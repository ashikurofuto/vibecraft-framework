/**
 * Asteroids Game — Main Entry Point
 * @description Инициализирует все компоненты игры и запускает игровой цикл
 */

import { Game } from './application/Game.js';
import { GameLoop } from './application/GameLoop.js';
import { Renderer } from './presentation/Renderer.js';
import { InputHandler } from './presentation/InputHandler.js';
import { UIController } from './presentation/UIController.js';
import { Storage } from './infrastructure/Storage.js';
import { AudioController } from './infrastructure/AudioController.js';

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
    // Get canvas
    const canvas = document.getElementById('game-canvas');

    // Create components
    const renderer = new Renderer(canvas);
    const inputHandler = new InputHandler(window);
    const storage = new Storage();
    const audioController = new AudioController();
    const uiController = new UIController(document);

    // Create game
    const game = new Game(renderer, inputHandler, storage, audioController);

    // Create game loop
    let lastTime = 0;
    let accumulator = 0;
    const fixedTimestep = 1 / 60;
    let isRunning = false;
    let animationFrameId = null;

    // Game loop function
    function gameLoop(currentTime) {
        if (!isRunning) return;

        // Calculate delta time in seconds
        let deltaTime = (currentTime - lastTime) / 1000;
        lastTime = currentTime;

        // Cap delta time to prevent spiral of death
        if (deltaTime > 0.25) {
            deltaTime = 0.25;
        }

        accumulator += deltaTime;

        // Update with fixed timestep
        const maxUpdates = 4;
        let updates = 0;
        while (accumulator >= fixedTimestep && updates < maxUpdates) {
            // Handle input
            const input = {
                thrust: inputHandler.isPressed('ArrowUp') || inputHandler.isPressed('KeyW'),
                rotate: inputHandler.isPressed('ArrowLeft') || inputHandler.isPressed('KeyA')
                    ? -1
                    : inputHandler.isPressed('ArrowRight') || inputHandler.isPressed('KeyD')
                        ? 1
                        : 0,
                fire: inputHandler.isPressed('Space'),
                pause: inputHandler.isPressed('KeyP'),
                hyperspace: inputHandler.isPressed('KeyH')
            };

            // Update game state
            game.handleInput(input);
            game.update(fixedTimestep);

            accumulator -= fixedTimestep;
            updates++;
        }

        // Render
        game.render();

        // Update UI
        updateUI();

        // End input frame
        inputHandler.endFrame();

        // Request next frame
        animationFrameId = requestAnimationFrame(gameLoop);
    }

    // Update UI elements
    function updateUI() {
        const gameState = game.getState();
        if (gameState) {
            uiController.updateScore(game.getScore());
            uiController.updateLives(game.getLives());
            uiController.updateLevel(game.getLevel());
            uiController.updateHighScore(game.getHighScore());

            // Handle screen visibility based on game state
            if (gameState.isMenu()) {
                uiController.showMenu();
            } else if (gameState.isPaused()) {
                uiController.showPause();
            } else if (gameState.isGameOver()) {
                uiController.showGameOver(game.getScore());
            } else if (gameState.isPlaying()) {
                uiController.hideAllScreens();
            }
        }
    }

    // Start game handler
    function startGame() {
        game.initialize();
        game.start();
        isRunning = true;
        lastTime = performance.now();
        animationFrameId = requestAnimationFrame(gameLoop);
    }

    // Setup UI buttons
    const startButton = document.getElementById('start-button');
    const restartButton = document.getElementById('restart-button');

    if (startButton) {
        startButton.addEventListener('click', () => {
            uiController.hideMenu();
            startGame();
        });
    }

    if (restartButton) {
        restartButton.addEventListener('click', () => {
            uiController.hideGameOver();
            startGame();
        });
    }

    // Register callbacks with UIController
    uiController.onStart(startGame);
    uiController.onRestart(startGame);

    // Initialize UI
    uiController.showMenu();
    uiController.updateHighScore(storage.getHighScore());

    // Handle keyboard shortcuts
    window.addEventListener('keydown', (e) => {
        if (e.code === 'KeyP') {
            // Pause toggle
            if (game.getState() && game.getState().isPlaying()) {
                game.pause();
            }
        }
    });

    // Expose game instance for debugging
    window.game = game;
});
