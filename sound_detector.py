import time
import numpy as np
from typing import List, Callable, Optional, Dict
from collections import defaultdict
from enum import Enum
from frequency_analyzer import FrequencyAnalyzer


class DetectionState(Enum):
    WAITING = "waiting"
    COMPLETED = "completed"


class SoundDetector:
    def __init__(self, 
                 sample_rate: int = 44100,
                 chunk_size: int = 4096,
                 target_frequencies: List[float] = None,
                 detection_threshold: float = 0.1,
                 detection_duration: float = 0.5,
                 throttle_duration: float = 10.0,
                 state_timeout: float = 5.0):
        """
        Initialize frequency detector for microphone input
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Number of samples per audio chunk
            target_frequencies: List of frequencies to detect in Hz (detected in sequence order)
            detection_threshold: Minimum amplitude threshold for detection (0.0-1.0)
            detection_duration: Minimum duration in seconds for sustained detection
            throttle_duration: Time in seconds to wait before allowing another detection callback
            state_timeout: Time in seconds to wait in current state before resetting to beginning
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.target_frequencies = target_frequencies or [440.0, 880.0, 1320.0]
        self.detection_threshold = detection_threshold
        self.detection_duration = detection_duration
        self.throttle_duration = throttle_duration
        self.state_timeout = state_timeout
        
        self.frequency_analyzer = FrequencyAnalyzer(sample_rate)
        self.detection_callback = None
        self.frequency_detection_times = defaultdict(list)
        self.last_detection_time = 0
        
        # State machine variables
        self.current_state = DetectionState.WAITING
        self.state_transition_time = time.time()
        self.current_frequency_index = 0  # Index of the frequency we're currently waiting for
        self.detected_frequencies = []  # Track which frequencies have been detected in sequence
        
    def set_detection_callback(self, callback: Callable[[], None]):
        """Set callback function to be called with detection result (True/False)"""
        self.detection_callback = callback
        
    def process_audio_chunk(self, audio_data: np.ndarray):
        """Process incoming audio chunk and return detection result"""
        if not self.detection_callback:
            return

        self._update_state_machine(audio_data)
        
        if self.current_state == DetectionState.COMPLETED:
            current_time = time.time()
            if current_time - self.last_detection_time >= self.throttle_duration:
                self.last_detection_time = current_time
                self.detection_callback()
                # Reset state machine after successful detection
                self._reset_state_machine()
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
                if not (any(self.frequency_analyzer.is_frequency_match(
                    detected_freq, target_freq *(i+1)) for i in range(3)) and 
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
    
    def _update_state_machine(self, audio_data: np.ndarray):
        """Update state machine based on detected frequencies"""
        if not self.target_frequencies:
            return
            
        current_time = time.time()
        detected_freqs = self._detect_target_frequencies(audio_data)
        
        # Check for timeout
        if (self.current_state == DetectionState.WAITING and 
            self.current_frequency_index and
            current_time - self.state_transition_time > self.state_timeout):
            self._reset_state_machine()
            return
        
        if self.current_state == DetectionState.WAITING:
            # Check if we've detected all frequencies in sequence
            if self.current_frequency_index >= len(self.target_frequencies):
                self.current_state = DetectionState.COMPLETED
                self.state_transition_time = current_time
                print(f"State: WAITING -> COMPLETED (all {len(self.target_frequencies)} frequencies detected)")
                return
            
            expected_freq = self.target_frequencies[self.current_frequency_index]
            
            # Check if we detected the expected frequency
            if expected_freq in detected_freqs:
                self.detected_frequencies.append(expected_freq)
                self.current_frequency_index += 1
                self.state_transition_time = current_time
                print(f"State: Detected frequency {self.current_frequency_index}/{len(self.target_frequencies)}: {expected_freq}Hz")
                
                # Check if this was the last frequency
                if self.current_frequency_index >= len(self.target_frequencies):
                    self.current_state = DetectionState.COMPLETED
                    print(f"State: WAITING -> COMPLETED (all {len(self.target_frequencies)} frequencies detected)")
    
    def _reset_state_machine(self):
        """Reset state machine to initial state"""
        self.current_state = DetectionState.WAITING
        self.current_frequency_index = 0
        self.detected_frequencies = []
        self.state_transition_time = time.time()
        print("State: Reset to WAITING")
    
    def get_current_state(self) -> DetectionState:
        """Get current state of the detection state machine"""
        return self.current_state
                
    def __del__(self):
        """Cleanup on destruction"""
        pass
