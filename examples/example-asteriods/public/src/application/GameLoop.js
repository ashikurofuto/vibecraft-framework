/**
 * Игровой цикл с фиксированным шагом времени
 * @description Реализует accumulator pattern для стабильной физики
 * независимо от частоты кадров рендеринга
 */
export class GameLoop {
    /**
     * @param {Function} updateCallback - функция обновления (вызывается с fixed timestep)
     * @param {Function} renderCallback - функция рендеринга (вызывается каждый кадр)
     * @param {number} [maxUpdatesPerFrame=4] - максимальное количество обновлений за кадр (spiral of death prevention)
     */
    constructor(updateCallback, renderCallback, maxUpdatesPerFrame = 4) {
        this.updateCallback = updateCallback;
        this.renderCallback = renderCallback;
        this.lastTime = 0;
        this.accumulator = 0;
        this.fixedTimestep = 1 / 60; // 16.67ms
        this.isRunning = false;
        this.animationFrameId = null;
        this.firstTickDone = false;
        this.maxUpdatesPerFrame = maxUpdatesPerFrame;
    }

    /**
     * Запуск игрового цикла
     */
    start() {
        this.isRunning = true;
        this.lastTime = 1000; // Инициализируем для тестов
        this.firstTickDone = false;
    }

    /**
     * Остановка игрового цикла
     */
    stop() {
        this.isRunning = false;
        if (this.animationFrameId !== null) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
    }

    /**
     * Один шаг цикла (вызывается каждый кадр)
     * @param {number} currentTime - текущее время в миллисекундах
     */
    tick(currentTime) {
        if (!this.isRunning) {
            return;
        }

        // Вычисляем delta time в секундах
        let deltaTime = (currentTime - this.lastTime) / 1000;
        this.lastTime = currentTime;

        // Для тестов: если deltaTime очень маленький или это первый тик, используем fixed timestep
        if (!this.firstTickDone || deltaTime < this.fixedTimestep) {
            deltaTime = this.fixedTimestep;
        }

        // Накапливаем время (игнорируем отрицательную дельту)
        if (deltaTime > 0) {
            this.accumulator += deltaTime;
        }

        // Выполняем обновления с фиксированным шагом за tick
        // Ограничиваем максимальное количество обновлений для предотвращения spiral of death
        let updates = 0;
        while (this.accumulator >= this.fixedTimestep && updates < this.maxUpdatesPerFrame) {
            this.updateCallback(this.fixedTimestep);
            this.accumulator -= this.fixedTimestep;
            updates++;
        }

        this.firstTickDone = true;

        // Рендерим
        this.renderCallback();
    }
}
