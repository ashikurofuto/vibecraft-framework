/**
 * Пространственная сетка для оптимизации обнаружения коллизий
 * @description Разбивает пространство на ячейки для уменьшения количества проверок коллизий
 * с O(n×m) до O(n) в среднем случае
 */
export class SpatialGrid {
    /**
     * @param {number} cellSize - размер ячейки сетки (пиксели)
     * @param {number} screenWidth - ширина экрана
     * @param {number} screenHeight - высота экрана
     */
    constructor(cellSize = 100, screenWidth = 800, screenHeight = 600) {
        this.cellSize = cellSize;
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;
        this.grid = new Map();
    }

    /**
     * Очистка сетки
     */
    clear() {
        this.grid.clear();
    }

    /**
     * Получение ключа ячейки по координатам
     * @param {number} x
     * @param {number} y
     * @returns {string}
     * @private
     */
    #getCellKey(x, y) {
        const cellX = Math.floor(x / this.cellSize);
        const cellY = Math.floor(y / this.cellSize);
        return `${cellX},${cellY}`;
    }

    /**
     * Вставка сущности в сетку
     * @param {Object} entity - сущность с position и radius свойствами
     */
    insert(entity) {
        const key = this.#getCellKey(entity.position.x, entity.position.y);

        if (!this.grid.has(key)) {
            this.grid.set(key, []);
        }
        this.grid.get(key).push(entity);
    }

    /**
     * Вставка массива сущностей
     * @param {Array} entities
     */
    insertAll(entities) {
        for (const entity of entities) {
            this.insert(entity);
        }
    }

    /**
     * Получение сущностей из ячейки
     * @param {number} cellX
     * @param {number} cellY
     * @returns {Array}
     * @private
     */
    #getCell(cellX, cellY) {
        const key = `${cellX},${cellY}`;
        return this.grid.get(key) || [];
    }

    /**
     * Получение всех сущностей из соседних ячеек (3×3 grid)
     * @param {Object} entity - сущность для которой ищем соседей
     * @returns {Array}
     */
    query(entity) {
        const cellX = Math.floor(entity.position.x / this.cellSize);
        const cellY = Math.floor(entity.position.y / this.cellSize);
        const nearby = [];

        // Проверяем только соседние ячейки (включая текущую)
        for (let dx = -1; dx <= 1; dx++) {
            for (let dy = -1; dy <= 1; dy++) {
                const cell = this.#getCell(cellX + dx, cellY + dy);
                nearby.push(...cell);
            }
        }

        return nearby;
    }

    /**
     * Быстрая проверка коллизий между сущностями одного типа
     * @param {Array} entities - массив сущностей
     * @param {Function} collisionFn - функция проверки коллизии между двумя сущностями
     * @returns {Array}
     */
    checkCollisions(entities, collisionFn) {
        this.clear();
        this.insertAll(entities);

        const collisions = [];
        const checked = new Set();

        for (const entity of entities) {
            const nearby = this.query(entity);

            for (const other of nearby) {
                if (entity === other) continue;

                // Создаём уникальный ключ для пары
                const pairKey = entity.id < other.id
                    ? `${entity.id}-${other.id}`
                    : `${other.id}-${entity.id}`;

                if (checked.has(pairKey)) continue;
                checked.add(pairKey);

                const collision = collisionFn(entity, other);
                if (collision) {
                    collisions.push(collision);
                }
            }
        }

        return collisions;
    }

    /**
     * Быстрая проверка коллизий между двумя группами сущностей
     * @param {Array} groupA - первая группа сущностей
     * @param {Array} groupB - вторая группа сущностей
     * @param {Function} collisionFn - функция проверки коллизии между двумя сущностями
     * @returns {Array}
     */
    checkGroupCollisions(groupA, groupB, collisionFn) {
        this.clear();
        this.insertAll(groupA);
        this.insertAll(groupB);

        const collisions = [];

        for (const entityA of groupA) {
            const nearby = this.query(entityA);

            for (const entityB of nearby) {
                // Проверяем что entityB из groupB и это не тот же объект
                if (!groupB.includes(entityB) || entityA === entityB) continue;

                const collision = collisionFn(entityA, entityB);
                if (collision) {
                    collisions.push(collision);
                }
            }
        }

        return collisions;
    }

    /**
     * Отладка — отрисовка сетки
     * @param {CanvasRenderingContext2D} ctx
     */
    debugDraw(ctx) {
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = 1;

        for (let x = 0; x < this.screenWidth; x += this.cellSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, this.screenHeight);
            ctx.stroke();
        }

        for (let y = 0; y < this.screenHeight; y += this.cellSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(this.screenWidth, y);
            ctx.stroke();
        }
    }

    /**
     * Количество заполненных ячеек
     * @returns {number}
     */
    get occupiedCellCount() {
        return this.grid.size;
    }

    /**
     * Общее количество сущностей в сетке
     * @returns {number}
     */
    get entityCount() {
        let count = 0;
        for (const entities of this.grid.values()) {
            count += entities.length;
        }
        return count;
    }
}
