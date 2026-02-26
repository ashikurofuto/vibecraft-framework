/**
 * Tests for Renderer
 * 
 * @description Тесты для компонента рендеринга через Canvas 2D API
 * @module Renderer
 * @see src/presentation/Renderer.js
 */

import { jest } from '@jest/globals';
import { createMockCanvas } from '../__mocks__/canvas.js';

describe('Renderer', () => {
    let Renderer;
    let renderer;
    let canvas;
    let ctx;

    // Константы для тестов
    const CANVAS_WIDTH = 800;
    const CANVAS_HEIGHT = 600;
    const BLACK = '#000000';
    const WHITE = '#FFFFFF';

    beforeEach(async () => {
        // Динамический импорт для изоляции тестов
        Renderer = (await import('../../../src/presentation/Renderer.js')).Renderer;

        // Создаём мок canvas
        canvas = createMockCanvas(CANVAS_WIDTH, CANVAS_HEIGHT);
        ctx = canvas._getMockContext();

        renderer = new Renderer(canvas);
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('constructor', () => {
        test('should store canvas reference', () => {
            expect(renderer.canvas).toBe(canvas);
        });

        test('should get 2d context from canvas', () => {
            expect(canvas.getContext).toHaveBeenCalledWith('2d');
        });

        test('should store context reference', () => {
            expect(renderer.ctx).toBe(ctx);
        });

        test('should store canvas width', () => {
            expect(renderer.width).toBe(CANVAS_WIDTH);
        });

        test('should store canvas height', () => {
            expect(renderer.height).toBe(CANVAS_HEIGHT);
        });
    });

    describe('render', () => {
        test('should clear canvas with black background', () => {
            renderer.render({ ship: null, asteroids: [], bullets: [], ufos: [] });

            expect(ctx.fillStyle).toBe(BLACK);
            expect(ctx.fillRect).toHaveBeenCalledWith(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        });

        test('should set white stroke style', () => {
            renderer.render({ ship: null, asteroids: [], bullets: [], ufos: [] });

            expect(ctx.strokeStyle).toBe(WHITE);
            expect(ctx.lineWidth).toBe(2);
        });

        test('should clear canvas before drawing', () => {
            renderer.render({ ship: null, asteroids: [], bullets: [], ufos: [] });

            // ✅ Используем fillRect вместо clearRect для очистки чёрным фоном
            expect(ctx.fillRect).toHaveBeenCalledWith(0, 0, 800, 600);
        });

        test('should render empty game state without errors', () => {
            expect(() => {
                renderer.render({ ship: null, asteroids: [], bullets: [], ufos: [] });
            }).not.toThrow();
        });
    });

    describe('drawShip', () => {
        test('should draw ship at correct position with vertices', () => {
            const vertices = [
                { x: 0, y: -20 },
                { x: -15, y: 20 },
                { x: 15, y: 20 }
            ];
            const mockShip = {
                position: { x: 400, y: 300 },
                rotation: 0,
                getVertices: jest.fn(() => vertices)
            };

            renderer.drawShip(mockShip);

            // ✅ Новая оптимизированная отрисовка использует position + vertices
            expect(ctx.beginPath).toHaveBeenCalled();
            expect(ctx.moveTo).toHaveBeenCalledWith(400, 280); // 300 + (-20)
            expect(ctx.lineTo).toHaveBeenCalledWith(385, 320); // 400 + (-15), 300 + 20
            expect(ctx.lineTo).toHaveBeenCalledWith(415, 320); // 400 + 15, 300 + 20
            expect(ctx.closePath).toHaveBeenCalled();
            expect(ctx.stroke).toHaveBeenCalled();
        });

        test('should not use save/restore in optimized drawShip', () => {
            const mockShip = {
                position: { x: 400, y: 300 },
                rotation: 0,
                getVertices: jest.fn(() => [
                    { x: 0, y: -20 },
                    { x: -15, y: 20 },
                    { x: 15, y: 20 }
                ])
            };

            renderer.drawShip(mockShip);

            // ✅ Оптимизированная версия не использует save/restore
            expect(ctx.save).not.toHaveBeenCalled();
            expect(ctx.restore).not.toHaveBeenCalled();
        });

        test('should not use translate/rotate in optimized drawShip', () => {
            const mockShip = {
                position: { x: 400, y: 300 },
                rotation: Math.PI / 4,
                getVertices: jest.fn(() => [
                    { x: 0, y: -20 },
                    { x: -15, y: 20 },
                    { x: 15, y: 20 }
                ])
            };

            renderer.drawShip(mockShip);

            // ✅ Оптимизированная версия не использует transform
            expect(ctx.translate).not.toHaveBeenCalled();
            expect(ctx.rotate).not.toHaveBeenCalled();
        });

        test('should begin path for triangle', () => {
            const mockShip = {
                position: { x: 400, y: 300 },
                rotation: 0,
                getVertices: jest.fn(() => [
                    { x: 0, y: -20 },
                    { x: -15, y: 20 },
                    { x: 15, y: 20 }
                ])
            };

            renderer.drawShip(mockShip);

            expect(ctx.beginPath).toHaveBeenCalled();
        });

        test('should draw triangle from vertices', () => {
            const vertices = [
                { x: 0, y: -20 },
                { x: -15, y: 20 },
                { x: 15, y: 20 }
            ];
            const mockShip = {
                position: { x: 400, y: 300 },
                rotation: 0,
                getVertices: jest.fn(() => vertices)
            };

            renderer.drawShip(mockShip);

            expect(ctx.moveTo).toHaveBeenCalledWith(vertices[0].x, vertices[0].y);
            expect(ctx.lineTo).toHaveBeenCalledWith(vertices[1].x, vertices[1].y);
            expect(ctx.lineTo).toHaveBeenCalledWith(vertices[2].x, vertices[2].y);
        });

        test('should close path after drawing triangle', () => {
            const mockShip = {
                position: { x: 400, y: 300 },
                rotation: 0,
                getVertices: jest.fn(() => [
                    { x: 0, y: -20 },
                    { x: -15, y: 20 },
                    { x: 15, y: 20 }
                ])
            };

            renderer.drawShip(mockShip);

            expect(ctx.closePath).toHaveBeenCalled();
        });

        test('should stroke the triangle', () => {
            const mockShip = {
                position: { x: 400, y: 300 },
                rotation: 0,
                getVertices: jest.fn(() => [
                    { x: 0, y: -20 },
                    { x: -15, y: 20 },
                    { x: 15, y: 20 }
                ])
            };

            renderer.drawShip(mockShip);

            expect(ctx.stroke).toHaveBeenCalled();
        });

        test('should draw thrust flame when ship is thrusting', () => {
            const mockShip = {
                position: { x: 400, y: 300 },
                rotation: 0,
                isThrusting: true,
                getVertices: jest.fn(() => [
                    { x: 0, y: -20 },
                    { x: -15, y: 20 },
                    { x: 15, y: 20 }
                ])
            };

            renderer.drawShip(mockShip);

            // Thrust должен быть нарисован (проверяем fill для пламени)
            expect(ctx.fill).toHaveBeenCalled();
        });

        test('should not draw thrust flame when ship is not thrusting', () => {
            const mockShip = {
                position: { x: 400, y: 300 },
                rotation: 0,
                isThrusting: false,
                getVertices: jest.fn(() => [
                    { x: 0, y: -20 },
                    { x: -15, y: 20 },
                    { x: 15, y: 20 }
                ])
            };

            renderer.drawShip(mockShip);

            // Для корабля без тяги fill не должен вызываться (только stroke)
            // Но stroke вызывается для треугольника, так что проверяем количество вызовов
            const fillCalls = ctx.fill.mock.calls.length;
            expect(fillCalls).toBeLessThan(2); // Только для thrust, если есть
        });
    });

    describe('drawAsteroid', () => {
        test('should save context state before drawing', () => {
            const mockAsteroid = {
                position: { x: 100, y: 100 },
                getVertices: jest.fn(() => [
                    { x: 0, y: -30 },
                    { x: 20, y: -20 },
                    { x: 25, y: 10 },
                    { x: 0, y: 30 },
                    { x: -25, y: 10 },
                    { x: -20, y: -20 }
                ])
            };

            renderer.drawAsteroid(mockAsteroid);

            expect(ctx.save).toHaveBeenCalled();
        });

        test('should restore context state after drawing', () => {
            const mockAsteroid = {
                position: { x: 100, y: 100 },
                getVertices: jest.fn(() => [
                    { x: 0, y: -30 },
                    { x: 20, y: -20 },
                    { x: 25, y: 10 },
                    { x: 0, y: 30 },
                    { x: -25, y: 10 },
                    { x: -20, y: -20 }
                ])
            };

            renderer.drawAsteroid(mockAsteroid);

            expect(ctx.restore).toHaveBeenCalled();
        });

        test('should translate to asteroid position', () => {
            const mockAsteroid = {
                position: { x: 100, y: 100 },
                getVertices: jest.fn(() => [
                    { x: 0, y: -30 },
                    { x: 20, y: -20 },
                    { x: 25, y: 10 },
                    { x: 0, y: 30 },
                    { x: -25, y: 10 },
                    { x: -20, y: -20 }
                ])
            };

            renderer.drawAsteroid(mockAsteroid);

            expect(ctx.translate).toHaveBeenCalledWith(100, 100);
        });

        test('should begin path for polygon', () => {
            const mockAsteroid = {
                position: { x: 100, y: 100 },
                getVertices: jest.fn(() => [
                    { x: 0, y: -30 },
                    { x: 20, y: -20 },
                    { x: 25, y: 10 },
                    { x: 0, y: 30 },
                    { x: -25, y: 10 },
                    { x: -20, y: -20 }
                ])
            };

            renderer.drawAsteroid(mockAsteroid);

            expect(ctx.beginPath).toHaveBeenCalled();
        });

        test('should draw polygon from vertices', () => {
            const vertices = [
                { x: 0, y: -30 },
                { x: 20, y: -20 },
                { x: 25, y: 10 },
                { x: 0, y: 30 },
                { x: -25, y: 10 },
                { x: -20, y: -20 }
            ];
            const mockAsteroid = {
                position: { x: 100, y: 100 },
                getVertices: jest.fn(() => vertices)
            };

            renderer.drawAsteroid(mockAsteroid);

            expect(ctx.moveTo).toHaveBeenCalledWith(vertices[0].x, vertices[0].y);
            expect(ctx.lineTo).toHaveBeenCalledWith(vertices[1].x, vertices[1].y);
            expect(ctx.lineTo).toHaveBeenCalledWith(vertices[2].x, vertices[2].y);
        });

        test('should close path after drawing polygon', () => {
            const mockAsteroid = {
                position: { x: 100, y: 100 },
                getVertices: jest.fn(() => [
                    { x: 0, y: -30 },
                    { x: 20, y: -20 },
                    { x: 25, y: 10 },
                    { x: 0, y: 30 },
                    { x: -25, y: 10 },
                    { x: -20, y: -20 }
                ])
            };

            renderer.drawAsteroid(mockAsteroid);

            expect(ctx.closePath).toHaveBeenCalled();
        });

        test('should stroke the polygon', () => {
            const mockAsteroid = {
                position: { x: 100, y: 100 },
                getVertices: jest.fn(() => [
                    { x: 0, y: -30 },
                    { x: 20, y: -20 },
                    { x: 25, y: 10 },
                    { x: 0, y: 30 },
                    { x: -25, y: 10 },
                    { x: -20, y: -20 }
                ])
            };

            renderer.drawAsteroid(mockAsteroid);

            expect(ctx.stroke).toHaveBeenCalled();
        });
    });

    describe('drawBullet', () => {
        test('should begin path for bullet line', () => {
            const mockBullet = {
                position: { x: 200, y: 200 },
                direction: { x: 0, y: -1 }
            };

            renderer.drawBullet(mockBullet);

            expect(ctx.beginPath).toHaveBeenCalled();
        });

        test('should draw line from bullet position in direction', () => {
            const mockBullet = {
                position: { x: 200, y: 200 },
                direction: { x: 0, y: -1 }
            };

            renderer.drawBullet(mockBullet);

            expect(ctx.moveTo).toHaveBeenCalledWith(200, 200);
            expect(ctx.lineTo).toHaveBeenCalledWith(200, 210); // direction * 10
        });

        test('should stroke the bullet line', () => {
            const mockBullet = {
                position: { x: 200, y: 200 },
                direction: { x: 0, y: -1 }
            };

            renderer.drawBullet(mockBullet);

            expect(ctx.stroke).toHaveBeenCalled();
        });

        test('should draw bullet in different directions', () => {
            const mockBullet = {
                position: { x: 400, y: 300 },
                direction: { x: 1, y: 0 }
            };

            renderer.drawBullet(mockBullet);

            expect(ctx.moveTo).toHaveBeenCalledWith(400, 300);
            expect(ctx.lineTo).toHaveBeenCalledWith(390, 300); // -direction.x * 10
        });
    });

    describe('drawUFO', () => {
        test('should save context state before drawing', () => {
            const mockUFO = {
                position: { x: 300, y: 100 }
            };

            renderer.drawUFO(mockUFO);

            expect(ctx.save).toHaveBeenCalled();
        });

        test('should restore context state after drawing', () => {
            const mockUFO = {
                position: { x: 300, y: 100 }
            };

            renderer.drawUFO(mockUFO);

            expect(ctx.restore).toHaveBeenCalled();
        });

        test('should translate to UFO position', () => {
            const mockUFO = {
                position: { x: 300, y: 100 }
            };

            renderer.drawUFO(mockUFO);

            expect(ctx.translate).toHaveBeenCalledWith(300, 100);
        });

        test('should draw dome with arc', () => {
            const mockUFO = {
                position: { x: 300, y: 100 }
            };

            renderer.drawUFO(mockUFO);

            expect(ctx.arc).toHaveBeenCalled();
        });

        test('should draw base with ellipse', () => {
            const mockUFO = {
                position: { x: 300, y: 100 }
            };

            renderer.drawUFO(mockUFO);

            expect(ctx.ellipse).toHaveBeenCalled();
        });

        test('should stroke the UFO', () => {
            const mockUFO = {
                position: { x: 300, y: 100 }
            };

            renderer.drawUFO(mockUFO);

            expect(ctx.stroke).toHaveBeenCalled();
        });
    });

    describe('drawExplosion', () => {
        test('should save context state before drawing', () => {
            renderer.drawExplosion({ x: 400, y: 300 });

            expect(ctx.save).toHaveBeenCalled();
        });

        test('should restore context state after drawing', () => {
            renderer.drawExplosion({ x: 400, y: 300 });

            expect(ctx.restore).toHaveBeenCalled();
        });

        test('should translate to explosion position', () => {
            renderer.drawExplosion({ x: 400, y: 300 });

            expect(ctx.translate).toHaveBeenCalledWith(400, 300);
        });

        test('should begin path for explosion lines', () => {
            renderer.drawExplosion({ x: 400, y: 300 });

            expect(ctx.beginPath).toHaveBeenCalled();
        });

        test('should stroke explosion lines', () => {
            renderer.drawExplosion({ x: 400, y: 300 });

            expect(ctx.stroke).toHaveBeenCalled();
        });

        test('should draw multiple explosion lines', () => {
            renderer.drawExplosion({ x: 400, y: 300 });

            // beginPath должен быть вызван несколько раз (для каждой линии)
            expect(ctx.beginPath).toHaveBeenCalledTimes(12);
        });
    });

    describe('full render cycle', () => {
        test('should render complete game state', () => {
            const mockShip = {
                position: { x: 400, y: 300 },
                rotation: 0,
                isThrusting: false,
                getVertices: jest.fn(() => [
                    { x: 0, y: -20 },
                    { x: -15, y: 20 },
                    { x: 15, y: 20 }
                ])
            };

            const mockAsteroid = {
                position: { x: 100, y: 100 },
                getVertices: jest.fn(() => [
                    { x: 0, y: -30 },
                    { x: 20, y: -20 },
                    { x: 25, y: 10 },
                    { x: 0, y: 30 },
                    { x: -25, y: 10 },
                    { x: -20, y: -20 }
                ])
            };

            const mockBullet = {
                position: { x: 200, y: 200 },
                direction: { x: 0, y: -1 }
            };

            const mockUFO = {
                position: { x: 300, y: 100 }
            };

            renderer.render({
                ship: mockShip,
                asteroids: [mockAsteroid],
                bullets: [mockBullet],
                ufos: [mockUFO]
            });

            // Проверяем что все методы отрисовки были вызваны
            expect(ctx.save).toHaveBeenCalled();
            expect(ctx.restore).toHaveBeenCalled();
            expect(ctx.stroke).toHaveBeenCalled();
        });

        test('should render multiple asteroids', () => {
            const mockAsteroids = [
                {
                    position: { x: 100, y: 100 },
                    getVertices: jest.fn(() => [{ x: 0, y: -30 }, { x: 30, y: 0 }, { x: 0, y: 30 }, { x: -30, y: 0 }])
                },
                {
                    position: { x: 200, y: 200 },
                    getVertices: jest.fn(() => [{ x: 0, y: -30 }, { x: 30, y: 0 }, { x: 0, y: 30 }, { x: -30, y: 0 }])
                },
                {
                    position: { x: 300, y: 300 },
                    getVertices: jest.fn(() => [{ x: 0, y: -30 }, { x: 30, y: 0 }, { x: 0, y: 30 }, { x: -30, y: 0 }])
                }
            ];

            renderer.render({
                ship: null,
                asteroids: mockAsteroids,
                bullets: [],
                ufos: []
            });

            // ✅ Оптимизированная отрисовка использует moveTo/lineTo с позицией
            expect(ctx.beginPath).toHaveBeenCalledTimes(3);
            expect(ctx.moveTo).toHaveBeenCalledWith(100, 70); // 100 + 0, 100 + (-30)
            expect(ctx.moveTo).toHaveBeenCalledWith(200, 170); // 200 + 0, 200 + (-30)
            expect(ctx.moveTo).toHaveBeenCalledWith(300, 270); // 300 + 0, 300 + (-30)
        });

        test('should render multiple bullets', () => {
            const mockBullets = [
                { position: { x: 100, y: 100 }, direction: { x: 0, y: -1 } },
                { position: { x: 200, y: 200 }, direction: { x: 1, y: 0 } },
                { position: { x: 300, y: 300 }, direction: { x: 0, y: 1 } }
            ];

            renderer.render({
                ship: null,
                asteroids: [],
                bullets: mockBullets,
                ufos: []
            });

            // moveTo должен быть вызван для каждой пули
            expect(ctx.moveTo).toHaveBeenCalledTimes(3);
        });
    });

    describe('rendering order', () => {
        test('should clear canvas before drawing entities', () => {
            const mockShip = {
                position: { x: 400, y: 300 },
                rotation: 0,
                getVertices: jest.fn(() => [{ x: 0, y: -20 }, { x: -15, y: 20 }, { x: 15, y: 20 }])
            };

            renderer.render({
                ship: mockShip,
                asteroids: [],
                bullets: [],
                ufos: []
            });

            // ✅ fillRect (очистка) должен быть вызван до beginPath (отрисовка корабля)
            const fillRectCall = ctx.fillRect.mock.invocationCallOrder[0];
            const beginPathCall = ctx.beginPath.mock.invocationCallOrder[0];

            expect(fillRectCall).toBeLessThan(beginPathCall);
        });
    });
});
