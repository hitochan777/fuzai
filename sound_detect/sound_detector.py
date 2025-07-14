import time
import numpy as np
from typing import List, Callable, Optional, Dict
from collections import defaultdict
from frequency_analyzer import FrequencyAnalyzer


class SoundDetector:
    def __init__(self, 
                 sample_rate: int = 44100,
                 chunk_size: int = 4096,
                 target_frequencies: List[float] = None,
                 detection_threshold: float = 0.1,
                 detection_duration: float = 0.5,
                 min_matching_frequencies: int = 1,
                 throttle_duration: float = 10.0):
        """
        Initialize frequency detector for microphone input
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Number of samples per audio chunk
            target_frequencies: List of frequencies to detect in Hz
            detection_threshold: Minimum amplitude threshold for detection (0.0-1.0)
            detection_duration: Minimum duration in seconds for sustained detection
            min_matching_frequencies: Minimum number of target frequencies that must match for detection
            throttle_duration: Time in seconds to wait before allowing another detection callback
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.target_frequencies = target_frequencies or [440.0, 880.0, 1320.0]
        self.detection_threshold = detection_threshold
        self.detection_duration = detection_duration
        self.min_matching_frequencies = min_matching_frequencies
        self.throttle_duration = throttle_duration
        
        self.frequency_analyzer = FrequencyAnalyzer(sample_rate)
        self.detection_callback = None
        self.frequency_detection_times = defaultdict(list)
        self.last_detection_time = 0
        
    def set_detection_callback(self, callback: Callable[[], None]):
        """Set callback function to be called with detection result (True/False)"""
        self.detection_callback = callback
        
    def process_audio_chunk(self, audio_data: np.ndarray):
        """Process incoming audio chunk and return detection result"""
        if not self.detection_callback:
            return

        target_freqs = self._detect_target_frequencies(audio_data)
        if len(target_freqs) >= self.min_matching_frequencies:
            current_time = time.time()
            if current_time - self.last_detection_time >= self.throttle_duration:
                self.last_detection_time = current_time
                self.detection_callback()
            else:
                print("Detected by throttled")
            
    
    def _detect_target_frequencies(self, audio_data: np.ndarray) -> List[float]:
        """
        Detect target frequencies in audio data with sustained detection logic
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            True if minimum number of target frequencies are detected, False otherwise
        """
        dominant_freqs = self.frequency_analyzer.find_dominant_frequencies(audio_data)
        current_time = time.time()
        
        # Normalize amplitude threshold
        if not dominant_freqs:
            return []

        max_amplitude = max(freq[1] for freq in dominant_freqs)
        threshold_amplitude = max_amplitude * self.detection_threshold
            
        detected_targets = []
        for target_freq in self.target_frequencies:
            # Check if any dominant frequency matches this target
            for detected_freq, amplitude in dominant_freqs:
                if not (self.frequency_analyzer.is_frequency_match(
                    detected_freq, target_freq) and 
                    amplitude >= threshold_amplitude):
                    continue

                # Add detection time
                self.frequency_detection_times[target_freq].append(current_time)
                
                # Remove old detections (outside duration window)
                cutoff_time = current_time - self.detection_duration
                self.frequency_detection_times[target_freq] = [
                    t for t in self.frequency_detection_times[target_freq] 
                    if t >= cutoff_time
                ]
                
                # Check if we have sustained detection
                detection_count = len(self.frequency_detection_times[target_freq])
                min_detections = max(1, int(self.detection_duration * self.sample_rate / self.chunk_size))
                
                if detection_count >= min_detections:
                    detected_targets.append(target_freq)
                    break
                    
        return detected_targets
                
    def __del__(self):
        """Cleanup on destruction"""
        pass
