import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from image_capturer import ImageCapturer


class TestImageCapturer(unittest.TestCase):
    """Test cases for ImageCapturer class"""

    @patch('cv2.VideoCapture')
    def test_init_opens_camera(self, mock_video_capture):
        """Test that initialization opens the camera with default device"""
        capturer = ImageCapturer()
        mock_video_capture.assert_called_once_with(0)

    @patch('cv2.VideoCapture')
    def test_init_with_custom_device(self, mock_video_capture):
        """Test that initialization can use a custom camera device"""
        capturer = ImageCapturer(camera_index=1)
        mock_video_capture.assert_called_once_with(1)

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
    @patch('cv2.imwrite')
    def test_save_image(self, mock_imwrite, mock_video_capture):
        """Test that save_image captures and saves frame to file"""
        mock_cap = Mock()
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, mock_frame)
        mock_video_capture.return_value = mock_cap

        capturer = ImageCapturer()
        result = capturer.save_image('test.jpg')

        self.assertTrue(result)
        mock_imwrite.assert_called_once()

    @patch('cv2.VideoCapture')
    def test_release_closes_camera(self, mock_video_capture):
        """Test that release method closes the camera"""
        mock_cap = Mock()
        mock_video_capture.return_value = mock_cap

        capturer = ImageCapturer()
        capturer.release()

        mock_cap.release.assert_called_once()


if __name__ == '__main__':
    unittest.main()
