/**
 * 2D вектор для работы с физикой
 * @description Оптимизирован для минимизации аллокаций памяти
 */
export class Vector2D {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }

    /**
     * Сложение векторов (создаёт новый объект)
     * @param {Vector2D} other
     * @returns {Vector2D}
     */
    add(other) {
        return new Vector2D(this.x + other.x, this.y + other.y);
    }

    /**
     * Вычитание векторов (создаёт новый объект)
     * @param {Vector2D} other
     * @returns {Vector2D}
     */
    subtract(other) {
        return new Vector2D(this.x - other.x, this.y - other.y);
    }

    /**
     * Умножение на скаляр (создаёт новый объект)
     * @param {number} scalar
     * @returns {Vector2D}
     */
    multiply(scalar) {
        return new Vector2D(this.x * scalar, this.y * scalar);
    }

    /**
     * Magnitude (длина вектора)
     * @returns {number}
     */
    magnitude() {
        return Math.sqrt(this.x ** 2 + this.y ** 2);
    }

    /**
     * Нормализация вектора (создаёт новый объект)
     * @returns {Vector2D}
     */
    normalize() {
        const mag = this.magnitude();
        if (mag === 0) return new Vector2D(0, 0);
        return new Vector2D(this.x / mag, this.y / mag);
    }

    /**
     * Расстояние между двумя векторами
     * @param {Vector2D} a
     * @param {Vector2D} b
     * @returns {number}
     */
    static distance(a, b) {
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    /**
     * Квадрат расстояния (без дорогого sqrt, для оптимизации коллизий)
     * @param {Vector2D} a
     * @param {Vector2D} b
     * @returns {number}
     */
    static distanceSquared(a, b) {
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        return dx * dx + dy * dy;
    }

    /**
     * Inline сложение — модифицирует текущий вектор (без аллокаций)
     * @param {Vector2D} other
     */
    addInline(other) {
        this.x += other.x;
        this.y += other.y;
    }

    /**
     * Inline вычитание — модифицирует текущий вектор (без аллокаций)
     * @param {Vector2D} other
     */
    subtractInline(other) {
        this.x -= other.x;
        this.y -= other.y;
    }

    /**
     * Inline умножение — модифицирует текущий вектор (без аллокаций)
     * @param {number} scalar
     */
    multiplyInline(scalar) {
        this.x *= scalar;
        this.y *= scalar;
    }

    /**
     * Копирование значений из другого вектора (без аллокаций)
     * @param {Vector2D} other
     */
    copyFrom(other) {
        this.x = other.x;
        this.y = other.y;
    }

    /**
     * Сброс вектора (без аллокаций)
     */
    reset() {
        this.x = 0;
        this.y = 0;
    }
}
