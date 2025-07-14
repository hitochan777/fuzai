#!/usr/bin/env python3
"""
Example showing the new inverted dependency architecture.

AudioCapture calls methods on SoundDetector, rather than 
SoundDetector managing AudioCapture internally.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from audio_capture import AudioCapture
from sound_detector import SoundDetector
import time


def detected_callback():
    """Called when target frequencies are detected"""
    print(f"Sound detected")


def main():
    print("Starting audio capture with frequency detection...")
    
    # Create frequency detector (no audio I/O concerns)
    detector = SoundDetector(
        target_frequencies=[440.0, 880.0, 1320.0],  # A4, A5, E6
        detection_threshold=0.1,
        detection_duration=0.5,
        min_matching_frequencies=1
    )
    
    # Set up detection callback
    detector.set_detection_callback(detected_callback)
    
    # Create audio capture (handles audio I/O)
    audio_capture = AudioCapture(sample_rate=44100, chunk_size=4096)
    
    # Start capturing audio
    if audio_capture.start_capture(detector.process_audio_chunk):
        print("✅ Audio capture started. Listening for target frequencies...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
        finally:
            audio_capture.stop_capture()
            print("✅ Audio capture stopped")
    else:
        print("❌ Failed to start audio capture")


if __name__ == "__main__":
    main()