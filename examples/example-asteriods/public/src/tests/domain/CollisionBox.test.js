import { CollisionBox } from '../../domain/value-objects/CollisionBox.js';
import { Vector2D } from '../../domain/value-objects/Vector2D.js';

describe('CollisionBox', () => {
    test('should create collision box with center and radius', () => {
        const center = new Vector2D(10, 10);
        const box = new CollisionBox(center, 5);
        expect(box.center).toEqual(center);
        expect(box.radius).toBe(5);
    });

    test('should contain point inside', () => {
        const center = new Vector2D(0, 0);
        const box = new CollisionBox(center, 10);
        const point = new Vector2D(5, 5);
        expect(box.contains(point)).toBe(true);
    });

    test('should not contain point outside', () => {
        const center = new Vector2D(0, 0);
        const box = new CollisionBox(center, 5);
        const point = new Vector2D(10, 10);
        expect(box.contains(point)).toBe(false);
    });

    test('should contain point on edge', () => {
        const center = new Vector2D(0, 0);
        const box = new CollisionBox(center, 10);
        const point = new Vector2D(10, 0);
        expect(box.contains(point)).toBe(true);
    });

    test('should intersect with another box', () => {
        const box1 = new CollisionBox(new Vector2D(0, 0), 10);
        const box2 = new CollisionBox(new Vector2D(15, 0), 10);
        expect(box1.intersects(box2)).toBe(true);
    });

    test('should not intersect when far apart', () => {
        const box1 = new CollisionBox(new Vector2D(0, 0), 5);
        const box2 = new CollisionBox(new Vector2D(20, 0), 5);
        expect(box1.intersects(box2)).toBe(false);
    });

    test('should intersect when touching', () => {
        const box1 = new CollisionBox(new Vector2D(0, 0), 10);
        const box2 = new CollisionBox(new Vector2D(20, 0), 10);
        expect(box1.intersects(box2)).toBe(true);
    });
});
