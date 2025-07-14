import unittest
import numpy as np
import time
from unittest.mock import MagicMock
from sound_detector import SoundDetector


class TestSoundDetector(unittest.TestCase):
        
    def test_detect_target_frequencies_single_frequency(self):
        """Test detection of single target frequency."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.1,
            detection_duration=0.1,
            min_matching_frequencies=1
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
            min_matching_frequencies=1
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
            min_matching_frequencies=1
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
            min_matching_frequencies=1
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
            min_matching_frequencies=1
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
        """Test process_audio_chunk triggers callback when frequency detected."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.1,
            detection_duration=0.1,
            min_matching_frequencies=1
        )
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Generate 440Hz sine wave that should trigger detection
        duration = 0.1
        sample_rate = 44100
        frequency = 440.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        sine_wave = np.sin(2 * np.pi * frequency * t)
        
        # Process multiple chunks to ensure sustained detection
        for _ in range(5):
            detector.process_audio_chunk(sine_wave)
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
            min_matching_frequencies=1
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
        
    def test_min_matching_frequencies_requirement(self):
        """Test that min_matching_frequencies requirement is enforced."""
        # Set detector to require 2 matching frequencies
        detector = SoundDetector(
            target_frequencies=[440.0, 880.0, 1320.0],
            min_matching_frequencies=2,
            detection_duration=0.1
        )
        
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Generate signal with only one target frequency (440Hz)
        duration = 0.1
        sample_rate = 44100
        frequency = 440.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        sine_wave = np.sin(2 * np.pi * frequency * t)
        
        # Process multiple chunks
        for _ in range(5):
            detector.process_audio_chunk(sine_wave)
            time.sleep(0.01)
            
        # Callback should not be called since we need 2 frequencies but only have 1
        self.assertFalse(callback.called)
        
        # Now test with signal containing 2 target frequencies
        signal_2_freqs = (np.sin(2 * np.pi * 440 * t) + 
                         np.sin(2 * np.pi * 880 * t))
        
        # Process multiple chunks with 2 frequencies
        for _ in range(5):
            detector.process_audio_chunk(signal_2_freqs)
            time.sleep(0.01)
            
        # Now callback should be called
        self.assertTrue(callback.called)
        
    def test_empty_audio_data(self):
        """Test handling of empty audio data."""
        detector = SoundDetector(
            sample_rate=44100,
            chunk_size=4096,
            target_frequencies=[440.0, 880.0, 1320.0],
            detection_threshold=0.1,
            detection_duration=0.1,
            min_matching_frequencies=1
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
            min_matching_frequencies=1
        )
        # Generate white noise
        np.random.seed(42)  # For reproducible tests
        noise = np.random.normal(0, 0.1, 4096)
        
        detected_targets = detector._detect_target_frequencies(noise)
        
        # Should not detect target frequencies in noise
        self.assertEqual(len(detected_targets), 0)


if __name__ == '__main__':
    unittest.main()