import numpy as np
import pyaudio
import threading
import time
from typing import List, Callable, Optional


class FrequencyDetector:
    def __init__(self, 
                 sample_rate: int = 44100,
                 chunk_size: int = 4096,
                 target_frequencies: List[float] = None,
                 frequency_tolerance: float = 50.0,
                 detection_threshold: float = 0.1,
                 detection_duration: float = 0.5):
        """
        Initialize frequency detector for microphone input
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Number of samples per audio chunk
            target_frequencies: List of frequencies to detect in Hz
            frequency_tolerance: Tolerance range for frequency matching in Hz
            detection_threshold: Minimum amplitude threshold for detection (0.0-1.0)
            detection_duration: Minimum duration in seconds for sustained detection
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.target_frequencies = target_frequencies or [440.0, 880.0, 1320.0]  # A4, A5, E6
        self.frequency_tolerance = frequency_tolerance
        self.detection_threshold = detection_threshold
        self.detection_duration = detection_duration
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_listening = False
        self.detection_callback = None
        self.detection_thread = None
        
        # Detection state tracking
        self.frequency_detection_times = {freq: [] for freq in self.target_frequencies}
        
    def set_target_frequencies(self, frequencies: List[float]):
        """Set the list of target frequencies to detect"""
        self.target_frequencies = frequencies
        self.frequency_detection_times = {freq: [] for freq in frequencies}
        
    def set_detection_callback(self, callback: Callable[[List[float]], None]):
        """Set callback function to be called when target frequencies are detected"""
        self.detection_callback = callback
        
    def _find_dominant_frequencies(self, audio_data: np.ndarray, num_peaks: int = 10) -> List[tuple]:
        """
        Find dominant frequencies in audio data using FFT
        
        Returns:
            List of (frequency, amplitude) tuples sorted by amplitude
        """
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
        
    def _is_frequency_match(self, detected_freq: float, target_freq: float) -> bool:
        """Check if detected frequency matches target within tolerance"""
        return abs(detected_freq - target_freq) <= self.frequency_tolerance
        
    def _detect_target_frequencies(self, audio_data: np.ndarray) -> List[float]:
        """
        Detect target frequencies in audio data
        
        Returns:
            List of detected target frequencies
        """
        dominant_freqs = self._find_dominant_frequencies(audio_data)
        detected_targets = []
        current_time = time.time()
        
        # Normalize amplitude threshold
        if dominant_freqs:
            max_amplitude = max(freq[1] for freq in dominant_freqs)
            threshold_amplitude = max_amplitude * self.detection_threshold
        else:
            return detected_targets
            
        for target_freq in self.target_frequencies:
            # Check if any dominant frequency matches this target
            for detected_freq, amplitude in dominant_freqs:
                if (self._is_frequency_match(detected_freq, target_freq) and 
                    amplitude >= threshold_amplitude):
                    
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
        
    def _audio_callback(self):
        """Main audio processing loop"""
        while self.is_listening:
            try:
                # Read audio data
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.float32)
                
                # Detect target frequencies
                detected_frequencies = self._detect_target_frequencies(audio_data)
                
                # Call detection callback if frequencies found
                if detected_frequencies and self.detection_callback:
                    self.detection_callback(detected_frequencies)
                    
            except Exception as e:
                print(f"Audio processing error: {e}")
                
    def start_listening(self) -> bool:
        """
        Start listening for target frequencies
        
        Returns:
            True if successfully started, False otherwise
        """
        if self.is_listening:
            return True
            
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_listening = True
            
            # Start detection thread
            self.detection_thread = threading.Thread(target=self._audio_callback, daemon=True)
            self.detection_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start audio stream: {e}")
            return False
            
    def stop_listening(self):
        """Stop listening for frequencies"""
        self.is_listening = False
        
        if self.detection_thread:
            self.detection_thread.join(timeout=1.0)
            self.detection_thread = None
            
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
    def get_current_spectrum(self, duration: float = 1.0) -> Optional[List[tuple]]:
        """
        Get current frequency spectrum for analysis
        
        Args:
            duration: Duration in seconds to analyze
            
        Returns:
            List of (frequency, amplitude) tuples or None if not listening
        """
        if not self.is_listening:
            return None
            
        try:
            # Collect audio data for specified duration
            samples_needed = int(duration * self.sample_rate)
            chunks_needed = (samples_needed + self.chunk_size - 1) // self.chunk_size
            
            audio_buffer = []
            for _ in range(chunks_needed):
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.float32)
                audio_buffer.extend(audio_data)
                
            # Trim to exact duration
            audio_buffer = np.array(audio_buffer[:samples_needed])
            
            return self._find_dominant_frequencies(audio_buffer, num_peaks=20)
            
        except Exception as e:
            print(f"Error getting spectrum: {e}")
            return None
            
    def __del__(self):
        """Cleanup on destruction"""
        self.stop_listening()
        if hasattr(self, 'audio'):
            self.audio.terminate()
