import numpy as np
from typing import List, Tuple


class FrequencyAnalyzer:
    def __init__(self, sample_rate: int = 44100, tolerance_range: float = 50.0):
        """
        Initialize frequency analyzer for FFT-based frequency detection
        
        Args:
            sample_rate: Audio sample rate in Hz
            tolerance_range: Tolerance range for frequency matching in Hz
        """
        self.sample_rate = sample_rate
        self.tolerance_range = tolerance_range
        
    def find_dominant_frequencies(self, audio_data: np.ndarray, num_peaks: int = 10) -> List[Tuple[float, float]]:
        """
        Find dominant frequencies in audio data using FFT
        
        Args:
            audio_data: Audio samples as numpy array
            num_peaks: Number of top frequency peaks to return
            
        Returns:
            List of (frequency, amplitude) tuples sorted by amplitude
        """
        if len(audio_data) == 0:
            return []
            
        # Apply window function to reduce spectral leakage
        windowed_data = audio_data * np.hanning(len(audio_data))
        
        # Compute FFT
        fft = np.fft.fft(windowed_data)
        magnitude = np.abs(fft)
        
        # Only use first half of FFT (positive frequencies)
        magnitude = magnitude[:len(magnitude)//2]
        
        # Create frequency bins
        freqs = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)[:len(magnitude)]
        
        # Find peaks
        peak_indices = np.argsort(magnitude)[-num_peaks:]
        peak_frequencies = [(freqs[i], magnitude[i]) for i in peak_indices if magnitude[i] > 0]
        
        # Sort by amplitude (descending)
        peak_frequencies.sort(key=lambda x: x[1], reverse=True)
        
        return peak_frequencies
        
    def is_frequency_match(self, detected_freq: float, target_freq: float, tolerance: float = None) -> bool:
        """
        Check if detected frequency matches target within tolerance
        
        Args:
            detected_freq: Detected frequency in Hz
            target_freq: Target frequency in Hz
            tolerance: Tolerance range in Hz (defaults to instance tolerance_range)
            
        Returns:
            True if frequencies match within tolerance
        """
        if tolerance is None:
            tolerance = self.tolerance_range
        return abs(detected_freq - target_freq) <= tolerance
        
    def get_frequency_spectrum(self, audio_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get full frequency spectrum of audio data
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            Tuple of (frequencies, magnitudes) arrays
        """
        if len(audio_data) == 0:
            return np.array([]), np.array([])
            
        # Apply window function
        windowed_data = audio_data * np.hanning(len(audio_data))
        
        # Compute FFT
        fft = np.fft.fft(windowed_data)
        magnitude = np.abs(fft)
        
        # Only use first half (positive frequencies)
        magnitude = magnitude[:len(magnitude)//2]
        freqs = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)[:len(magnitude)]
        
        return freqs, magnitude