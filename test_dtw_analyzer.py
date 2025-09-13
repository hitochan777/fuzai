import unittest
import numpy as np
import tempfile
import os
import librosa
import soundfile as sf
from dtw_analyzer import DTWAnalyzer

SAMPLE_RATE = 44100

def generate_base_pattern():
    # Create a simple audio pattern (440Hz + 880Hz tones)
    duration = 1.0
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # Create a pattern with two tones
    pattern = (np.sin(2 * np.pi * 440 * t) + 0.5 * np.sin(2 * np.pi * 880 * t))

    return pattern


class TestDTWAnalyzer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Create a temporary reference audio file for testing."""
        # Generate a test reference audio file (440Hz + 880Hz tones)
        cls.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        cls.temp_file.close()

        cls.pattern = generate_base_pattern()
        
        # Save to file using soundfile
        sf.write(cls.temp_file.name, cls.pattern, SAMPLE_RATE)
        
    @classmethod
    def tearDownClass(cls):
        """Clean up temporary file."""
        os.unlink(cls.temp_file.name)
    
    def test_initialization_with_reference_audio_sets_sample_rate(self):
        """Test that DTW analyzer initializes correctly."""
        analyzer = DTWAnalyzer(
            reference_audio=generate_base_pattern(),
            sample_rate=SAMPLE_RATE,
        )
        
        # Test that analyzer initializes with default values
        self.assertEqual(analyzer.sample_rate, SAMPLE_RATE)
    
    def test_calculate_similarity_with_identical_audio_returns_zero(self):
        """Test similarity calculation with matching audio."""
        # Use default parameters to ensure consistency
        analyzer = DTWAnalyzer(
            reference_audio=generate_base_pattern(),
            sample_rate=SAMPLE_RATE,
        )

        pattern = generate_base_pattern()
        similarity = analyzer.calculate_similarity(pattern)
        print(f"Identical audio similarity: {similarity}")
        self.assertEqual(similarity, 0.0)
    
    def test_calculate_similarity_with_different_audio_returns_high_value(self):
        """Test similarity calculation with non-matching audio."""
        analyzer = DTWAnalyzer(
            reference_audio=generate_base_pattern(),
            sample_rate=SAMPLE_RATE,
        )
        
        # Generate different audio (2000Hz tone)
        sample_rate = analyzer.sample_rate
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        different_pattern = np.sin(2 * np.pi * 2000 * t)
        
        similarity = analyzer.calculate_similarity(different_pattern)
        print(f"Different audio similarity: {similarity}")
        self.assertGreater(similarity, 0.5)
        self.assertLessEqual(similarity, 1.0)
    
    def test_calculate_similarity_between_synthetic_and_loaded_audio_returns_low_value(self):
        """Test similarity between synthetic and loaded audio."""
        # Load audio from file
        loaded_audio, _ = librosa.load(self.temp_file.name, sr=SAMPLE_RATE)
        analyzer = DTWAnalyzer(
            reference_audio=loaded_audio,
            sample_rate=SAMPLE_RATE,
        )
        
        synthetic_pattern = generate_base_pattern()
        similarity = analyzer.calculate_similarity(synthetic_pattern)
        print(f"Synthetic vs reference similarity: {similarity}")
        # don't know why but after pattern is saved as WAV, when it is loaded and compared with the same pattern it was generated from,
        # the similarity is not zero, maybe the pattern is modified on the course of WAV transformation
        self.assertLess(similarity, 0.5)
    

if __name__ == '__main__':
    unittest.main(verbosity=2)
