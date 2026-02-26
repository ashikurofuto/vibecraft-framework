/**
 * Renderer — компонент рендеринга графики через Canvas 2D API
 * @module Renderer
 * @description Оптимизирован для минимизации save/restore вызовов
 */

export class Renderer {
    /**
     * Создаёт рендерер
     * @param {HTMLCanvasElement} canvas - Canvas элемент для отрисовки
     */
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = canvas.width;
        this.height = canvas.height;

        // ✅ Кэшируем стили для уменьшения повторных установок
        this._cachedStyle = {
            strokeStyle: '#FFFFFF',
            fillStyle: '#000000',
            lineWidth: 2
        };
    }

    /**
     * Получение canvas элемента
     * @returns {HTMLCanvasElement}
     */
    getCanvas() {
        return this.canvas;
    }

    /**
     * Рендерит игровое состояние
     * @param {Object} gameState - Объект с игровыми сущностями
     * @param {Object|null} gameState.ship - Корабль игрока
     * @param {Array} gameState.asteroids - Массив астероидов
     * @param {Array} gameState.bullets - Массив пуль
     * @param {Array} gameState.ufos - Массив НЛО
     */
    render(gameState) {
        const { ctx, width, height } = this;
        const { ship, asteroids, bullets, ufos } = gameState;

        // ✅ Очистка canvas чёрным фоном (один вызов)
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, width, height);

        // ✅ Базовые настройки ОДИН раз для всех объектов
        ctx.strokeStyle = this._cachedStyle.strokeStyle;
        ctx.lineWidth = this._cachedStyle.lineWidth;

        // Отрисовка сущностей (без save/restore для простых объектов)
        if (ship) {
            this.drawShipFast(ship);
        }
        
        // ✅ Пакетная отрисовка астероидов
        for (let i = 0; i < asteroids.length; i++) {
            this.drawAsteroidFast(asteroids[i]);
        }
        
        // ✅ Пакетная отрисовка пуль
        for (let i = 0; i < bullets.length; i++) {
            this.drawBullet(bullets[i]);
        }
        
        // ✅ Пакетная отрисовка НЛО (с одним save/restore для всех)
        if (ufos.length > 0) {
            ctx.save();
            for (let i = 0; i < ufos.length; i++) {
                this.drawUFO(ufos[i]);
            }
            ctx.restore();
        }
    }

    /**
     * Быстрая отрисовка корабля
     * @param {Object} ship - Объект корабля
     * @private
     */
    drawShipFast(ship) {
        const { ctx } = this;
        const vertices = ship.getVertices();

        ctx.beginPath();
        ctx.moveTo(ship.position.x + vertices[0].x, ship.position.y + vertices[0].y);
        ctx.lineTo(ship.position.x + vertices[1].x, ship.position.y + vertices[1].y);
        ctx.lineTo(ship.position.x + vertices[2].x, ship.position.y + vertices[2].y);
        ctx.closePath();
        ctx.stroke();

        // Рисуем пламя тяги если нужно
        if (ship.isThrusting) {
            this.#drawThrustFlame(ship.position);
        }
    }

    /**
     * Отрисовка корабля (публичный метод для тестов)
     * @param {Object} ship - Объект корабля
     */
    drawShip(ship) {
        this.drawShipFast(ship);
    }

    /**
     * Отрисовка пламени тяги
     * @param {{x: number, y: number}} position - Позиция корабля
     * @private
     */
    #drawThrustFlame(position) {
        const { ctx } = this;
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        ctx.moveTo(position.x - 5, position.y + 15);
        ctx.lineTo(position.x, position.y + 25 + Math.random() * 5);
        ctx.lineTo(position.x + 5, position.y + 15);
        ctx.closePath();
        ctx.fill();
    }

    /**
     * Быстрая отрисовка астероида
     * @param {Object} asteroid - Объект астероида
     * @private
     */
    drawAsteroidFast(asteroid) {
        const { ctx } = this;
        const vertices = asteroid.getVertices();

        ctx.beginPath();
        ctx.moveTo(asteroid.position.x + vertices[0].x, asteroid.position.y + vertices[0].y);
        for (let i = 1; i < vertices.length; i++) {
            ctx.lineTo(asteroid.position.x + vertices[i].x, asteroid.position.y + vertices[i].y);
        }
        ctx.closePath();
        ctx.stroke();
    }

    /**
     * Отрисовка астероида (публичный метод для тестов)
     * @param {Object} asteroid - Объект астероида
     */
    drawAsteroid(asteroid) {
        const { ctx } = this;
        const vertices = asteroid.getVertices();

        ctx.save();
        ctx.translate(asteroid.position.x, asteroid.position.y);

        ctx.beginPath();
        ctx.moveTo(vertices[0].x, vertices[0].y);
        for (let i = 1; i < vertices.length; i++) {
            ctx.lineTo(vertices[i].x, vertices[i].y);
        }
        ctx.closePath();
        ctx.stroke();

        ctx.restore();
    }

    /**
     * Отрисовывает пулю
     * @param {Object} bullet - Объект пули
     * @param {Object} bullet.position - Позиция пули {x, y}
     * @param {Object} bullet.direction - Направление пули {x, y}
     */
    drawBullet(bullet) {
        const { ctx } = this;

        ctx.beginPath();
        ctx.moveTo(bullet.position.x, bullet.position.y);
        ctx.lineTo(
            bullet.position.x - bullet.direction.x * 10,
            bullet.position.y - bullet.direction.y * 10
        );
        ctx.stroke();
    }

    /**
     * Отрисовывает НЛО
     * @param {Object} ufo - Объект НЛО
     * @param {Object} ufo.position - Позиция НЛО {x, y}
     */
    drawUFO(ufo) {
        const { ctx } = this;

        ctx.save();
        ctx.translate(ufo.position.x, ufo.position.y);

        // Рисуем купол
        ctx.beginPath();
        ctx.arc(0, -5, 15, Math.PI, 0);
        ctx.stroke();

        // Рисуем основание
        ctx.beginPath();
        ctx.ellipse(0, 5, 25, 8, 0, 0, Math.PI * 2);
        ctx.stroke();

        ctx.restore();
    }

    /**
     * Отрисовывает взрыв
     * @param {Object} position - Позиция взрыва {x, y}
     */
    drawExplosion(position) {
        const { ctx } = this;
        const lines = 12;

        ctx.save();
        ctx.translate(position.x, position.y);

        for (let i = 0; i < lines; i++) {
            const angle = (i / lines) * Math.PI * 2;
            const length = 10 + Math.random() * 10;

            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(
                Math.cos(angle) * length,
                Math.sin(angle) * length
            );
            ctx.stroke();
        }

        ctx.restore();
    }
}
