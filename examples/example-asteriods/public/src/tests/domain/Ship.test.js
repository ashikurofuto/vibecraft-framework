import { Ship } from '../../domain/entities/Ship.js';
import { Vector2D } from '../../domain/value-objects/Vector2D.js';
import { CollisionBox } from '../../domain/value-objects/CollisionBox.js';
import { Bullet } from '../../domain/entities/Bullet.js';

describe('Ship', () => {
    test('should create ship at center', () => {
        const ship = new Ship(400, 300);
        expect(ship.position.x).toBe(400);
        expect(ship.position.y).toBe(300);
    });

    test('should create ship with zero velocity', () => {
        const ship = new Ship(400, 300);
        expect(ship.velocity.x).toBe(0);
        expect(ship.velocity.y).toBe(0);
    });

    test('should create ship with zero rotation', () => {
        const ship = new Ship(400, 300);
        expect(ship.rotation).toBe(0);
    });

    test('should rotate left (counter-clockwise)', () => {
        const ship = new Ship(400, 300);
        ship.rotate(-1);
        // ✅ Новая логика: -1 = counter-clockwise = положительное вращение
        expect(ship.rotation).toBeGreaterThan(0);
    });

    test('should rotate right (clockwise)', () => {
        const ship = new Ship(400, 300);
        ship.rotate(1);
        // ✅ Новая логика: 1 = clockwise = отрицательное вращение
        expect(ship.rotation).toBeLessThan(0);
    });

    test('should thrust forward', () => {
        const ship = new Ship(400, 300);
        ship.thrust();
        // ✅ При rotation = 0 корабль смотрит вверх, thrust даёт скорость вверх
        expect(ship.velocity.magnitude()).toBeGreaterThan(0);
    });

    test('should update position based on velocity', () => {
        const ship = new Ship(400, 300);
        // ✅ Устанавливаем ненулевую скорость напрямую для теста
        ship.velocity.x = 100;
        ship.velocity.y = 50;
        const initialPos = new Vector2D(ship.position.x, ship.position.y);
        ship.update(1 / 60);
        expect(ship.position.x).not.toBe(initialPos.x);
        expect(ship.position.y).not.toBe(initialPos.y);
    });

    test('should apply friction', () => {
        const ship = new Ship(400, 300);
        ship.thrust();
        const initialVelocity = ship.velocity.magnitude();
        ship.applyFriction(0.99);
        expect(ship.velocity.magnitude()).toBeLessThan(initialVelocity);
    });

    test('should wrap position when off screen (left edge)', () => {
        const ship = new Ship(400, 300);
        ship.position.x = -10;
        ship.wrapPosition(800, 600);
        expect(ship.position.x).toBe(790);
    });

    test('should wrap position when off screen (right edge)', () => {
        const ship = new Ship(400, 300);
        ship.position.x = 810;
        ship.wrapPosition(800, 600);
        expect(ship.position.x).toBe(10);
    });

    test('should wrap position when off screen (top edge)', () => {
        const ship = new Ship(400, 300);
        ship.position.y = -10;
        ship.wrapPosition(800, 600);
        expect(ship.position.y).toBe(590);
    });

    test('should wrap position when off screen (bottom edge)', () => {
        const ship = new Ship(400, 300);
        ship.position.y = 610;
        ship.wrapPosition(800, 600);
        expect(ship.position.y).toBe(10);
    });

    test('should return collision box', () => {
        const ship = new Ship(400, 300);
        const box = ship.getCollisionBox();
        expect(box).toBeInstanceOf(CollisionBox);
    });

    test('should fire bullet', () => {
        const ship = new Ship(400, 300);
        const bullet = ship.fire();
        expect(bullet).toBeInstanceOf(Bullet);
    });

    test('should fire bullet in direction of ship rotation', () => {
        const ship = new Ship(400, 300);
        ship.rotation = -Math.PI / 2; // pointing up
        const bullet = ship.fire();
        expect(bullet.velocity.y).toBeLessThan(0);
    });
});
