import { Bullet } from '../domain/entities/Bullet.js';
import { Vector2D } from '../domain/value-objects/Vector2D.js';

/**
 * Object Pool для пуль
 * @description Переиспользует объекты Bullet для минимизации GC пауз
 * @implements ADR-007: Object Pooling for Bullets and Asteroids
 */
export class BulletPool {
    /**
     * @param {number} size - размер пула (максимальное количество пуль)
     */
    constructor(size = 50) {
        this.pool = [];
        this.available = new Set();
        
        // Инициализируем пул
        for (let i = 0; i < size; i++) {
            // Создаём пули с начальными координатами за пределами экрана
            const bullet = new Bullet(
                new Vector2D(-1000, -1000), // Начальная позиция за экраном
                new Vector2D(0, 0)           // Нулевая скорость
            );
            bullet.id = i;
            bullet.isAlive = false;
            this.pool.push(bullet);
            this.available.add(i);
        }
    }

    /**
     * Получение активной пули из пула
     * @param {Vector2D} position - позиция запуска
     * @param {Vector2D} velocity - скорость пули
     * @returns {Bullet|null} Пуля или null если пул исчерпан
     */
    acquire(position, velocity) {
        if (this.available.size === 0) {
            return null; // Пул исчерпан
        }

        // Получаем первый доступный индекс
        const id = this.available.values().next().value;
        this.available.delete(id);

        const bullet = this.pool[id];
        bullet.position.x = position.x;
        bullet.position.y = position.y;
        bullet.velocity.x = velocity.x;
        bullet.velocity.y = velocity.y;
        bullet.isAlive = true;
        bullet.age = 0; // Сброс времени жизни

        return bullet;
    }

    /**
     * Возврат пули в пул
     * @param {Bullet} bullet - пуля для возврата
     */
    release(bullet) {
        bullet.isAlive = false;
        bullet.position.x = -1000;
        bullet.position.y = -1000;
        bullet.velocity.x = 0;
        bullet.velocity.y = 0;
        bullet.age = 0;
        
        this.available.add(bullet.id);
    }

    /**
     * Получение всех активных пуль
     * @returns {Bullet[]}
     */
    getActive() {
        const active = [];
        for (const bullet of this.pool) {
            if (bullet.isAlive) {
                active.push(bullet);
            }
        }
        return active;
    }

    /**
     * Обновление всех активных пуль
     * @param {number} deltaTime - время в секундах
     */
    update(deltaTime) {
        for (const bullet of this.pool) {
            if (bullet.isAlive) {
                bullet.update(deltaTime);
                
                // Автоматическое удаление по времени жизни
                if (!bullet.isAlive) {
                    this.release(bullet);
                }
            }
        }
    }

    /**
     * Сброс всех пуль в пул
     */
    reset() {
        for (const bullet of this.pool) {
            bullet.isAlive = false;
            bullet.position.x = -1000;
            bullet.position.y = -1000;
        }
        this.available.clear();
        for (let i = 0; i < this.pool.length; i++) {
            this.available.add(i);
        }
    }

    /**
     * Количество активных пуль
     * @returns {number}
     */
    get activeCount() {
        return this.pool.length - this.available.size;
    }

    /**
     * Количество доступных пуль
     * @returns {number}
     */
    get availableCount() {
        return this.available.size;
    }
}
