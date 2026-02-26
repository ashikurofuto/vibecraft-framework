/**
 * AudioController — генерация звуковых эффектов через Web Audio API
 * Infrastructure Layer
 * 
 * @description Создаёт звуковые эффекты для игры (выстрелы, взрывы, тяга)
 * используя Web Audio API oscillators без внешних файлов
 */
export class AudioController {
    /**
     * Создать AudioController
     * @param {AudioContext} [audioContext] - AudioContext для генерации звука
     */
    constructor(audioContext) {
        // Используем предоставленный контекст или создаём новый
        this.audioContext = audioContext || new (window.AudioContext || window.webkitAudioContext)();
        
        try {
            // Создаём мастер gain node для управления общей громкостью
            this.masterGain = this.audioContext.createGain();
            this.masterGain.connect(this.audioContext.destination);
            this.masterGain.gain.value = 0.3; // Громкость по умолчанию
        } catch (e) {
            console.warn('Failed to create audio nodes:', e.message);
            this.masterGain = null;
        }
        
        // Oscillator для звука тяги (постоянный звук)
        this.thrustOscillator = null;
    }

    /**
     * Установить общую громкость
     * @param {number} value - Значение от 0 до 1
     */
    setVolume(value) {
        if (this.masterGain) {
            this.masterGain.gain.value = Math.max(0, Math.min(1, value));
        }
    }

    /**
     * Воспроизвести звук выстрела
     * @description Квадратная волна с частотой от 880Hz до 110Hz за 0.1 сек
     */
    playShoot() {
        try {
            const osc = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();

            // Соединяем: oscillator -> gain -> masterGain
            osc.connect(gain);
            gain.connect(this.masterGain);

            // Настройка звука выстрела
            osc.type = 'square';
            osc.frequency.setValueAtTime(880, this.audioContext.currentTime);
            osc.frequency.exponentialRampToValueAtTime(110, this.audioContext.currentTime + 0.1);

            // Настройка громкости
            gain.gain.setValueAtTime(1, this.audioContext.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1);

            // Запускаем и останавливаем
            osc.start(this.audioContext.currentTime);
            osc.stop(this.audioContext.currentTime + 0.1);
        } catch (e) {
            console.warn('Failed to play shoot sound:', e.message);
        }
    }

    /**
     * Воспроизвести звук взрыва
     * @description Пилообразная волна с частотой от 100Hz до 10Hz за 0.3 сек
     */
    playExplosion() {
        try {
            const osc = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();

            // Соединяем: oscillator -> gain -> masterGain
            osc.connect(gain);
            gain.connect(this.masterGain);

            // Настройка звука взрыва
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(100, this.audioContext.currentTime);
            osc.frequency.exponentialRampToValueAtTime(10, this.audioContext.currentTime + 0.3);

            // Настройка громкости
            gain.gain.setValueAtTime(1, this.audioContext.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);

            // Запускаем и останавливаем
            osc.start(this.audioContext.currentTime);
            osc.stop(this.audioContext.currentTime + 0.3);
        } catch (e) {
            console.warn('Failed to play explosion sound:', e.message);
        }
    }

    /**
     * Воспроизвести звук попадания
     * @description Квадратная волна с частотой от 220Hz до 110Hz за 0.2 сек
     */
    playHit() {
        try {
            const osc = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();

            // Соединяем: oscillator -> gain -> masterGain
            osc.connect(gain);
            gain.connect(this.masterGain);

            // Настройка звука попадания
            osc.type = 'square';
            osc.frequency.setValueAtTime(220, this.audioContext.currentTime);
            osc.frequency.linearRampToValueAtTime(110, this.audioContext.currentTime + 0.2);

            // Настройка громкости
            gain.gain.setValueAtTime(1, this.audioContext.currentTime);
            gain.gain.linearRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2);

            // Запускаем и останавливаем
            osc.start(this.audioContext.currentTime);
            osc.stop(this.audioContext.currentTime + 0.2);
        } catch (e) {
            console.warn('Failed to play hit sound:', e.message);
        }
    }

    /**
     * Запустить звук тяги двигателя
     * @description Постоянная пилообразная волна 50Hz
     */
    startThrust() {
        try {
            // Не создаём новый oscillator если уже играет
            if (this.thrustOscillator) {
                return;
            }

            this.thrustOscillator = this.audioContext.createOscillator();
            const gain = this.audioContext.createGain();

            // Соединяем: oscillator -> gain -> masterGain
            this.thrustOscillator.connect(gain);
            gain.connect(this.masterGain);

            // Настройка звука тяги
            this.thrustOscillator.type = 'sawtooth';
            this.thrustOscillator.frequency.value = 50;

            // Настройка громкости
            gain.gain.value = 0.3;

            // Запускаем
            this.thrustOscillator.start(this.audioContext.currentTime);
        } catch (e) {
            console.warn('Failed to start thrust sound:', e.message);
        }
    }

    /**
     * Остановить звук тяги двигателя
     */
    stopThrust() {
        try {
            if (this.thrustOscillator) {
                this.thrustOscillator.stop(this.audioContext.currentTime);
                this.thrustOscillator = null;
            }
        } catch (e) {
            console.warn('Failed to stop thrust sound:', e.message);
        }
    }
}
