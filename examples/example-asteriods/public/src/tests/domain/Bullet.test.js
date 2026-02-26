import { Bullet } from '../../domain/entities/Bullet.js';
import { Vector2D } from '../../domain/value-objects/Vector2D.js';
import { CollisionBox } from '../../domain/value-objects/CollisionBox.js';

describe('Bullet', () => {
    test('should create bullet at position', () => {
        const pos = new Vector2D(100, 100);
        const vel = new Vector2D(0, -400);
        const bullet = new Bullet(pos, vel);
        expect(bullet.position).toEqual(pos);
    });

    test('should create bullet with given velocity', () => {
        const pos = new Vector2D(100, 100);
        const vel = new Vector2D(0, -400);
        const bullet = new Bullet(pos, vel);
        expect(bullet.velocity).toEqual(vel);
    });

    test('should create bullet alive', () => {
        const pos = new Vector2D(100, 100);
        const vel = new Vector2D(0, -400);
        const bullet = new Bullet(pos, vel);
        expect(bullet.isAlive).toBe(true);
    });

    test('should update position over time', () => {
        const bullet = new Bullet(new Vector2D(0, 0), new Vector2D(0, -400));
        bullet.update(1 / 60);
        expect(bullet.position.y).toBeLessThan(0);
    });

    test('should die after lifetime', () => {
        const bullet = new Bullet(new Vector2D(0, 0), new Vector2D(0, -400));
        bullet.update(2.1);
        expect(bullet.isAlive).toBe(false);
    });

    test('should stay alive before lifetime expires', () => {
        const bullet = new Bullet(new Vector2D(0, 0), new Vector2D(0, -400));
        bullet.update(1);
        expect(bullet.isAlive).toBe(true);
    });

    test('should return collision box', () => {
        const bullet = new Bullet(new Vector2D(0, 0), new Vector2D(0, -400));
        const box = bullet.getCollisionBox();
        expect(box).toBeInstanceOf(CollisionBox);
    });
});
