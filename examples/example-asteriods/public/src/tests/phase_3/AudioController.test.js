/**
 * Тесты для AudioController класса
 * Infrastructure Layer - Phase 3
 * 
 * AudioController отвечает за генерацию звуковых эффектов через Web Audio API
 */

import { AudioController } from '../../infrastructure/AudioController.js';
import { 
    createMockAudioContext,
    createMockAudioContextUnavailable,
    createMockAudioContextPartial
} from '../__mocks__/audio.js';

describe('AudioController', () => {
    let audioController;
    let mockAudioContext;
    let mockOscillator;
    let mockGain;

    beforeEach(() => {
        mockAudioContext = createMockAudioContext();
        mockOscillator = mockAudioContext._getLastOscillator();
        mockGain = mockAudioContext._getLastGain();
        
        audioController = new AudioController(mockAudioContext);
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    describe('constructor', () => {
        test('should create AudioController with provided audio context', () => {
            expect(audioController.audioContext).toBe(mockAudioContext);
        });

        test('should create master gain node', () => {
            expect(mockAudioContext.createGain).toHaveBeenCalled();
        });

        test('should connect master gain to destination', () => {
            expect(mockGain.connect).toHaveBeenCalledWith(mockAudioContext.destination);
        });

        test('should set default volume to 0.3', () => {
            expect(mockGain.gain.value).toBe(0.3);
        });

        test('should initialize thrustOscillator to null', () => {
            expect(audioController.thrustOscillator).toBeNull();
        });

        test('should create default AudioContext when not provided', () => {
            const realAudioContext = window.AudioContext || window.webkitAudioContext;
            const mockContext = jest.fn();
            window.AudioContext = mockContext;
            
            new AudioController();
            
            expect(mockContext).toHaveBeenCalled();
            
            window.AudioContext = realAudioContext;
        });
    });

    describe('setVolume', () => {
        test('should set volume to specified value', () => {
            audioController.setVolume(0.5);
            expect(mockGain.gain.value).toBe(0.5);
        });

        test('should set volume to 0', () => {
            audioController.setVolume(0);
            expect(mockGain.gain.value).toBe(0);
        });

        test('should set volume to 1 (maximum)', () => {
            audioController.setVolume(1);
            expect(mockGain.gain.value).toBe(1);
        });

        test('should clamp volume to minimum 0 when negative', () => {
            audioController.setVolume(-0.5);
            expect(mockGain.gain.value).toBe(0);
        });

        test('should clamp volume to maximum 1 when greater than 1', () => {
            audioController.setVolume(1.5);
            expect(mockGain.gain.value).toBe(1);
        });

        test('should clamp volume when value is very large', () => {
            audioController.setVolume(100);
            expect(mockGain.gain.value).toBe(1);
        });
    });

    describe('playShoot', () => {
        test('should create oscillator for shoot sound', () => {
            audioController.playShoot();
            expect(mockAudioContext.createOscillator).toHaveBeenCalled();
        });

        test('should create gain node for shoot sound', () => {
            audioController.playShoot();
            expect(mockAudioContext.createGain).toHaveBeenCalled();
        });

        test('should connect oscillator to gain', () => {
            audioController.playShoot();
            const shootOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            const shootGain = mockAudioContext.createGain.mock.results[0].value;
            expect(shootOscillator.connect).toHaveBeenCalledWith(shootGain);
        });

        test('should connect gain to master gain', () => {
            audioController.playShoot();
            const shootGain = mockAudioContext.createGain.mock.results[0].value;
            expect(shootGain.connect).toHaveBeenCalledWith(audioController.masterGain);
        });

        test('should set oscillator type to square', () => {
            audioController.playShoot();
            const shootOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(shootOscillator.type).toBe('square');
        });

        test('should set initial frequency to 880Hz', () => {
            audioController.playShoot();
            const shootOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(shootOscillator.frequency.setValueAtTime).toHaveBeenCalledWith(
                880,
                mockAudioContext.currentTime
            );
        });

        test('should ramp frequency down to 110Hz', () => {
            audioController.playShoot();
            const shootOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(shootOscillator.frequency.exponentialRampToValueAtTime).toHaveBeenCalledWith(
                110,
                mockAudioContext.currentTime + 0.1
            );
        });

        test('should start oscillator', () => {
            audioController.playShoot();
            const shootOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(shootOscillator.start).toHaveBeenCalled();
        });

        test('should stop oscillator after 0.1 seconds', () => {
            audioController.playShoot();
            const shootOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(shootOscillator.stop).toHaveBeenCalledWith(mockAudioContext.currentTime + 0.1);
        });

        test('should not throw when audio context throws error', () => {
            const errorContext = createMockAudioContextUnavailable();
            const errorController = new AudioController(errorContext);
            
            expect(() => errorController.playShoot()).not.toThrow();
        });
    });

    describe('playExplosion', () => {
        test('should create oscillator for explosion sound', () => {
            audioController.playExplosion();
            expect(mockAudioContext.createOscillator).toHaveBeenCalled();
        });

        test('should create gain node for explosion sound', () => {
            audioController.playExplosion();
            expect(mockAudioContext.createGain).toHaveBeenCalled();
        });

        test('should set oscillator type to sawtooth', () => {
            audioController.playExplosion();
            const explosionOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(explosionOscillator.type).toBe('sawtooth');
        });

        test('should set initial frequency to 100Hz', () => {
            audioController.playExplosion();
            const explosionOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(explosionOscillator.frequency.setValueAtTime).toHaveBeenCalledWith(
                100,
                mockAudioContext.currentTime
            );
        });

        test('should ramp frequency down to 10Hz', () => {
            audioController.playExplosion();
            const explosionOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(explosionOscillator.frequency.exponentialRampToValueAtTime).toHaveBeenCalledWith(
                10,
                mockAudioContext.currentTime + 0.3
            );
        });

        test('should stop oscillator after 0.3 seconds', () => {
            audioController.playExplosion();
            const explosionOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(explosionOscillator.stop).toHaveBeenCalledWith(mockAudioContext.currentTime + 0.3);
        });

        test('should not throw when audio context throws error', () => {
            const errorContext = createMockAudioContextUnavailable();
            const errorController = new AudioController(errorContext);
            
            expect(() => errorController.playExplosion()).not.toThrow();
        });
    });

    describe('playHit', () => {
        test('should create oscillator for hit sound', () => {
            audioController.playHit();
            expect(mockAudioContext.createOscillator).toHaveBeenCalled();
        });

        test('should create gain node for hit sound', () => {
            audioController.playHit();
            expect(mockAudioContext.createGain).toHaveBeenCalled();
        });

        test('should set oscillator type to square', () => {
            audioController.playHit();
            const hitOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(hitOscillator.type).toBe('square');
        });

        test('should set initial frequency to 220Hz', () => {
            audioController.playHit();
            const hitOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(hitOscillator.frequency.setValueAtTime).toHaveBeenCalledWith(
                220,
                mockAudioContext.currentTime
            );
        });

        test('should ramp frequency linearly to 110Hz', () => {
            audioController.playHit();
            const hitOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(hitOscillator.frequency.linearRampToValueAtTime).toHaveBeenCalledWith(
                110,
                mockAudioContext.currentTime + 0.2
            );
        });

        test('should stop oscillator after 0.2 seconds', () => {
            audioController.playHit();
            const hitOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(hitOscillator.stop).toHaveBeenCalledWith(mockAudioContext.currentTime + 0.2);
        });

        test('should not throw when audio context throws error', () => {
            const errorContext = createMockAudioContextUnavailable();
            const errorController = new AudioController(errorContext);
            
            expect(() => errorController.playHit()).not.toThrow();
        });
    });

    describe('startThrust', () => {
        test('should create oscillator for thrust sound', () => {
            audioController.startThrust();
            expect(mockAudioContext.createOscillator).toHaveBeenCalled();
        });

        test('should set oscillator type to sawtooth', () => {
            audioController.startThrust();
            const thrustOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(thrustOscillator.type).toBe('sawtooth');
        });

        test('should set frequency to 50Hz', () => {
            audioController.startThrust();
            const thrustOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(thrustOscillator.frequency.value).toBe(50);
        });

        test('should store oscillator reference', () => {
            audioController.startThrust();
            expect(audioController.thrustOscillator).not.toBeNull();
        });

        test('should start oscillator', () => {
            audioController.startThrust();
            const thrustOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(thrustOscillator.start).toHaveBeenCalled();
        });

        test('should not create new oscillator if thrust is already playing', () => {
            audioController.startThrust();
            mockAudioContext.createOscillator.mockClear();
            audioController.startThrust();
            
            expect(mockAudioContext.createOscillator).not.toHaveBeenCalled();
        });

        test('should not throw when audio context throws error', () => {
            const errorContext = createMockAudioContextUnavailable();
            const errorController = new AudioController(errorContext);
            
            expect(() => errorController.startThrust()).not.toThrow();
        });
    });

    describe('stopThrust', () => {
        test('should stop thrust oscillator', () => {
            audioController.startThrust();
            audioController.stopThrust();
            
            const thrustOscillator = mockAudioContext.createOscillator.mock.results[0].value;
            expect(thrustOscillator.stop).toHaveBeenCalled();
        });

        test('should clear thrustOscillator reference', () => {
            audioController.startThrust();
            audioController.stopThrust();
            
            expect(audioController.thrustOscillator).toBeNull();
        });

        test('should not throw when called without starting thrust', () => {
            expect(() => audioController.stopThrust()).not.toThrow();
        });

        test('should not throw when audio context throws error', () => {
            const errorContext = createMockAudioContextUnavailable();
            const errorController = new AudioController(errorContext);
            
            expect(() => errorController.stopThrust()).not.toThrow();
        });
    });

    describe('Integration: Sound sequence', () => {
        test('should play multiple sounds in sequence', () => {
            audioController.playShoot();
            audioController.playExplosion();
            audioController.playHit();
            
            expect(mockAudioContext.createOscillator).toHaveBeenCalledTimes(3);
        });

        test('should handle thrust start/stop cycle', () => {
            audioController.startThrust();
            audioController.stopThrust();
            audioController.startThrust();
            audioController.stopThrust();
            
            expect(audioController.thrustOscillator).toBeNull();
        });

        test('should maintain volume across sound plays', () => {
            audioController.setVolume(0.7);
            audioController.playShoot();
            audioController.playExplosion();
            
            expect(mockGain.gain.value).toBe(0.7);
        });
    });

    describe('Error handling', () => {
        test('should handle partial audio context failure', () => {
            const partialContext = createMockAudioContextPartial();
            const partialController = new AudioController(partialContext);
            
            expect(() => partialController.playShoot()).not.toThrow();
        });

        test('should continue working after error', () => {
            const errorContext = createMockAudioContextUnavailable();
            const errorController = new AudioController(errorContext);
            
            errorController.playShoot();
            errorController.playExplosion();
            
            expect(() => errorController.setVolume(0.5)).not.toThrow();
        });
    });
});
