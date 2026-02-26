import { SpatialGrid } from './SpatialGrid.js';

/**
 * Сервис обнаружения столкновений
 * @description Оптимизирован с использованием SpatialGrid для уменьшения сложности
 * с O(n×m) до O(n) в среднем случае
 */
export class CollisionDetector {
    /**
     * @param {number} [cellSize=100] - размер ячейки spatial grid
     * @param {number} [screenWidth=800] - ширина экрана
     * @param {number} [screenHeight=600] - высота экрана
     */
    constructor(cellSize = 100, screenWidth = 800, screenHeight = 600) {
        this.spatialGrid = new SpatialGrid(cellSize, screenWidth, screenHeight);
    }

    static checkShipAsteroid(ship, asteroid) {
        const shipBox = ship.getCollisionBox();
        const asteroidBox = asteroid.getCollisionBox();

        if (shipBox.intersects(asteroidBox)) {
            return { type: 'ship-asteroid', ship, asteroid };
        }

        return null;
    }

    static checkBulletAsteroid(bullet, asteroid) {
        const bulletBox = bullet.getCollisionBox();
        const asteroidBox = asteroid.getCollisionBox();

        if (bulletBox.intersects(asteroidBox)) {
            return { type: 'bullet-asteroid', bullet, asteroid };
        }

        return null;
    }

    static checkBulletUFO(bullet, ufo) {
        const bulletBox = bullet.getCollisionBox();
        const ufoBox = ufo.getCollisionBox();

        if (bulletBox.intersects(ufoBox)) {
            return { type: 'bullet-ufo', bullet, ufo };
        }

        return null;
    }

    static checkShipUFO(ship, ufo) {
        const shipBox = ship.getCollisionBox();
        const ufoBox = ufo.getCollisionBox();

        if (shipBox.intersects(ufoBox)) {
            return { type: 'ship-ufo', ship, ufo };
        }

        return null;
    }

    /**
     * Проверка всех коллизий с использованием SpatialGrid
     * @param {Object} entities
     * @param {Object} entities.ship - корабль
     * @param {Array} entities.asteroids - массив астероидов
     * @param {Array} entities.bullets - массив пуль
     * @param {Array} entities.ufos - массив НЛО
     * @returns {Array}
     */
    checkAll(entities) {
        const collisions = [];
        const { ship, asteroids, bullets, ufos } = entities;

        // Ship vs Asteroids — простая проверка (всегда 1 астероид проверяется)
        for (const asteroid of asteroids) {
            const collision = CollisionDetector.checkShipAsteroid(ship, asteroid);
            if (collision) {
                collisions.push(collision);
            }
        }

        // Bullets vs Asteroids — используем SpatialGrid для оптимизации
        const bulletAsteroidCollisions = this.#checkBulletAsteroidsWithGrid(bullets, asteroids);
        collisions.push(...bulletAsteroidCollisions);

        // Bullets vs UFOs — используем SpatialGrid для оптимизации
        const bulletUfoCollisions = this.#checkBulletUfosWithGrid(bullets, ufos);
        collisions.push(...bulletUfoCollisions);

        // Ship vs UFOs — простая проверка
        for (const ufo of ufos) {
            const collision = CollisionDetector.checkShipUFO(ship, ufo);
            if (collision) {
                collisions.push(collision);
            }
        }

        return collisions;
    }

    /**
     * Оптимизированная проверка пуль с астероидами через SpatialGrid
     * @param {Array} bullets
     * @param {Array} asteroids
     * @returns {Array}
     * @private
     */
    #checkBulletAsteroidsWithGrid(bullets, asteroids) {
        if (bullets.length === 0 || asteroids.length === 0) {
            return [];
        }

        const collisions = [];
        this.spatialGrid.clear();
        this.spatialGrid.insertAll(asteroids);

        for (const bullet of bullets) {
            const nearbyAsteroids = this.spatialGrid.query(bullet);

            for (const asteroid of nearbyAsteroids) {
                const collision = CollisionDetector.checkBulletAsteroid(bullet, asteroid);
                if (collision) {
                    collisions.push(collision);
                    break; // Пуля попадает только в один астероид за раз
                }
            }
        }

        return collisions;
    }

    /**
     * Оптимизированная проверка пуль с НЛО через SpatialGrid
     * @param {Array} bullets
     * @param {Array} ufos
     * @returns {Array}
     * @private
     */
    #checkBulletUfosWithGrid(bullets, ufos) {
        if (bullets.length === 0 || ufos.length === 0) {
            return [];
        }

        const collisions = [];
        this.spatialGrid.clear();
        this.spatialGrid.insertAll(ufos);

        for (const bullet of bullets) {
            const nearbyUfos = this.spatialGrid.query(bullet);

            for (const ufo of nearbyUfos) {
                const collision = CollisionDetector.checkBulletUFO(bullet, ufo);
                if (collision) {
                    collisions.push(collision);
                    break; // Пуля попадает только в одно НЛО за раз
                }
            }
        }

        return collisions;
    }

    /**
     * Быстрая проверка коллизий между сущностями одного типа
     * @param {Array} entities
     * @param {Function} collisionFn
     * @returns {Array}
     */
    checkSameTypeCollisions(entities, collisionFn) {
        return this.spatialGrid.checkCollisions(entities, collisionFn);
    }

    /**
     * Отладка — отрисовка spatial grid
     * @param {CanvasRenderingContext2D} ctx
     */
    debugDraw(ctx) {
        this.spatialGrid.debugDraw(ctx);
    }
}
