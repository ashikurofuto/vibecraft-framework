import { Vector2D } from '../value-objects/Vector2D.js';
import { CollisionBox } from '../value-objects/CollisionBox.js';
import { Bullet } from './Bullet.js';

/**
 * НЛО (тарелка)
 */
export class UFO {
    constructor(position, pattern) {
        this.position = position;
        this.pattern = pattern;
        this.velocity = this.#generateRandomVelocity();
        this.radius = this.#getRadiusForPattern(pattern);
        this.shootCooldown = 0;
        this.fireInterval = this.#getFireInterval();
    }

    #getRadiusForPattern(pattern) {
        return pattern === 'large' ? 50 : 35;
    }

    #getFireInterval() {
        return this.pattern === 'large' ? 3 : 1.5;
    }

    #generateRandomVelocity() {
        const speed = this.pattern === 'large' ? 30 : 60;
        const angle = Math.random() * Math.PI * 2;
        return new Vector2D(
            Math.cos(angle) * speed,
            Math.sin(angle) * speed
        );
    }

    update(deltaTime) {
        const displacement = this.velocity.multiply(deltaTime);
        this.position = this.position.add(displacement);

        if (this.shootCooldown > 0) {
            this.shootCooldown -= deltaTime;
        }
    }

    tryFire() {
        if (this.shootCooldown > 0) {
            return null;
        }

        this.shootCooldown = this.fireInterval;

        const direction = new Vector2D(0, 1);
        const bulletVelocity = direction.multiply(200);
        const bulletPosition = new Vector2D(
            this.position.x,
            this.position.y + this.radius
        );

        return new Bullet(bulletPosition, bulletVelocity);
    }

    getPoints() {
        return this.pattern === 'large' ? 200 : 1000;
    }

    getCollisionBox() {
        return new CollisionBox(this.position, this.radius);
    }
}
