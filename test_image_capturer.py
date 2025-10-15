import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import os
from image_capturer import ImageCapturer


class TestImageCapturer(unittest.TestCase):
    """Test cases for ImageCapturer class"""

    @patch('subprocess.run')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    @patch('os.path.exists')
    def test_capture_image_returns_bytes(self, mock_exists, mock_file, mock_run):
        """Test that capture_image returns image bytes from fswebcam"""
        mock_run.return_value = Mock(returncode=0)
        mock_exists.return_value = True

        capturer = ImageCapturer()
        image_bytes = capturer.capture_image()

        self.assertIsNotNone(image_bytes)
        self.assertEqual(image_bytes, b'fake_image_data')
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_capture_image_returns_none_on_failure(self, mock_run):
        """Test that capture_image returns None when fswebcam fails"""
        mock_run.return_value = Mock(returncode=1)

        capturer = ImageCapturer()
        image_bytes = capturer.capture_image()

        self.assertIsNone(image_bytes)

    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_save_image_creates_file(self, mock_exists, mock_run):
        """Test that save_image successfully saves to specified path"""
        mock_run.return_value = Mock(returncode=0)
        mock_exists.return_value = True

        capturer = ImageCapturer()
        result = capturer.save_image('/tmp/test.jpg')

        self.assertTrue(result)
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_save_image_returns_false_on_failure(self, mock_run):
        """Test that save_image returns False when fswebcam fails"""
        mock_run.return_value = Mock(returncode=1)

        capturer = ImageCapturer()
        result = capturer.save_image('/tmp/test.jpg')

        self.assertFalse(result)

    def test_context_manager_works(self):
        """Test that context manager properly initializes and cleans up"""
        with ImageCapturer() as capturer:
            self.assertIsNotNone(capturer)
            self.assertEqual(capturer.camera_index, 0)

    def test_context_manager_works_on_exception(self):
        """Test that context manager handles exceptions gracefully"""
        try:
            with ImageCapturer() as capturer:
                raise ValueError("Test exception")
        except ValueError:
            pass


if __name__ == '__main__':
    unittest.main()
