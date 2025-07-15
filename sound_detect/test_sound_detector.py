import unittest
import numpy as np
import time
from unittest.mock import MagicMock
from sound_detector import SoundDetector, DetectionState


class TestSoundDetector(unittest.TestCase):
        
    def test_detect_target_frequencies_single_frequency(self):
        """Test detection of single target frequency."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.1,
            detection_duration=0.1,
        )
        # Generate 440Hz sine wave (one of the target frequencies)
        duration = 0.1
        sample_rate = 44100
        frequency = 440.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        sine_wave = np.sin(2 * np.pi * frequency * t)
        
        detected_targets = detector._detect_target_frequencies(sine_wave)
        
        # Should detect 440Hz frequency
        self.assertIn(440.0, detected_targets)
        
    def test_detect_target_frequencies_multiple_frequencies(self):
        """Test detection of multiple target frequencies."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.1,
            detection_duration=0.1,
        )
        # Generate signal with 440Hz and 880Hz (both target frequencies)
        duration = 0.1
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        signal = (np.sin(2 * np.pi * 440 * t) + 
                 np.sin(2 * np.pi * 880 * t))
        
        detected_targets = detector._detect_target_frequencies(signal)
        
        # Should detect both frequencies
        self.assertIn(440.0, detected_targets)
        self.assertIn(880.0, detected_targets)
        
    def test_detect_target_frequencies_non_target(self):
        """Test that non-target frequencies are not detected."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.1,
            detection_duration=0.1,
        )
        # Generate 1000Hz sine wave (not a target frequency)
        duration = 0.1
        sample_rate = 44100
        frequency = 1000.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        sine_wave = np.sin(2 * np.pi * frequency * t)
        
        detected_targets = detector._detect_target_frequencies(sine_wave)
        
        # Should not detect any target frequencies
        self.assertEqual(len(detected_targets), 0)
        
    def test_detect_target_frequencies_low_amplitude(self):
        """Test that low amplitude signals below threshold are not detected."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.5,  # Higher threshold
            detection_duration=0.1,
        )
        # Generate signal with low amplitude target frequency and louder noise
        duration = 0.1
        sample_rate = 44100
        frequency = 440.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Low amplitude target frequency + louder background noise at non-target frequency
        weak_signal = 0.1 * np.sin(2 * np.pi * frequency * t)  # Weak 440Hz
        loud_noise = 1.0 * np.sin(2 * np.pi * 1000 * t)  # Loud 1000Hz noise
        combined_signal = weak_signal + loud_noise
        
        detected_targets = detector._detect_target_frequencies(combined_signal)
        
        # Should not detect target frequency due to low relative amplitude
        self.assertEqual(len(detected_targets), 0)
        
    def test_sustained_detection_logic(self):
        """Test sustained detection over multiple calls."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.1,
            detection_duration=0.1,
        )
        # Generate 440Hz sine wave
        duration = 0.1
        sample_rate = 44100
        frequency = 440.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        sine_wave = np.sin(2 * np.pi * frequency * t)
        
        # Process multiple chunks to build up detection history
        for _ in range(5):
            detected_targets = detector._detect_target_frequencies(sine_wave)
            time.sleep(0.01)  # Small delay between detections
            
        # Should consistently detect 440Hz frequency
        self.assertIn(440.0, detected_targets)
        
    def test_process_audio_chunk_with_callback(self):
        """Test process_audio_chunk triggers callback when both frequencies detected in sequence."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0],  # Only 2 frequencies for this test
            detection_threshold=0.1,
            detection_duration=0.1,
            throttle_duration=0.1  # Reduce throttle for testing
        )
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Generate test signals
        duration = 0.1
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        first_freq_signal = np.sin(2 * np.pi * 440 * t)  # 440Hz (first frequency)
        second_freq_signal = np.sin(2 * np.pi * 880 * t)  # 880Hz (second frequency)
        
        # Process first frequency to transition to WAITING_SECOND
        for _ in range(5):
            detector.process_audio_chunk(first_freq_signal)
            time.sleep(0.01)
        
        # Process second frequency to complete detection
        for _ in range(5):
            detector.process_audio_chunk(second_freq_signal)
            time.sleep(0.01)
            
        # Callback should have been called at least once
        self.assertTrue(callback.called)
        
    def test_process_audio_chunk_no_detection(self):
        """Test process_audio_chunk doesn't trigger callback for non-target frequency."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.1,
            detection_duration=0.1,
        )
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Generate 1000Hz sine wave (not a target frequency)
        duration = 0.1
        sample_rate = 44100
        frequency = 1000.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        sine_wave = np.sin(2 * np.pi * frequency * t)
        
        detector.process_audio_chunk(sine_wave)
        
        # Callback should not have been called
        self.assertFalse(callback.called)
        
    def test_sequential_detection_order_matters(self):
        """Test that frequencies must be detected in the correct order."""
        detector = SoundDetector(
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_duration=0.1,
            throttle_duration=0.1  # Reduce throttle for testing
        )
        
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Generate test signals
        duration = 0.1
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        freq1_signal = np.sin(2 * np.pi * 440 * t)    # 440Hz (first)
        freq2_signal = np.sin(2 * np.pi * 880 * t)    # 880Hz (second)
        freq3_signal = np.sin(2 * np.pi * 1320 * t)   # 1320Hz (third)
        
        # Test 1: Send frequencies in wrong order (3, 1, 2)
        for _ in range(3):
            detector.process_audio_chunk(freq3_signal)
            time.sleep(0.01)
        for _ in range(3):
            detector.process_audio_chunk(freq1_signal)
            time.sleep(0.01)
        for _ in range(3):
            detector.process_audio_chunk(freq2_signal)
            time.sleep(0.01)
            
        # Should not have triggered callback (wrong order)
        self.assertFalse(callback.called)
        
        # Test 2: Send frequencies in correct order (1, 2, 3)
        for _ in range(3):
            detector.process_audio_chunk(freq1_signal)
            time.sleep(0.01)
        for _ in range(3):
            detector.process_audio_chunk(freq2_signal)
            time.sleep(0.01)
        for _ in range(3):
            detector.process_audio_chunk(freq3_signal)
            time.sleep(0.01)
            
        # Should have triggered callback (correct order)
        self.assertTrue(callback.called)
        
    def test_empty_audio_data(self):
        """Test handling of empty audio data."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.1,
            detection_duration=0.1,
        )
        empty_data = np.array([])
        detected_targets = detector._detect_target_frequencies(empty_data)
        self.assertEqual(len(detected_targets), 0)
        
    def test_noise_signal(self):
        """Test that random noise doesn't trigger false detections."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.1,
            detection_duration=0.1,
        )
        # Generate white noise
        np.random.seed(42)  # For reproducible tests
        noise = np.random.normal(0, 0.1, 4096)
        
        detected_targets = detector._detect_target_frequencies(noise)
        
        # Should not detect target frequencies in noise
        self.assertEqual(len(detected_targets), 0)
    
    
    def test_state_machine_timeout(self):
        """Test state machine timeout from WAITING_SECOND state."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.1,
            detection_duration=0.1,
            state_timeout=0.5  # Short timeout for testing
        )
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Generate first frequency signal
        duration = 0.1
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        first_freq_signal = np.sin(2 * np.pi * 440 * t)
        
        # Send first frequency to transition to WAITING_SECOND
        for _ in range(5):
            detector.process_audio_chunk(first_freq_signal)
            time.sleep(0.01)
        
        # Should be in WAITING state (waiting for second frequency)
        self.assertEqual(detector.get_current_state(), DetectionState.WAITING)
        
        # Wait for timeout
        time.sleep(0.6)
        
        # Process silence to trigger timeout check
        silence = np.zeros(int(sample_rate * duration))
        detector.process_audio_chunk(silence)
        
        # Should reset to WAITING due to timeout
        self.assertEqual(detector.get_current_state(), DetectionState.WAITING)
        self.assertFalse(callback.called)
    
    def test_state_machine_reset_on_lost_first_frequency(self):
        """Test state machine resets when first frequency is lost in WAITING_SECOND state."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.1,
            detection_duration=0.1,
            state_timeout=2.0
        )
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Generate test signals
        duration = 0.1
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        first_freq_signal = np.sin(2 * np.pi * 440 * t)  # 440Hz
        noise_signal = np.sin(2 * np.pi * 1000 * t)     # 1000Hz (not a target)
        
        # Send first frequency to transition to WAITING_SECOND
        for _ in range(5):
            detector.process_audio_chunk(first_freq_signal)
            time.sleep(0.01)
        
        # Should be in WAITING state (waiting for second frequency)
        self.assertEqual(detector.get_current_state(), DetectionState.WAITING)
        
        # Send noise (no target frequencies) - should reset to WAITING
        for _ in range(5):
            detector.process_audio_chunk(noise_signal)
            time.sleep(0.01)
        
        # Should reset to WAITING
        self.assertEqual(detector.get_current_state(), DetectionState.WAITING)
        self.assertFalse(callback.called)

    def test_state_machine_three_frequencies(self):
        """Test state machine with three frequencies in sequence."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.1,
            detection_duration=0.1,
            state_timeout=2.0,
            throttle_duration=0.1  # Reduce throttle for testing
        )
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Generate test signals
        duration = 0.1
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        freq1_signal = np.sin(2 * np.pi * 440 * t)    # 440Hz
        freq2_signal = np.sin(2 * np.pi * 880 * t)    # 880Hz
        freq3_signal = np.sin(2 * np.pi * 1320 * t)   # 1320Hz
        
        # Initial state should be WAITING
        self.assertEqual(detector.get_current_state(), DetectionState.WAITING)
        
        # Send first frequency
        for _ in range(5):
            detector.process_audio_chunk(freq1_signal)
            time.sleep(0.01)
        
        # Should still be in WAITING state (waiting for second frequency)
        self.assertEqual(detector.get_current_state(), DetectionState.WAITING)
        self.assertFalse(callback.called)
        
        # Send second frequency
        for _ in range(5):
            detector.process_audio_chunk(freq2_signal)
            time.sleep(0.01)
        
        # Should still be in WAITING state (waiting for third frequency)
        self.assertEqual(detector.get_current_state(), DetectionState.WAITING)
        self.assertFalse(callback.called)
        
        # Send third frequency - should complete and trigger callback
        for _ in range(5):
            detector.process_audio_chunk(freq3_signal)
            time.sleep(0.01)
        
        # Should have triggered callback
        self.assertTrue(callback.called)
        
        # After callback, state should reset to WAITING
        self.assertEqual(detector.get_current_state(), DetectionState.WAITING)

    def test_state_machine_single_frequency(self):
        """Test state machine with single frequency."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0],
            detection_threshold=0.1,
            detection_duration=0.1,
            state_timeout=2.0,
            throttle_duration=0.1  # Reduce throttle for testing
        )
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Generate test signal
        duration = 0.1
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq_signal = np.sin(2 * np.pi * 440 * t)
        
        # Initial state should be WAITING
        self.assertEqual(detector.get_current_state(), DetectionState.WAITING)
        
        # Send frequency - should complete immediately
        for _ in range(5):
            detector.process_audio_chunk(freq_signal)
            time.sleep(0.01)
            if callback.called:
                break
        
        # Should have triggered callback
        self.assertTrue(callback.called)
        
        # State should be reset to WAITING immediately after callback
        # The reset happens in the same process_audio_chunk call
        self.assertEqual(detector.get_current_state(), DetectionState.WAITING)


if __name__ == '__main__':
    unittest.main()