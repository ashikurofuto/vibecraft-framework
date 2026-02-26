import { UFO } from '../../domain/entities/UFO.js';
import { Vector2D } from '../../domain/value-objects/Vector2D.js';
import { CollisionBox } from '../../domain/value-objects/CollisionBox.js';
import { Bullet } from '../../domain/entities/Bullet.js';

describe('UFO', () => {
    test('should create large UFO', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'large');
        expect(ufo.pattern).toBe('large');
    });

    test('should create small UFO', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'small');
        expect(ufo.pattern).toBe('small');
    });

    test('should create UFO with random velocity', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'large');
        expect(ufo.velocity).toBeInstanceOf(Vector2D);
    });

    test('should update position over time', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'large');
        const initialPos = new Vector2D(ufo.position.x, ufo.position.y);
        ufo.update(1 / 60);
        expect(ufo.position.x).not.toBe(initialPos.x);
        expect(ufo.position.y).not.toBe(initialPos.y);
    });

    test('should try to fire when cooldown ready', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'small');
        const bullet = ufo.tryFire();
        expect(bullet).toBeInstanceOf(Bullet);
    });

    test('should not fire when cooldown not ready', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'small');
        ufo.tryFire();
        const bullet2 = ufo.tryFire();
        expect(bullet2).toBeNull();
    });

    test('should return collision box', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'large');
        const box = ufo.getCollisionBox();
        expect(box).toBeInstanceOf(CollisionBox);
    });

    test('should return points based on type - large', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'large');
        expect(ufo.getPoints()).toBe(200);
    });

    test('should return points based on type - small', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'small');
        expect(ufo.getPoints()).toBe(1000);
    });
});
