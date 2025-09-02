import time
import numpy as np
import librosa
import os
from typing import Callable
from collections import deque
from dtw_analyzer import DTWAnalyzer
from datetime import datetime


class SoundDetector:
    def __init__(self, 
                 reference_audio_path: str,
                 sample_rate: int = 8192,
                 chunk_size: int = 4098,
                 similarity_threshold: float = 0.8,
                 detection_duration: float = 0.1,
                 throttle_duration: float = 10.0,
        ):
        """
        Initialize DTW-based sound detector for microphone input
        
        Args:
            reference_audio_path: Path to reference audio file to match against
            sample_rate: Audio sample rate in Hz
            chunk_size: Number of samples per audio chunk
            similarity_threshold: DTW similarity threshold (0=perfect match, 1=no similarity)
            detection_duration: Minimum duration in seconds for sustained detection
            throttle_duration: Time in seconds to wait before allowing another detection callback
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.similarity_threshold = similarity_threshold
        self.detection_duration = detection_duration
        self.throttle_duration = throttle_duration
        
        # Load reference audio file
        self.reference_audio, _ = librosa.load(reference_audio_path, sr=sample_rate)
        self.reference_duration = len(self.reference_audio) / sample_rate
        
        self.dtw_analyzer = DTWAnalyzer(sample_rate=sample_rate, reference_audio=self.reference_audio)
        
        self.detection_callback = None
        self.pattern_detection_times = []
        self.last_detection_time = 0
        self.chunk_counter = 0
        self.processing_interval = int(os.getenv('PROCESSING_INTERVAL', '2'))  # Process every N chunks
        
        # Audio buffer to store latest n seconds of audio data
        self.buffer_size = int(self.reference_duration * sample_rate)
        self.audio_buffer = deque(maxlen=self.buffer_size)
        
    def set_detection_callback(self, callback: Callable[[], None]):
        """Set callback function to be called with detection result (True/False)"""
        self.detection_callback = callback
        
    def process_audio_chunk(self, audio_data: np.ndarray):
        """Process incoming audio chunk and return detection result"""
        start_time = time.time()
        
        if not self.detection_callback:
            return
        
        # Add new audio data to buffer (always)
        buffer_start = time.time()
        self.audio_buffer.extend(audio_data)
        buffer_time = time.time() - buffer_start
        
        # Skip processing some chunks to reduce CPU load
        self.chunk_counter = (self.chunk_counter + 1) % self.processing_interval
        if self.chunk_counter != 0:
            if os.getenv('DEBUG', '').lower() == 'true':
                print(f"Skipping chunk {self.chunk_counter} (interval={self.processing_interval})")
            return
        
        # Pattern detection timing
        detection_start = time.time()
        detected = self._detect_pattern_similarity(np.array(list(self.audio_buffer)))
        detection_time = time.time() - detection_start
        
        total_time = time.time() - start_time
        if os.getenv('DEBUG', '').lower() == 'true':
            print(f"Audio processing: buffer={buffer_time*1000:.1f}ms, detection={detection_time*1000:.1f}ms, total={total_time*1000:.1f}ms")
        
        if not detected:
            return

        current_time = time.time()
        if current_time - self.last_detection_time >= self.throttle_duration:
            self.last_detection_time = current_time
            self.detection_callback()
        else:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Detected by throttled")
            
    
    def _detect_pattern_similarity(self, audio_buffer: np.ndarray) -> bool:
        """
        Detect pattern similarity using DTW with sustained detection logic
        
        Args:
            audio_buffer: Audio samples as numpy array
            
        Returns:
            True if pattern matches reference with sustained detection, False otherwise
        """
        if len(audio_buffer) < self.buffer_size:
            return False
            
        similarity = self.dtw_analyzer.calculate_similarity(audio_buffer)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "similarity", similarity)
        if similarity <= self.similarity_threshold:
            return True
        
        return False
