import { Vector2D } from '../value-objects/Vector2D.js';
import { CollisionBox } from '../value-objects/CollisionBox.js';

/**
 * Лазерная пуля
 * @description Оптимизирован для минимизации аллокаций памяти
 */
export class Bullet {
    constructor(position, velocity) {
        this.position = position;
        this.velocity = velocity;
        this.lifetime = 2;
        this.age = 0;
        this.isAlive = true;
        this.radius = 5; // ✅ 5px — реалистичный размер пули для игр (было 50px)
        this._collisionBox = null;
    }

    update(deltaTime) {
        this.age += deltaTime;
        if (this.age >= this.lifetime) {
            this.isAlive = false;
            return;
        }

        // ✅ Inline операция — избегаем создания промежуточных векторов
        this.position.x += this.velocity.x * deltaTime;
        this.position.y += this.velocity.y * deltaTime;
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
     * Получение направления пули для отрисовки
     * @returns {{x: number, y: number}}
     */
    get direction() {
        const magnitude = Math.sqrt(this.velocity.x ** 2 + this.velocity.y ** 2);
        if (magnitude === 0) {
            return { x: 0, y: -1 };
        }
        return {
            x: this.velocity.x / magnitude,
            y: this.velocity.y / magnitude
        };
    }
}
