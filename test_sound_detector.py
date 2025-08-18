import unittest
import numpy as np
import time
import os
from unittest.mock import MagicMock, patch
from sound_detector import SoundDetector


class TestSoundDetector(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures with reference audio file."""
        self.reference_audio_path = "reference_intercom.wav"
        # Verify reference file exists
        self.assertTrue(os.path.exists(self.reference_audio_path), 
                       f"Reference audio file {self.reference_audio_path} not found")
    
    def test_sound_detector_initialization(self):
        """Test SoundDetector initialization with DTW analyzer."""
        detector = SoundDetector(
            reference_audio_path=self.reference_audio_path,
            sample_rate=44100,
            chunk_size=4096,
            similarity_threshold=0.3,
            detection_duration=0.1,
            throttle_duration=10.0
        )
        
        # Check that detector is properly initialized
        self.assertEqual(detector.sample_rate, 44100)
        self.assertEqual(detector.chunk_size, 4096)
        self.assertEqual(detector.similarity_threshold, 0.3)
        self.assertEqual(detector.detection_duration, 0.1)
        self.assertEqual(detector.throttle_duration, 10.0)
        self.assertIsNotNone(detector.dtw_analyzer)
        self.assertIsNone(detector.detection_callback)
        
    def test_set_detection_callback(self):
        """Test setting detection callback function."""
        detector = SoundDetector(reference_audio_path=self.reference_audio_path)
        callback = MagicMock()
        
        detector.set_detection_callback(callback)
        
        self.assertEqual(detector.detection_callback, callback)
        
    def test_process_audio_chunk_without_callback(self):
        """Test process_audio_chunk returns early when no callback is set."""
        detector = SoundDetector(reference_audio_path=self.reference_audio_path)
        
        # Generate some test audio data
        audio_data = np.random.random(1024).astype(np.float32)
        
        # Should not raise an error and should return early
        detector.process_audio_chunk(audio_data)
        
    def test_process_audio_chunk_with_pattern_match(self):
        """Test process_audio_chunk triggers callback when pattern matches."""
        detector = SoundDetector(
            reference_audio_path=self.reference_audio_path,
            throttle_duration=0.1  # Very short throttle for testing
        )
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Set the last detection time to a very old time to avoid throttling
        detector.last_detection_time = 0
        
        # Directly mock the _detect_pattern_similarity method to return True
        with patch.object(detector, '_detect_pattern_similarity', return_value=True):
            audio_data = np.random.random(1024).astype(np.float32)
            detector.process_audio_chunk(audio_data)
            
            # Callback should have been called
            callback.assert_called_once()
                
    def test_process_audio_chunk_throttling(self):
        """Test that detection is throttled within throttle duration."""
        detector = SoundDetector(
            reference_audio_path=self.reference_audio_path,
            throttle_duration=10.0
        )
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Set initial last detection time to force throttling on second call
        detector.last_detection_time = time.time()
        
        # Mock the _detect_pattern_similarity method to always return True
        with patch.object(detector, '_detect_pattern_similarity', return_value=True):
            audio_chunk = np.random.random(1024).astype(np.float32)
            
            # First detection should be throttled (since last_detection_time is recent)
            detector.process_audio_chunk(audio_chunk)
            callback.assert_not_called()
            
            # Set last_detection_time to a long time ago to allow detection
            detector.last_detection_time = 0
            detector.process_audio_chunk(audio_chunk)
            callback.assert_called_once()
            
    def test_detect_pattern_similarity_insufficient_buffer(self):
        """Test _detect_pattern_similarity returns False when buffer is too small."""
        detector = SoundDetector(reference_audio_path=self.reference_audio_path)
        
        # Create audio buffer smaller than required buffer size
        small_buffer = np.random.random(detector.buffer_size - 100).astype(np.float32)
        
        result = detector._detect_pattern_similarity(small_buffer)
        
        self.assertFalse(result)
        
    def test_detect_pattern_similarity_with_match(self):
        """Test _detect_pattern_similarity returns True when pattern matches."""
        detector = SoundDetector(reference_audio_path=self.reference_audio_path)
        
        # Create audio buffer of correct size
        audio_buffer = np.random.random(detector.buffer_size).astype(np.float32)
        
        # Mock the DTW analyzer to return a match
        with patch.object(detector.dtw_analyzer, 'is_pattern_match', return_value=True):
            with patch.object(detector.dtw_analyzer, 'get_similarity_score', return_value=0.2):
                result = detector._detect_pattern_similarity(audio_buffer)
                
                self.assertTrue(result)
                
    def test_detect_pattern_similarity_no_match(self):
        """Test _detect_pattern_similarity returns False when pattern doesn't match."""
        detector = SoundDetector(reference_audio_path=self.reference_audio_path)
        
        # Create audio buffer of correct size
        audio_buffer = np.random.random(detector.buffer_size).astype(np.float32)
        
        # Mock the DTW analyzer to return no match
        with patch.object(detector.dtw_analyzer, 'is_pattern_match', return_value=False):
            with patch.object(detector.dtw_analyzer, 'get_similarity_score', return_value=0.8):
                result = detector._detect_pattern_similarity(audio_buffer)
                
                self.assertFalse(result)
                
    def test_audio_buffer_management(self):
        """Test that audio buffer is properly managed with maxlen."""
        detector = SoundDetector(reference_audio_path=self.reference_audio_path)
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        # Fill buffer beyond its capacity
        chunk_size = 1024
        num_chunks = (detector.buffer_size // chunk_size) + 2  # Exceed buffer size
        
        with patch.object(detector, '_detect_pattern_similarity', return_value=False):
            for _ in range(num_chunks):
                audio_data = np.random.random(chunk_size).astype(np.float32)
                detector.process_audio_chunk(audio_data)
        
        # Buffer should not exceed its maximum size
        self.assertEqual(len(detector.audio_buffer), detector.buffer_size)
        
    def test_empty_audio_data(self):
        """Test handling of empty audio data."""
        detector = SoundDetector(reference_audio_path=self.reference_audio_path)
        callback = MagicMock()
        detector.set_detection_callback(callback)
        
        empty_data = np.array([])
        
        # Should not raise an error
        detector.process_audio_chunk(empty_data)
        
        # Callback should not be called
        callback.assert_not_called()


if __name__ == '__main__':
    unittest.main()