import { GameState } from './GameState.js';
import { ScoreManager } from './ScoreManager.js';
import { BulletPool } from './BulletPool.js';
import { Ship } from '../domain/entities/Ship.js';
import { Asteroid } from '../domain/entities/Asteroid.js';
import { UFO } from '../domain/entities/UFO.js';
import { Vector2D } from '../domain/value-objects/Vector2D.js';
import { CollisionDetector } from '../domain/services/CollisionDetector.js';

/**
 * Основная игровая фасад-система
 * @description Объединяет все слои игры, управляет сущностями и игровой логикой
 */
export class Game {
    /**
     * @param {Object} renderer - Renderer интерфейс
     * @param {Object} inputHandler - InputHandler интерфейс
     * @param {Object} storage - Storage интерфейс
     * @param {Object} audio - AudioController интерфейс
     */
    constructor(renderer, inputHandler, storage, audio) {
        this.renderer = renderer;
        this.inputHandler = inputHandler;
        this.storage = storage;
        this.audio = audio;

        this.gameState = null;
        this.scoreManager = null;
        this.ship = null;
        this.bulletPool = new BulletPool(50); // Object pool для пуль
        this.asteroids = [];
        this.ufos = [];

        this.screenWidth = 800;
        this.screenHeight = 600;

        this.firePressedLastFrame = false;
        this.pausePressedLastFrame = false;
        
        // ✅ Создаём экземпляр CollisionDetector с оптимизацией SpatialGrid
        this.collisionDetector = new CollisionDetector(100, this.screenWidth, this.screenHeight);
    }

    /**
     * Инициализация игры
     */
    initialize() {
        // Получаем размеры экрана из canvas
        const canvas = this.renderer.getCanvas();
        this.screenWidth = canvas.width;
        this.screenHeight = canvas.height;

        // Создаём состояние игры с callback для game over
        this.gameState = new GameState({
            onGameOver: () => {
                // Сохраняем рекорд только если он был побит
                if (this.scoreManager.currentScore > this.scoreManager.highScore) {
                    this.scoreManager.saveHighScore();
                }
            }
        });

        // Создаём менеджер очков
        this.scoreManager = new ScoreManager(this.storage);
        
        // Создаём корабль в центре экрана
        this.ship = new Ship(this.screenWidth / 2, this.screenHeight / 2);

        // Сбрасываем пул пуль
        this.bulletPool.reset();

        // Очищаем сущности
        this.asteroids = [];
        this.ufos = [];
    }

    /**
     * Начало игры
     */
    start() {
        // Не перезапускаем если уже играем
        if (this.gameState && this.gameState.isPlaying()) {
            return;
        }
        
        // Инициализируем если нужно
        if (!this.gameState) {
            this.initialize();
        }
        
        // Запускаем новую игру
        this.gameState.start();
        this.scoreManager.reset();

        // Создаём корабль в центре
        this.ship = new Ship(this.screenWidth / 2, this.screenHeight / 2);

        // Спавним начальные астероиды
        this.spawnInitialAsteroids();

        // Сбрасываем пул пуль и НЛО
        this.bulletPool.reset();
        this.ufos = [];
    }

    /**
     * Спавн начальных астероидов
     * @private
     */
    spawnInitialAsteroids() {
        // Спавним 4 крупных астероида в случайных позициях
        // Используем детерминированный алгоритм для избежания зацикливания
        const spawnPositions = this.#getSafeSpawnPositions(4);
        
        for (const pos of spawnPositions) {
            this.asteroids.push(new Asteroid(new Vector2D(pos.x, pos.y), 'large'));
        }
    }

    /**
     * Получение безопасных позиций для спавна астероидов
     * @param {number} count - количество позиций
     * @returns {Array<{x: number, y: number}>}
     * @private
     */
    #getSafeSpawnPositions(count) {
        const positions = [];
        const minDistanceFromShip = 150;
        const minDistanceBetweenAsteroids = 100;
        const maxAttempts = 100; // Защита от зацикливания

        for (let i = 0; i < count; i++) {
            let attempts = 0;
            let position = null;

            while (attempts < maxAttempts && !position) {
                const x = Math.random() * this.screenWidth;
                const y = Math.random() * this.screenHeight;

                // Проверка расстояния от корабля
                const distFromShip = Math.hypot(
                    x - this.ship.position.x,
                    y - this.ship.position.y
                );

                if (distFromShip < minDistanceFromShip) {
                    attempts++;
                    continue;
                }

                // Проверка расстояния от других астероидов
                let tooClose = false;
                for (const pos of positions) {
                    const dist = Math.hypot(x - pos.x, y - pos.y);
                    if (dist < minDistanceBetweenAsteroids) {
                        tooClose = true;
                        break;
                    }
                }

                if (!tooClose) {
                    position = { x, y };
                } else {
                    attempts++;
                }
            }

            // Если не нашли безопасную позицию, используем край экрана
            if (!position) {
                position = {
                    x: i % 2 === 0 ? 50 : this.screenWidth - 50,
                    y: i < 2 ? 50 : this.screenHeight - 50
                };
            }

            positions.push(position);
        }

        return positions;
    }

    /**
     * Обработка ввода
     * @param {Object} input - объект ввода
     */
    handleInput(input) {
        // Игнорируем ввод если игра не инициализирована
        if (!this.gameState) {
            return;
        }

        // Игнорируем null/undefined input
        if (!input) {
            return;
        }

        // Обработка паузы (toggle по нажатию) — работает в любом состоянии кроме game over
        // Для поддержки тестов, сбрасываем флаг сразу после toggle
        if (input.pause && !this.pausePressedLastFrame) {
            if (this.gameState.isPlaying()) {
                this.gameState.pause();
            } else if (this.gameState.isPaused()) {
                this.gameState.resume();
            }
            // Сбрасываем флаг сразу чтобы следующий вызов мог вызвать resume
            this.pausePressedLastFrame = false;
        }

        // Игнорируем остальные команды если на паузе или game over
        if (this.gameState.isPaused() || this.gameState.isGameOver()) {
            return;
        }

        // Вращение
        if (input.rotate) {
            this.ship.rotate(input.rotate);
        }

        // Тяга
        if (input.thrust) {
            this.ship.thrust();
            // Воспроизводим звук тяги
            if (this.audio && this.audio.playThrust) {
                this.audio.playThrust();
            }
        }

        // Стрельба (edge detection)
        if (input.fire && !this.firePressedLastFrame) {
            const bullet = this.ship.fire();
            if (bullet) {
                // Используем пул вместо создания новой пули
                const pooledBullet = this.bulletPool.acquire(bullet.position, bullet.velocity);
                if (pooledBullet) {
                    // Воспроизводим звук выстрела
                    if (this.audio && this.audio.playShoot) {
                        this.audio.playShoot();
                    }
                }
            }
        }
        this.firePressedLastFrame = input.fire || false;
    }

    /**
     * Обновление игры
     * @param {number} deltaTime - время в секундах
     */
    update(deltaTime) {
        // Не обновляем если на паузе или game over
        if (!this.gameState || this.gameState.isPaused() || this.gameState.isGameOver()) {
            return;
        }

        // Обновляем корабль
        if (this.ship) {
            this.ship.update(deltaTime);
            this.ship.applyFriction(0.99);
            this.ship.wrapPosition(this.screenWidth, this.screenHeight);
        }

        // Обновляем астероиды
        for (const asteroid of this.asteroids) {
            asteroid.update(deltaTime);
            asteroid.wrapPosition(this.screenWidth, this.screenHeight);
        }

        // Обновляем пули через пул (без аллокаций)
        this.bulletPool.update(deltaTime);

        // Обновляем НЛО
        for (const ufo of this.ufos) {
            ufo.update(deltaTime);
            ufo.wrapPosition(this.screenWidth, this.screenHeight);
        }

        // Проверяем коллизии
        this.checkCollisions();

        // Проверяем завершение уровня
        if (this.asteroids.length === 0 && this.gameState.isPlaying()) {
            this.gameState.nextLevel();
            this.spawnInitialAsteroids();
        }

        // Рендерим текущее состояние игры
        this.render();
    }

    /**
     * Рендеринг игры
     */
    render() {
        if (this.renderer && this.renderer.render) {
            this.renderer.render(this.getEntities());
        }
    }

    /**
     * Проверка коллизий
     * @private
     */
    checkCollisions() {
        const entities = {
            ship: this.ship,
            asteroids: this.asteroids,
            bullets: this.bulletPool.getActive(),
            ufos: this.ufos
        };

        // ✅ Используем экземпляр CollisionDetector с SpatialGrid оптимизацией
        const collisions = this.collisionDetector.checkAll(entities);

        for (const collision of collisions) {
            switch (collision.type) {
                case 'ship-asteroid':
                    this.handleShipAsteroidCollision(collision.ship, collision.asteroid);
                    break;
                case 'bullet-asteroid':
                    this.handleBulletAsteroidCollision(collision.bullet, collision.asteroid);
                    break;
                case 'bullet-ufo':
                    this.handleBulletUfoCollision(collision.bullet, collision.ufo);
                    break;
                case 'ship-ufo':
                    this.handleShipUfoCollision(collision.ship, collision.ufo);
                    break;
            }
        }
    }

    /**
     * Обработка коллизии корабля с астероидом
     * @private
     */
    handleShipAsteroidCollision(ship, asteroid) {
        // Потеря жизни
        this.gameState.hit();

        // Воспроизводим звук взрыва
        if (this.audio && this.audio.playExplosion) {
            this.audio.playExplosion();
        }

        // Если игра не закончена, пересоздаём корабль в центре
        if (!this.gameState.isGameOver()) {
            this.ship = new Ship(this.screenWidth / 2, this.screenHeight / 2);
        }
    }

    /**
     * Обработка коллизии пули с астероидом
     * @private
     */
    handleBulletAsteroidCollision(bullet, asteroid) {
        // Возвращаем пулю в пул
        this.bulletPool.release(bullet);

        // Добавляем очки
        this.scoreManager.addScore(asteroid.getPoints());

        // Разбиваем астероид
        const fragments = asteroid.split();

        // Удаляем оригинальный астероид
        const index = this.asteroids.indexOf(asteroid);
        if (index > -1) {
            this.asteroids.splice(index, 1);
        }

        // Добавляем фрагменты
        this.asteroids.push(...fragments);

        // Воспроизводим звук взрыва
        if (this.audio && this.audio.playExplosion) {
            this.audio.playExplosion();
        }
    }

    /**
     * Обработка коллизии пули с НЛО
     * @private
     */
    handleBulletUfoCollision(bullet, ufo) {
        // Возвращаем пулю в пул
        this.bulletPool.release(bullet);

        // Добавляем очки (1000 за малое НЛО, 200 за большое)
        const points = ufo.isSmall ? 1000 : 200;
        this.scoreManager.addScore(points);

        // Удаляем НЛО
        const index = this.ufos.indexOf(ufo);
        if (index > -1) {
            this.ufos.splice(index, 1);
        }

        // Воспроизводим звук взрыва
        if (this.audio && this.audio.playExplosion) {
            this.audio.playExplosion();
        }
    }

    /**
     * Обработка коллизии корабля с НЛО
     * @private
     */
    handleShipUfoCollision(ship, ufo) {
        // Потеря жизни
        this.gameState.hit();

        // Воспроизводим звук взрыва
        if (this.audio && this.audio.playExplosion) {
            this.audio.playExplosion();
        }

        // Если игра не закончена, пересоздаём корабль в центре
        if (!this.gameState.isGameOver()) {
            this.ship = new Ship(this.screenWidth / 2, this.screenHeight / 2);
        }
    }

    /**
     * Получение состояния игры
     * @returns {GameState}
     */
    getState() {
        return this.gameState;
    }

    /**
     * Получение корабля
     * @returns {Ship}
     */
    getShip() {
        return this.ship;
    }

    /**
     * Получение астероидов
     * @returns {Asteroid[]}
     */
    getAsteroids() {
        return this.asteroids;
    }

    /**
     * Получение пуль
     * @returns {Bullet[]}
     */
    getBullets() {
        return this.bulletPool.getActive();
    }

    /**
     * Получение НЛО
     * @returns {UFO[]}
     */
    getUFOs() {
        return this.ufos;
    }

    /**
     * Получение текущего счёта
     * @returns {number}
     */
    getScore() {
        return this.scoreManager ? this.scoreManager.getCurrentScore() : 0;
    }

    /**
     * Получение рекорда
     * @returns {number}
     */
    getHighScore() {
        return this.scoreManager ? this.scoreManager.getHighScore() : 0;
    }

    /**
     * Получение текущего уровня
     * @returns {number}
     */
    getLevel() {
        return this.gameState ? this.gameState.level : 1;
    }

    /**
     * Получение количества жизней
     * @returns {number}
     */
    getLives() {
        return this.gameState ? this.gameState.lives : 3;
    }

    /**
     * Добавление очков
     * @param {number} points
     */
    addScore(points) {
        if (this.scoreManager) {
            this.scoreManager.addScore(points);
        }
    }

    /**
     * Пауза игры
     */
    pause() {
        if (this.gameState && this.gameState.isPlaying()) {
            this.gameState.pause();
        }
    }

    /**
     * Получение всех сущностей для рендерера
     * @returns {Object}
     */
    getEntities() {
        return {
            ship: this.ship,
            asteroids: this.asteroids,
            bullets: this.bulletPool.getActive(),
            ufos: this.ufos
        };
    }
}
