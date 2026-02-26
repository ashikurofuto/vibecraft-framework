import { Asteroid } from '../../domain/entities/Asteroid.js';
import { Vector2D } from '../../domain/value-objects/Vector2D.js';
import { CollisionBox } from '../../domain/value-objects/CollisionBox.js';

describe('Asteroid', () => {
    test('should create large asteroid', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'large');
        expect(asteroid.size).toBe('large');
        expect(asteroid.getCollisionBox().radius).toBe(60);
    });

    test('should create medium asteroid', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'medium');
        expect(asteroid.size).toBe('medium');
        expect(asteroid.getCollisionBox().radius).toBe(30);
    });

    test('should create small asteroid', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'small');
        expect(asteroid.size).toBe('small');
        expect(asteroid.getCollisionBox().radius).toBe(15);
    });

    test('should create asteroid with random velocity', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'large');
        expect(asteroid.velocity).toBeInstanceOf(Vector2D);
    });

    test('should update position over time', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'large');
        const initialPos = new Vector2D(asteroid.position.x, asteroid.position.y);
        asteroid.update(1 / 60);
        expect(asteroid.position.x).not.toBe(initialPos.x);
        expect(asteroid.position.y).not.toBe(initialPos.y);
    });

    test('should split large into 2 medium', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'large');
        const children = asteroid.split();
        expect(children.length).toBe(2);
        expect(children[0].size).toBe('medium');
        expect(children[1].size).toBe('medium');
    });

    test('should split medium into 2 small', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'medium');
        const children = asteroid.split();
        expect(children.length).toBe(2);
        expect(children[0].size).toBe('small');
        expect(children[1].size).toBe('small');
    });

    test('should not split small', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'small');
        const children = asteroid.split();
        expect(children.length).toBe(0);
    });

    test('should return points based on size - large', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'large');
        expect(asteroid.getPoints()).toBe(20);
    });

    test('should return points based on size - medium', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'medium');
        expect(asteroid.getPoints()).toBe(50);
    });

    test('should return points based on size - small', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'small');
        expect(asteroid.getPoints()).toBe(100);
    });

    test('should return collision box', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'large');
        const box = asteroid.getCollisionBox();
        expect(box).toBeInstanceOf(CollisionBox);
    });
});
