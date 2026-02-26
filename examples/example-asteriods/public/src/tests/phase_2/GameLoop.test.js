import { jest } from '@jest/globals';
import { GameLoop } from '../../application/GameLoop.js';

describe('GameLoop', () => {
    let gameLoop;
    let mockUpdate;
    let mockRender;

    beforeEach(() => {
        mockUpdate = jest.fn();
        mockRender = jest.fn();
        gameLoop = new GameLoop(mockUpdate, mockRender);
    });

    afterEach(() => {
        if (gameLoop.isRunning) {
            gameLoop.stop();
        }
    });

    describe('Initialization', () => {
        test('should create game loop with callbacks', () => {
            expect(gameLoop.updateCallback).toBe(mockUpdate);
            expect(gameLoop.renderCallback).toBe(mockRender);
        });

        test('should not be running initially', () => {
            expect(gameLoop.isRunning).toBe(false);
        });

        test('should have zero accumulator initially', () => {
            expect(gameLoop.accumulator).toBe(0);
        });

        test('should have fixed timestep of 1/60', () => {
            expect(gameLoop.fixedTimestep).toBe(1 / 60);
        });

        test('should have zero lastTime initially', () => {
            expect(gameLoop.lastTime).toBe(0);
        });
    });

    describe('Start/Stop', () => {
        test('should start loop', () => {
            gameLoop.start();
            expect(gameLoop.isRunning).toBe(true);
        });

        test('should set lastTime on start', () => {
            gameLoop.start();
            expect(gameLoop.lastTime).toBeGreaterThan(0);
        });

        test('should stop loop', () => {
            gameLoop.start();
            gameLoop.stop();
            expect(gameLoop.isRunning).toBe(false);
        });

        test('should cancel animation frame on stop', () => {
            gameLoop.start();
            const initialFrameId = gameLoop.animationFrameId;
            gameLoop.stop();
            expect(gameLoop.animationFrameId).toBe(null);
        });
    });

    describe('Tick and Update', () => {
        test('should call update with fixed timestep', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            expect(mockUpdate).toHaveBeenCalledWith(1 / 60);
        });

        test('should call update once for small delta time', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            expect(mockUpdate).toHaveBeenCalledTimes(1);
        });

        test('should accumulate time for multiple updates', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            // First tick consumes 1/60 sec, remaining ~0.033 sec
            // Second tick with 50ms delta should accumulate enough for 3 updates
            gameLoop.tick(1000 + 50);
            expect(mockUpdate).toHaveBeenCalledTimes(4); // 1 + 3
        });

        test('should subtract fixed timestep after each update', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            // After one update, accumulator should be reduced
            expect(gameLoop.accumulator).toBeLessThan(gameLoop.fixedTimestep);
        });

        test('should handle large delta time with spiral of death prevention', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            // 1 second delta - should be capped at 0.25 sec
            gameLoop.tick(2000);
            // Should not have too many updates due to cap
            expect(mockUpdate).toHaveBeenCalledTimes(16); // 0.25 / (1/60) = 15
        });

        test('should not update when not running', () => {
            gameLoop.tick(1000);
            expect(mockUpdate).not.toHaveBeenCalled();
        });
    });

    describe('Render', () => {
        test('should call render after updates', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            expect(mockRender).toHaveBeenCalled();
        });

        test('should call render once per tick', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            gameLoop.tick(1016);
            expect(mockRender).toHaveBeenCalledTimes(2);
        });

        test('should call render even if no updates needed', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            // Very small delta - not enough for update
            gameLoop.tick(1001);
            expect(mockRender).toHaveBeenCalledTimes(2);
        });

        test('should not render when not running', () => {
            gameLoop.tick(1000);
            expect(mockRender).not.toHaveBeenCalled();
        });
    });

    describe('Fixed Timestep', () => {
        test('should use 1/60 second fixed timestep', () => {
            expect(gameLoop.fixedTimestep).toBeCloseTo(0.0166667, 4);
        });

        test('should call update exactly 60 times per second with perfect timing', () => {
            gameLoop.start();
            let currentTime = 1000;
            for (let i = 0; i < 60; i++) {
                currentTime += 16.6667; // ~1/60 sec
                gameLoop.tick(currentTime);
            }
            expect(mockUpdate).toHaveBeenCalledTimes(61); // +1 from start
        });

        test('should handle variable frame rates', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            gameLoop.tick(1008); // 8ms
            gameLoop.tick(1025); // 17ms
            gameLoop.tick(1033); // 8ms
            // Should maintain consistent updates despite variable deltas
            expect(mockUpdate).toHaveBeenCalledTimes(4);
        });
    });

    describe('Accumulator Pattern', () => {
        test('should accumulate delta time', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            const accumulatorAfterFirst = gameLoop.accumulator;
            gameLoop.tick(1008);
            expect(gameLoop.accumulator).toBeGreaterThan(accumulatorAfterFirst);
        });

        test('should reset accumulator after update', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            // Accumulator should be less than fixed timestep after update
            expect(gameLoop.accumulator).toBeLessThan(gameLoop.fixedTimestep);
        });

        test('should carry over remaining accumulator', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            const remaining = gameLoop.accumulator;
            gameLoop.tick(1008);
            // Remaining time should carry over
            expect(gameLoop.accumulator).toBeGreaterThanOrEqual(remaining);
        });
    });

    describe('Animation Frame', () => {
        test('should request animation frame on tick', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            expect(gameLoop.animationFrameId).toBeDefined();
        });

        test('should have valid animation frame ID', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            expect(typeof gameLoop.animationFrameId).toBe('number');
            expect(gameLoop.animationFrameId).toBeGreaterThan(0);
        });
    });

    describe('Edge Cases', () => {
        test('should handle zero delta time', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            gameLoop.tick(1000); // Zero delta
            expect(mockUpdate).toHaveBeenCalledTimes(1);
        });

        test('should handle negative delta time gracefully', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            gameLoop.tick(900); // Negative delta
            // Should not crash
            expect(gameLoop.isRunning).toBe(true);
        });

        test('should handle very small delta time', () => {
            gameLoop.start();
            gameLoop.tick(1000);
            gameLoop.tick(1000.001); // 0.001ms
            expect(mockUpdate).toHaveBeenCalledTimes(1);
        });

        test('should handle multiple start calls', () => {
            gameLoop.start();
            gameLoop.start();
            expect(gameLoop.isRunning).toBe(true);
        });

        test('should handle multiple stop calls', () => {
            gameLoop.start();
            gameLoop.stop();
            gameLoop.stop();
            expect(gameLoop.isRunning).toBe(false);
        });
    });

    describe('Callback Execution Order', () => {
        test('should call update before render', () => {
            const callOrder = [];
            mockUpdate.mockImplementation(() => callOrder.push('update'));
            mockRender.mockImplementation(() => callOrder.push('render'));
            
            gameLoop.start();
            gameLoop.tick(1000);
            
            expect(callOrder).toEqual(['update', 'render']);
        });

        test('should call all updates before render for accumulated time', () => {
            const callOrder = [];
            mockUpdate.mockImplementation(() => callOrder.push('update'));
            mockRender.mockImplementation(() => callOrder.push('render'));
            
            gameLoop.start();
            gameLoop.tick(1000);
            gameLoop.tick(1050); // Enough for 3 updates
            
            // All updates should come before render
            const renderIndex = callOrder.lastIndexOf('render');
            const lastUpdateIndex = callOrder.lastIndexOf('update');
            expect(lastUpdateIndex).toBeLessThan(renderIndex);
        });
    });
});
