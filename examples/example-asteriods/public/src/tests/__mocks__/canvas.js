/**
 * Mock для Canvas API
 * Используется в тестах Renderer
 */
import { jest } from '@jest/globals';

/**
 * Создаёт мок для CanvasRenderingContext2D
 * @returns {Object} Мок объекта контекста Canvas
 */
export function createMockCanvasContext() {
    return {
        // Transformations
        save: jest.fn(),
        restore: jest.fn(),
        translate: jest.fn(),
        rotate: jest.fn(),
        scale: jest.fn(),
        transform: jest.fn(),
        setTransform: jest.fn(),
        resetTransform: jest.fn(),

        // Drawing styles
        strokeStyle: '#000000',
        fillStyle: '#000000',
        lineWidth: 1,
        lineCap: 'butt',
        lineJoin: 'miter',
        miterLimit: 10,
        lineDashOffset: 0,
        globalAlpha: 1,
        globalCompositeOperation: 'source-over',

        setLineDash: jest.fn(),
        getLineDash: jest.fn(() => []),

        // Paths
        beginPath: jest.fn(),
        closePath: jest.fn(),
        moveTo: jest.fn(),
        lineTo: jest.fn(),
        bezierCurveTo: jest.fn(),
        quadraticCurveTo: jest.fn(),
        arc: jest.fn(),
        arcTo: jest.fn(),
        ellipse: jest.fn(),
        rect: jest.fn(),

        // Drawing
        fill: jest.fn(),
        stroke: jest.fn(),
        clip: jest.fn(),
        isPointInPath: jest.fn(() => false),
        isPointInStroke: jest.fn(() => false),

        // Clearing
        clearRect: jest.fn(),
        fillRect: jest.fn(),
        strokeRect: jest.fn(),
        fillText: jest.fn(),
        strokeText: jest.fn(),

        // Image data
        createImageData: jest.fn(),
        getImageData: jest.fn(),
        putImageData: jest.fn(),

        // Text
        font: '10px sans-serif',
        textAlign: 'start',
        textBaseline: 'alphabetic',
        direction: 'ltr',
        measureText: jest.fn(() => ({ width: 0, height: 0 })),

        // Canvas properties
        canvas: null
    };
}

/**
 * Создаёт мок для HTMLCanvasElement
 * @param {number} width - Ширина canvas
 * @param {number} height - Высота canvas
 * @returns {Object} Мок объекта Canvas
 */
export function createMockCanvas(width = 800, height = 600) {
    const ctx = createMockCanvasContext();

    return {
        width: width,
        height: height,
        getContext: jest.fn((type) => {
            if (type === '2d') {
                ctx.canvas = { width, height };
                return ctx;
            }
            return null;
        }),
        toDataURL: jest.fn(() => 'data:image/png;base64,mock'),
        toBlob: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),

        // Метод для получения контекста для проверок
        _getMockContext: () => ctx
    };
}

/**
 * Создаёт мок для OffscreenCanvas (для тестов без DOM)
 * @param {number} width - Ширина canvas
 * @param {number} height - Высота canvas
 * @returns {Object} Мок объекта OffscreenCanvas
 */
export function createMockOffscreenCanvas(width = 800, height = 600) {
    const ctx = createMockCanvasContext();

    return {
        width: width,
        height: height,
        getContext: jest.fn((type) => {
            if (type === '2d') {
                ctx.canvas = { width, height };
                return ctx;
            }
            return null;
        }),
        convertToBlob: jest.fn(),
        transferToImageBitmap: jest.fn(),

        // Метод для получения контекста для проверок
        _getMockContext: () => ctx
    };
}
