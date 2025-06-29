from sound_detect import FrequencyDetector
from line_service import create_line_service
import os
import time


def main():
    line = create_line_service(os.environ["CHANNEL_ACCESS_TOKEN"])
    def on_detection(frequencies):
        print(f"Detected target frequencies: {frequencies}")
        line.broadcast_message([
          {
            "type": "text",
            "text": "Intercom rang just now"
          }
        ])

    # Create detector with common musical frequencies
    detector = FrequencyDetector(
        target_frequencies=[440.0, 880.0, 1320.0],  # A4, A5, E6
        detection_threshold=0.2,
        detection_duration=1.0
    )
    
    detector.set_detection_callback(on_detection)
    
    print("Starting frequency detection...")
    print(f"Target frequencies: {detector.target_frequencies}")
    print("Press Ctrl+C to stop")
    
    if detector.start_listening():
        try:
            while True:
                time.sleep(1)
                
                # Get current spectrum every 2 seconds for debugging
                spectrum = detector.get_current_spectrum(0.5)
                if spectrum:
                    top_freqs = spectrum[:3]
                    print(f"Top frequencies: {[(f'{freq:.1f}Hz', f'{amp:.3f}') for freq, amp in top_freqs]}")
                    
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            detector.stop_listening()
    else:
        print("Failed to start audio detection")


if __name__ == "__main__":
    main()
