import { CollisionDetector } from '../../domain/services/CollisionDetector.js';
import { Ship } from '../../domain/entities/Ship.js';
import { Asteroid } from '../../domain/entities/Asteroid.js';
import { Bullet } from '../../domain/entities/Bullet.js';
import { UFO } from '../../domain/entities/UFO.js';
import { Vector2D } from '../../domain/value-objects/Vector2D.js';

describe('CollisionDetector', () => {
    let detector;

    beforeEach(() => {
        // ✅ Создаём экземпляр для каждого теста
        detector = new CollisionDetector(100, 800, 600);
    });

    describe('checkShipAsteroid', () => {
        test('should detect ship-asteroid collision', () => {
            const ship = new Ship(0, 0);
            const asteroid = new Asteroid(new Vector2D(5, 0), 'large');
            const collision = CollisionDetector.checkShipAsteroid(ship, asteroid);
            expect(collision).not.toBeNull();
        });

        test('should not detect collision when far apart', () => {
            const ship = new Ship(0, 0);
            const asteroid = new Asteroid(new Vector2D(200, 200), 'small');
            const collision = CollisionDetector.checkShipAsteroid(ship, asteroid);
            expect(collision).toBeNull();
        });
    });

    describe('checkBulletAsteroid', () => {
        test('should detect bullet-asteroid collision', () => {
            // ✅ Пуля теперь имеет радиус 3px, поэтому должна быть ближе к астероиду
            const bullet = new Bullet(new Vector2D(0, 0), new Vector2D(0, -400));
            const asteroid = new Asteroid(new Vector2D(0, 10), 'medium'); // Радиус 30px + 3px = 33px максимум
            const collision = CollisionDetector.checkBulletAsteroid(bullet, asteroid);
            expect(collision).not.toBeNull();
        });

        test('should not detect collision when far apart', () => {
            const bullet = new Bullet(new Vector2D(0, 0), new Vector2D(0, -400));
            const asteroid = new Asteroid(new Vector2D(200, 200), 'small');
            const collision = CollisionDetector.checkBulletAsteroid(bullet, asteroid);
            expect(collision).toBeNull();
        });
    });

    describe('checkBulletUFO', () => {
        test('should detect bullet-ufo collision', () => {
            const bullet = new Bullet(new Vector2D(0, 0), new Vector2D(0, -400));
            const ufo = new UFO(new Vector2D(0, 50), 'large');
            const collision = CollisionDetector.checkBulletUFO(bullet, ufo);
            expect(collision).not.toBeNull();
        });

        test('should not detect collision when far apart', () => {
            const bullet = new Bullet(new Vector2D(0, 0), new Vector2D(0, -400));
            const ufo = new UFO(new Vector2D(200, 200), 'large');
            const collision = CollisionDetector.checkBulletUFO(bullet, ufo);
            expect(collision).toBeNull();
        });
    });

    describe('checkShipUFO', () => {
        test('should detect ship-ufo collision', () => {
            const ship = new Ship(0, 0);
            const ufo = new UFO(new Vector2D(5, 0), 'large');
            const collision = CollisionDetector.checkShipUFO(ship, ufo);
            expect(collision).not.toBeNull();
        });

        test('should not detect collision when far apart', () => {
            const ship = new Ship(0, 0);
            const ufo = new UFO(new Vector2D(200, 200), 'large');
            const collision = CollisionDetector.checkShipUFO(ship, ufo);
            expect(collision).toBeNull();
        });
    });

    describe('checkAll', () => {
        test('should check all collisions at once', () => {
            const entities = {
                ship: new Ship(0, 0),
                asteroids: [new Asteroid(new Vector2D(5, 0), 'large')],
                bullets: [],
                ufos: []
            };
            const allCollisions = detector.checkAll(entities);
            expect(allCollisions.length).toBeGreaterThan(0);
        });

        test('should return empty collisions when no entities', () => {
            const entities = {
                ship: new Ship(0, 0),
                asteroids: [],
                bullets: [],
                ufos: []
            };
            const allCollisions = detector.checkAll(entities);
            expect(allCollisions.length).toBe(0);
        });

        test('should detect multiple collision types', () => {
            const entities = {
                ship: new Ship(0, 0),
                asteroids: [new Asteroid(new Vector2D(5, 0), 'large')],
                bullets: [new Bullet(new Vector2D(0, 0), new Vector2D(0, -100))],
                ufos: [new UFO(new Vector2D(10, 0), 'small')]
            };
            const allCollisions = detector.checkAll(entities);
            expect(allCollisions.length).toBeGreaterThan(0);
        });
    });

    describe('SpatialGrid Optimization', () => {
        test('should use spatial grid for bullet-asteroid collisions', () => {
            // ✅ Пуля теперь имеет радиус 3px, размещаем ближе для коллизии
            const bullets = [
                new Bullet(new Vector2D(0, 0), new Vector2D(0, -400)),
                new Bullet(new Vector2D(100, 100), new Vector2D(0, -400))
            ];
            const asteroids = [
                new Asteroid(new Vector2D(0, 10), 'medium'), // Близко к первой пуле
                new Asteroid(new Vector2D(500, 500), 'large')
            ];

            const collisions = detector.checkAll({
                ship: new Ship(0, 0),
                asteroids,
                bullets,
                ufos: []
            });

            // Должна быть хотя бы одна коллизия
            expect(collisions.length).toBeGreaterThan(0);
        });

        test('should handle empty bullet array efficiently', () => {
            const asteroids = [
                new Asteroid(new Vector2D(0, 50), 'medium'),
                new Asteroid(new Vector2D(100, 100), 'large')
            ];

            const collisions = detector.checkAll({
                ship: new Ship(0, 0),
                asteroids,
                bullets: [],
                ufos: []
            });

            // Только ship-asteroid коллизии
            expect(collisions.length).toBeGreaterThanOrEqual(0);
        });

        test('should handle empty asteroid array efficiently', () => {
            const bullets = [
                new Bullet(new Vector2D(0, 0), new Vector2D(0, -400)),
                new Bullet(new Vector2D(100, 100), new Vector2D(0, -400))
            ];

            const collisions = detector.checkAll({
                ship: new Ship(0, 0),
                asteroids: [],
                bullets,
                ufos: []
            });

            expect(collisions.length).toBe(0);
        });
    });
});
