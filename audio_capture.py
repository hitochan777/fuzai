import numpy as np
import pyaudio
import threading
import time
from typing import Callable, Optional


class AudioCapture:
    def __init__(self, 
                 sample_rate: int = 44100,
                 chunk_size: int = 4096):
        """
        Initialize audio capture for microphone input
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Number of samples per audio chunk
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_capturing = False
        self.capture_thread = None
        
    def _read_audio_chunk(self) -> Optional[np.ndarray]:
        """Read a single audio chunk from the stream"""
        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            return np.frombuffer(data, dtype=np.float32)
        except Exception as e:
            print(f"Audio capture error: {e}")
            return None
    
    def _capture_loop(self, audio_callback: Callable[[np.ndarray], None]):
        """Main audio capture loop"""
        while self.is_capturing:
            audio_data = self._read_audio_chunk()
            assert audio_data is not None
            audio_callback(audio_data)
                
    def start_capture(self, audio_callback: Callable[[np.ndarray], None]) -> bool:
        """
        Start capturing audio from microphone
        
        Returns:
            True if successfully started, False otherwise
        """
        if self.is_capturing:
            return True
            
        try:
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_capturing = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True, args=[audio_callback])
            self.capture_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start audio capture: {e}")
            return False
            
    def stop_capture(self):
        """Stop capturing audio"""
        self.is_capturing = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=1.0)
            self.capture_thread = None
            
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
    def capture_for_duration(self, duration: float) -> Optional[np.ndarray]:
        """
        Capture audio for a specific duration
        
        Args:
            duration: Duration in seconds to capture
            
        Returns:
            Combined audio data or None if not capturing
        """
        if not self.is_capturing:
            return None
            
        samples_needed = int(duration * self.sample_rate)
        chunks_needed = (samples_needed + self.chunk_size - 1) // self.chunk_size
        
        audio_buffer = []
        for _ in range(chunks_needed):
            audio_data = self._read_audio_chunk()
            if audio_data is None:
                return None
            audio_buffer.extend(audio_data)
            
        return np.array(audio_buffer[:samples_needed])
            
    def __del__(self):
        """Cleanup on destruction"""
        self.stop_capture()
        self.audio.terminate()