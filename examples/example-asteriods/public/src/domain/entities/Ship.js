import { Vector2D } from '../value-objects/Vector2D.js';
import { CollisionBox } from '../value-objects/CollisionBox.js';
import { Bullet } from './Bullet.js';

/**
 * Корабль игрока
 * @description Оптимизирован для минимизации аллокаций памяти
 */
export class Ship {
    constructor(x, y) {
        this.position = new Vector2D(x, y);
        this.velocity = new Vector2D(0, 0);
        this.rotation = 0;
        this.rotationSpeed = 3; // radians per second
        this.thrustPower = 50; // pixels per second squared
        this.radius = 15;
        this._collisionBox = null;
        this.isThrusting = false;
    }

    rotate(direction) {
        // direction: -1 = counter-clockwise (positive), 1 = clockwise (negative)
        this.rotation += direction * this.rotationSpeed * (1/60) * -1;
    }

    thrust() {
        // Корабль смотрит вверх при rotation = 0
        // В Canvas Y растёт вниз, поэтому для движения вверх нужно вычитать
        // Добавляем -PI/2 чтобы 0 radians = вверх
        const angle = this.rotation - Math.PI / 2;
        const cos = Math.cos(angle);
        const sin = Math.sin(angle);
        this.velocity.x += cos * this.thrustPower * (1/60);
        this.velocity.y += sin * this.thrustPower * (1/60);
        this.isThrusting = true;
    }

    update(deltaTime) {
        // ✅ Inline операция — избегаем создания промежуточных векторов
        this.position.x += this.velocity.x * deltaTime;
        this.position.y += this.velocity.y * deltaTime;
        this.isThrusting = false;
    }

    applyFriction(coefficient) {
        // ✅ Inline операция — избегаем создания промежуточного вектора
        this.velocity.x *= coefficient;
        this.velocity.y *= coefficient;
    }

    wrapPosition(screenWidth, screenHeight) {
        if (this.position.x < 0) {
            this.position.x = screenWidth + this.position.x;
        } else if (this.position.x > screenWidth) {
            this.position.x = this.position.x - screenWidth;
        }

        if (this.position.y < 0) {
            this.position.y = screenHeight + this.position.y;
        } else if (this.position.y > screenHeight) {
            this.position.y = this.position.y - screenHeight;
        }
    }

    getCollisionBox() {
        // ✅ Кэшируем CollisionBox для уменьшения аллокаций
        if (!this._collisionBox) {
            this._collisionBox = new CollisionBox(this.position, this.radius);
        } else {
            this._collisionBox.center = this.position;
        }
        return this._collisionBox;
    }

    /**
     * Получение вершин треугольника корабля для отрисовки
     * @returns {Array<{x: number, y: number}>}
     */
    getVertices() {
        const size = this.radius;
        // Вершины треугольника: нос направлен вверх (отрицательный Y)
        const nose = { x: 0, y: -size };
        const leftWing = { x: -size * 0.6, y: size * 0.8 };
        const rightWing = { x: size * 0.6, y: size * 0.8 };

        // Поворот вершин
        const cos = Math.cos(this.rotation);
        const sin = Math.sin(this.rotation);

        return [
            { x: nose.x * cos - nose.y * sin, y: nose.x * sin + nose.y * cos },
            { x: leftWing.x * cos - leftWing.y * sin, y: leftWing.x * sin + leftWing.y * cos },
            { x: rightWing.x * cos - rightWing.y * sin, y: rightWing.x * sin + rightWing.y * cos }
        ];
    }

    fire() {
        // Пуля летит в том же направлении, куда смотрит корабль (вверх при rotation = 0)
        const angle = this.rotation - Math.PI / 2;
        const cos = Math.cos(angle);
        const sin = Math.sin(angle);
        const bulletVelocity = new Vector2D(cos * 300, sin * 300);
        const bulletPosition = new Vector2D(
            this.position.x + cos * 20,
            this.position.y + sin * 20
        );
        return new Bullet(bulletPosition, bulletVelocity);
    }
}
