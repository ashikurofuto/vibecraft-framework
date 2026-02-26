/**
 * Mock для Web Audio API
 * Используется в тестах AudioController
 */
import { jest } from '@jest/globals';

/**
 * Создаёт мок для AudioContext
 * @returns {Object} Мок объекта AudioContext
 */
export function createMockAudioContext() {
    const mockOscillator = {
        start: jest.fn(),
        stop: jest.fn(),
        connect: jest.fn(),
        disconnect: jest.fn(),
        frequency: {
            value: 0,
            setValueAtTime: jest.fn(),
            exponentialRampToValueAtTime: jest.fn(),
            linearRampToValueAtTime: jest.fn()
        },
        type: '',
        onended: null
    };

    const mockGain = {
        connect: jest.fn(),
        disconnect: jest.fn(),
        gain: {
            value: 1,
            setValueAtTime: jest.fn(),
            exponentialRampToValueAtTime: jest.fn(),
            linearRampToValueAtTime: jest.fn()
        }
    };

    const mockBuffer = {
        sampleRate: 44100,
        length: 44100,
        numberOfChannels: 2,
        getChannelData: jest.fn(() => new Float32Array(44100))
    };

    return {
        createOscillator: jest.fn(() => mockOscillator),
        createGain: jest.fn(() => mockGain),
        createBuffer: jest.fn(() => mockBuffer),
        createBufferSource: jest.fn(() => ({
            connect: jest.fn(),
            start: jest.fn(),
            stop: jest.fn(),
            buffer: null
        })),
        currentTime: 0,
        destination: {},
        resume: jest.fn(),
        suspend: jest.fn(),
        close: jest.fn(),

        // Метод для получения последнего созданного осциллятора
        _getLastOscillator: () => mockOscillator,
        _getLastGain: () => mockGain
    };
}

/**
 * Создаёт недоступный AudioContext (для тестирования обработки ошибок)
 * @returns {Object} Мок который выбрасывает ошибки
 */
export function createMockAudioContextUnavailable() {
    return {
        createOscillator: jest.fn(() => {
            throw new Error('Audio not available');
        }),
        createGain: jest.fn(() => {
            throw new Error('Audio not available');
        }),
        currentTime: 0,
        destination: {}
    };
}

/**
 * Создаёт частично доступный AudioContext (createOscillator работает, createGain нет)
 * @returns {Object} Мок с частичной доступностью
 */
export function createMockAudioContextPartial() {
    const mockOscillator = {
        start: jest.fn(),
        stop: jest.fn(),
        connect: jest.fn(),
        frequency: { value: 0, setValueAtTime: jest.fn() },
        type: ''
    };

    return {
        createOscillator: jest.fn(() => mockOscillator),
        createGain: jest.fn(() => {
            throw new Error('Gain node not available');
        }),
        currentTime: 0,
        destination: {}
    };
}
