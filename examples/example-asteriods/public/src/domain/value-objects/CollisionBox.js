import { Vector2D } from './Vector2D.js';

/**
 * Хитбокс для обнаружения столкновений
 */
export class CollisionBox {
    constructor(center, radius) {
        this.center = center;
        this.radius = radius;
    }

    contains(point) {
        const distance = Vector2D.distance(this.center, point);
        return distance <= this.radius;
    }

    intersects(other) {
        const distance = Vector2D.distance(this.center, other.center);
        return distance <= (this.radius + other.radius);
    }
}
