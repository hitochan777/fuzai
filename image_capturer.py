import cv2
from typing import Optional
import numpy as np


class ImageCapturer:
    """Captures images from a camera device"""

    def __init__(self, camera_index: int = 0):
        """
        Initialize the image capturer with a camera device.

        Args:
            camera_index: Camera device index (default: 0 for primary camera)
        """
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(camera_index)

    def capture_image(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the camera.

        Returns:
            numpy array containing the captured frame, or None if capture fails
        """
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None

    def save_image(self, filepath: str) -> bool:
        """
        Capture an image and save it to a file.

        Args:
            filepath: Path where the image should be saved

        Returns:
            True if image was successfully captured and saved, False otherwise
        """
        frame = self.capture_image()
        if frame is not None:
            cv2.imwrite(filepath, frame)
            return True
        return False

    def release(self):
        """Release the camera resource"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup camera resource"""
        self.release()
        return False  # Don't suppress exceptions


if __name__ == "__main__":
    # Test the ImageCapturer
    print("Testing ImageCapturer...")
    print("Capturing an image and saving to 'test_capture.jpg'")

    with ImageCapturer(camera_index=0) as capturer:
        success = capturer.save_image("test_capture.jpg")
        if success:
            print("✓ Image captured and saved successfully!")
        else:
            print("✗ Failed to capture image")
