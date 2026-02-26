import { Vector2D } from '../../domain/value-objects/Vector2D.js';

describe('Vector2D', () => {
    test('should create vector with x and y', () => {
        const v = new Vector2D(3, 4);
        expect(v.x).toBe(3);
        expect(v.y).toBe(4);
    });

    test('should add two vectors', () => {
        const v1 = new Vector2D(1, 2);
        const v2 = new Vector2D(3, 4);
        const result = v1.add(v2);
        expect(result.x).toBe(4);
        expect(result.y).toBe(6);
    });

    test('should subtract two vectors', () => {
        const v1 = new Vector2D(5, 7);
        const v2 = new Vector2D(2, 3);
        const result = v1.subtract(v2);
        expect(result.x).toBe(3);
        expect(result.y).toBe(4);
    });

    test('should multiply vector by scalar', () => {
        const v = new Vector2D(2, 3);
        const result = v.multiply(3);
        expect(result.x).toBe(6);
        expect(result.y).toBe(9);
    });

    test('should calculate magnitude', () => {
        const v = new Vector2D(3, 4);
        expect(v.magnitude()).toBe(5);
    });

    test('should normalize vector', () => {
        const v = new Vector2D(3, 4);
        const normalized = v.normalize();
        expect(normalized.magnitude()).toBeCloseTo(1);
    });

    test('should normalize zero vector to zero vector', () => {
        const v = new Vector2D(0, 0);
        const normalized = v.normalize();
        expect(normalized.x).toBe(0);
        expect(normalized.y).toBe(0);
    });

    test('should calculate distance between vectors', () => {
        const v1 = new Vector2D(0, 0);
        const v2 = new Vector2D(3, 4);
        expect(Vector2D.distance(v1, v2)).toBe(5);
    });
});
