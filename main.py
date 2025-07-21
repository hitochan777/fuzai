from sound_detector import SoundDetector
from line_service import create_line_service
from audio_capture import AudioCapture
import os
import time


def main():
    line = create_line_service(os.environ["CHANNEL_ACCESS_TOKEN"])
    
    def on_detection():
        print("Detected target frequencies!")
        line.broadcast_message([
          {
            "type": "text",
            "text": "Intercom rang just now"
          }
        ])

    # Create detector with common musical frequencies
    detector = SoundDetector(
        target_frequencies=[502, 648],
        detection_threshold=0.2,
        detection_duration=3.0,
    )
    
    detector.set_detection_callback(on_detection)
    
    # Create audio capture
    audio_capture = AudioCapture(
        sample_rate=detector.sample_rate,
        chunk_size=detector.chunk_size
    )
    
    print("Starting frequency detection...")
    print(f"Target frequencies: {detector.target_frequencies}")
    print("Press Ctrl+C to stop")
    
    if audio_capture.start_capture(detector.process_audio_chunk):
        try:
            while True:
                time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            audio_capture.stop_capture()
    else:
        print("Failed to start audio detection")


if __name__ == "__main__":
    main()
