import unittest
import numpy as np
import time
import os
from unittest.mock import MagicMock, patch
from datetime import datetime
from sound_detector import SoundDetector


class TestSoundDetector(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures with reference audio file."""
        self.reference_audio_path = "reference_intercom.wav"
        # Verify reference file exists
        self.assertTrue(os.path.exists(self.reference_audio_path), 
                       f"Reference audio file {self.reference_audio_path} not found")
    
    def test_set_detection_callback_stores_callback_function(self):
        """Test setting detection callback function."""
        detector = SoundDetector(reference_audio_path=self.reference_audio_path)
        callback = MagicMock()
        
        detector.set_detection_callback(callback)
        
        self.assertEqual(detector.detection_callback, callback)
        
    def test_process_audio_chunk_without_callback_not_raise_error(self):
        """Test process_audio_chunk returns early when no callback is set."""
        detector = SoundDetector(reference_audio_path=self.reference_audio_path)
        
        # Generate some test audio data
        audio_data = np.random.random(1024).astype(np.float32)
        
        # Should not raise an error
        detector.process_audio_chunk(audio_data)
        
    def test_process_audio_chunk_with_pattern_match_triggers_callback(self):
        """Test process_audio_chunk triggers callback when pattern matches."""
        detector = SoundDetector(
            reference_audio_path=self.reference_audio_path,
            throttle_duration=0.1  # Very short throttle for testing
        )
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Set the last detection time to a very old time to avoid throttling
        detector.last_detection_time = 0
        
        # Set chunk counter to ensure processing happens on first call
        detector.chunk_counter = detector.processing_interval - 1
        
        # Mock pause window and pattern similarity
        with patch.object(detector, '_is_in_pause_window', return_value=False):
            with patch.object(detector, '_detect_pattern_similarity', return_value=True):
                audio_data = np.random.random(1024).astype(np.float32)
                detector.process_audio_chunk(audio_data)
                
                callback.assert_called_once()
                
    def test_process_audio_chunk_within_throttle_duration_prevents_detection(self):
        """Test that detection is throttled within throttle duration."""
        detector = SoundDetector(
            reference_audio_path=self.reference_audio_path,
            throttle_duration=10.0
        )
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Set initial last detection time to force throttling on second call
        detector.last_detection_time = time.time()
        
        # Mock pause window and pattern similarity
        with patch.object(detector, '_is_in_pause_window', return_value=False):
            with patch.object(detector, '_detect_pattern_similarity', return_value=True):
                audio_chunk = np.random.random(1024).astype(np.float32)
                
                # First detection should be throttled (since last_detection_time is recent)
                detector.process_audio_chunk(audio_chunk)
                callback.assert_not_called()
            
    def test_detect_pattern_similarity_with_insufficient_buffer_returns_false(self):
        """Test _detect_pattern_similarity returns False when buffer is too small."""
        detector = SoundDetector(reference_audio_path=self.reference_audio_path)
        
        # Create audio buffer smaller than required buffer size
        small_buffer = np.random.random(detector.buffer_size - 100).astype(np.float32)
        
        result = detector._detect_pattern_similarity(small_buffer)
        
        self.assertFalse(result)
        
    def test_detect_pattern_similarity_below_threshold_returns_true(self):
        """Test _detect_pattern_similarity returns True when pattern matches."""
        detector = SoundDetector(reference_audio_path=self.reference_audio_path)
        
        # Create audio buffer of correct size
        audio_buffer = np.random.random(detector.buffer_size).astype(np.float32)
        
        # Mock the DTW analyzer to return a match (similarity < threshold means match)
        with patch.object(detector.dtw_analyzer, 'calculate_similarity', return_value=0.2):
            result = detector._detect_pattern_similarity(audio_buffer)
            
            self.assertTrue(result)
                
    def test_detect_pattern_similarity_above_threshold_returns_false(self):
        """Test _detect_pattern_similarity returns False when pattern doesn't match."""
        detector = SoundDetector(reference_audio_path=self.reference_audio_path)
        
        # Create audio buffer of correct size
        audio_buffer = np.random.random(detector.buffer_size).astype(np.float32)
        
        # Mock the DTW analyzer to return no match (similarity > threshold means no match)
        with patch.object(detector.dtw_analyzer, 'calculate_similarity', return_value=0.9):
            result = detector._detect_pattern_similarity(audio_buffer)
            
            self.assertFalse(result)
                
        
    def test_process_audio_chunk_with_empty_data_does_not_crash(self):
        """Test handling of empty audio data."""
        detector = SoundDetector(reference_audio_path=self.reference_audio_path)
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        empty_data = np.array([])
        
        # Should not raise an error
        detector.process_audio_chunk(empty_data)
        
        # Callback should not be called
        callback.assert_not_called()
        
    def test_initialization_with_time_pause_enabled_sets_parameters(self):
        """Test SoundDetector initialization with time-based pause parameters."""
        detector = SoundDetector(
            reference_audio_path=self.reference_audio_path,
            enable_time_pause=True,
            pause_start_hour=22,
            pause_end_hour=8
        )
        
        self.assertTrue(detector.enable_time_pause)
        self.assertEqual(detector.pause_start_hour, 22)
        self.assertEqual(detector.pause_end_hour, 8)
        
    def test_initialization_with_time_pause_disabled_sets_flag_false(self):
        """Test that time-based pause can be disabled."""
        detector = SoundDetector(
            reference_audio_path=self.reference_audio_path,
            enable_time_pause=False
        )
        
        self.assertFalse(detector.enable_time_pause)
        
    def test_is_in_pause_window_when_disabled_returns_false(self):
        """Test _is_in_pause_window returns False when time pause is disabled."""
        detector = SoundDetector(
            reference_audio_path=self.reference_audio_path,
            enable_time_pause=False,
            pause_start_hour=0,
            pause_end_hour=0
        )
        
        # Should return False regardless of time when disabled
        result = detector._is_in_pause_window()
        self.assertFalse(result)
        
    def test_is_in_pause_window_spanning_midnight_correctly_identifies_hours(self):
        """Test _is_in_pause_window correctly handles pause window spanning midnight."""
        detector = SoundDetector(
            reference_audio_path=self.reference_audio_path,
            enable_time_pause=True,
            pause_start_hour=22,  # 10 PM
            pause_end_hour=8     # 8 AM
        )
        
        # Test various hours
        test_cases = [
            (23, True),   # 11 PM - should be paused
            (0, True),    # Midnight - should be paused
            (3, True),    # 3 AM - should be paused
            (7, True),    # 7 AM - should be paused
            (8, False),   # 8 AM - should not be paused
            (12, False),  # Noon - should not be paused
            (21, False),  # 9 PM - should not be paused
            (22, True),   # 10 PM - should be paused
        ]
        
        for hour, expected_paused in test_cases:
            with patch('sound_detector.datetime') as mock_datetime:
                mock_datetime.now.return_value.hour = hour
                result = detector._is_in_pause_window()
                self.assertEqual(result, expected_paused, 
                               f"Hour {hour} should {'be paused' if expected_paused else 'not be paused'}")
                
    def test_is_in_pause_window_within_same_day_correctly_identifies_hours(self):
        """Test _is_in_pause_window for pause window within same day."""
        detector = SoundDetector(
            reference_audio_path=self.reference_audio_path,
            enable_time_pause=True,
            pause_start_hour=14,  # 2 PM
            pause_end_hour=18    # 6 PM
        )
        
        test_cases = [
            (13, False),  # 1 PM - should not be paused
            (14, True),   # 2 PM - should be paused
            (16, True),   # 4 PM - should be paused
            (17, True),   # 5 PM - should be paused
            (18, False),  # 6 PM - should not be paused
            (19, False),  # 7 PM - should not be paused
        ]
        
        for hour, expected_paused in test_cases:
            with patch('sound_detector.datetime') as mock_datetime:
                mock_datetime.now.return_value.hour = hour
                result = detector._is_in_pause_window()
                self.assertEqual(result, expected_paused,
                               f"Hour {hour} should {'be paused' if expected_paused else 'not be paused'}")
                
    def test_process_audio_chunk_during_pause_window_skips_detection(self):
        """Test that process_audio_chunk skips processing during pause window."""
        detector = SoundDetector(
            reference_audio_path=self.reference_audio_path,
            enable_time_pause=True,
            pause_start_hour=22,
            pause_end_hour=8,
            throttle_duration=0.1,
        )
        detector.last_detection_time = 0
        detector.chunk_counter = detector.processing_interval - 1

        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Mock current time to be in pause window (e.g., 2 AM)
        with patch('sound_detector.datetime') as mock_datetime:
            mock_datetime.now.return_value.hour = 2
            
            # Mock pattern detection to return True (should be ignored due to pause)
            with patch.object(detector, '_detect_pattern_similarity', return_value=True):
                audio_data = np.random.random(1024).astype(np.float32)
                detector.process_audio_chunk(audio_data)
                
                # Callback should not be called due to time-based pause
                callback.assert_not_called()

    def test_process_audio_chunk_outside_pause_window_not_skip_detection(self):
        detector = SoundDetector(
            reference_audio_path=self.reference_audio_path,
            enable_time_pause=True,
            pause_start_hour=22,
            pause_end_hour=8,
            throttle_duration=0.1,
        )
        detector.last_detection_time = 0
        detector.chunk_counter = detector.processing_interval - 1

        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Mock current time to be in pause window (e.g., 2 AM)
        with patch('sound_detector.datetime') as mock_datetime:
            mock_datetime.now.return_value.hour = 10
            
            # Mock pattern detection to return True (should be ignored due to pause)
            with patch.object(detector, '_detect_pattern_similarity', return_value=True):
                audio_data = np.random.random(1024).astype(np.float32)
                detector.process_audio_chunk(audio_data)
                
                # Callback should not be called due to time-based pause
                callback.assert_called_once()
                

if __name__ == '__main__':
    unittest.main()
