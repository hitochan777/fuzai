import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from image_capturer import ImageCapturer


class TestImageCapturer(unittest.TestCase):
    """Test cases for ImageCapturer class"""

    @patch('cv2.VideoCapture')
    def test_capture_image_returns_frame(self, mock_video_capture):
        """Test that capture_image returns a frame from the camera"""
        mock_cap = Mock()
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, mock_frame)
        mock_video_capture.return_value = mock_cap

        capturer = ImageCapturer()
        frame = capturer.capture_image()

        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (480, 640, 3))

    @patch('cv2.VideoCapture')
    def test_capture_image_returns_none_on_failure(self, mock_video_capture):
        """Test that capture_image returns None when camera read fails"""
        mock_cap = Mock()
        mock_cap.read.return_value = (False, None)
        mock_video_capture.return_value = mock_cap

        capturer = ImageCapturer()
        frame = capturer.capture_image()

        self.assertIsNone(frame)

    @patch('cv2.VideoCapture')
    def test_context_manager_releases_camera(self, mock_video_capture):
        """Test that context manager properly releases camera on exit"""
        mock_cap = Mock()
        mock_video_capture.return_value = mock_cap

        with ImageCapturer() as capturer:
            self.assertIsNotNone(capturer)

        mock_cap.release.assert_called_once()

    @patch('cv2.VideoCapture')
    def test_context_manager_releases_on_exception(self, mock_video_capture):
        """Test that context manager releases camera even when exception occurs"""
        mock_cap = Mock()
        mock_video_capture.return_value = mock_cap

        try:
            with ImageCapturer() as capturer:
                raise ValueError("Test exception")
        except ValueError:
            pass

        mock_cap.release.assert_called_once()


if __name__ == '__main__':
    unittest.main()
