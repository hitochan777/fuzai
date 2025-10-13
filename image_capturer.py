import subprocess
import tempfile
import os
from typing import Optional


class ImageCapturer:
    """Captures images from a camera device using fswebcam"""

    def __init__(self, camera_index: int = 0):
        """
        Initialize the image capturer with a camera device.

        Args:
            camera_index: Camera device index (default: 0 for primary camera)
        """
        self.camera_index = camera_index
        self.device_path = f"/dev/video{camera_index}"

    def capture_image(self) -> Optional[bytes]:
        """
        Capture a single frame from the camera and return as bytes.

        Returns:
            bytes containing the captured image (JPEG format), or None if capture fails
        """
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Use fswebcam to capture image
            result = subprocess.run(
                ['fswebcam', '-d', self.device_path, '--no-banner', '-r', '640x480', tmp_path],
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and os.path.exists(tmp_path):
                with open(tmp_path, 'rb') as f:
                    image_bytes = f.read()
                return image_bytes
            return None
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def save_image(self, filepath: str) -> bool:
        """
        Capture an image and save it to a file.

        Args:
            filepath: Path where the image should be saved

        Returns:
            True if image was successfully captured and saved, False otherwise
        """
        result = subprocess.run(
            ['fswebcam', '-d', self.device_path, '--no-banner', '-r', '640x480', filepath],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    def release(self):
        """Release the camera resource (no-op for fswebcam)"""
        pass

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
