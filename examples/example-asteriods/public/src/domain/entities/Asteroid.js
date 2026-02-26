import { Vector2D } from '../value-objects/Vector2D.js';
import { CollisionBox } from '../value-objects/CollisionBox.js';

/**
 * Астероид
 * @description Оптимизирован для минимизации аллокаций памяти
 */
export class Asteroid {
    constructor(position, size) {
        this.position = position;
        this.size = size;
        this.velocity = this.#generateRandomVelocity();
        this.radius = this.#getRadiusForSize(size);
        this._collisionBox = null;
    }

    #getRadiusForSize(size) {
        switch (size) {
            case 'large': return 60;
            case 'medium': return 30;
            case 'small': return 15;
            default: return 30;
        }
    }

    #generateRandomVelocity() {
        const speed = 50;
        const angle = Math.random() * Math.PI * 2;
        return new Vector2D(
            Math.cos(angle) * speed,
            Math.sin(angle) * speed
        );
    }

    update(deltaTime) {
        // ✅ Inline операция — избегаем создания промежуточных векторов
        this.position.x += this.velocity.x * deltaTime;
        this.position.y += this.velocity.y * deltaTime;
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

    split() {
        if (this.size === 'small') {
            return [];
        }

        const newSize = this.size === 'large' ? 'medium' : 'small';
        const children = [];

        for (let i = 0; i < 2; i++) {
            // ✅ Передаём ту же позицию без создания промежуточных векторов
            const child = new Asteroid(new Vector2D(this.position.x, this.position.y), newSize);
            children.push(child);
        }

        return children;
    }

    getPoints() {
        switch (this.size) {
            case 'large': return 20;
            case 'medium': return 50;
            case 'small': return 100;
            default: return 0;
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
     * Получение вершин многоугольника астероида для отрисовки
     * @returns {Array<{x: number, y: number}>}
     */
    getVertices() {
        const vertices = [];
        const sides = this.size === 'large' ? 12 : (this.size === 'medium' ? 10 : 8);
        const irregularity = 0.3; // Насколько форма неправильная

        for (let i = 0; i < sides; i++) {
            const angle = (i / sides) * Math.PI * 2;
            // Добавляем случайные отклонения для неправильной формы
            const radiusVariation = 1 + (Math.sin(angle * 3) + Math.cos(angle * 5)) * irregularity * 0.5;
            const radius = this.radius * radiusVariation;

            vertices.push({
                x: Math.cos(angle) * radius,
                y: Math.sin(angle) * radius
            });
        }

        return vertices;
    }
}
