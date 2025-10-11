import unittest
from unittest.mock import Mock, patch, MagicMock
import io
from slack_service import SlackMessagingService


class TestSlackMessagingService(unittest.TestCase):
    """Test cases for SlackMessagingService"""

    def setUp(self):
        """Set up test fixtures"""
        self.token = "xoxb-test-token"
        self.channel = "C1234567890"

    @patch('slack_service.WebClient')
    def test_init_creates_client(self, mock_web_client):
        """Test that initialization creates a Slack WebClient"""
        service = SlackMessagingService(self.token, self.channel)
        mock_web_client.assert_called_once_with(token=self.token)
        self.assertEqual(service.channel, self.channel)

    @patch('slack_service.WebClient')
    def test_send_message_success(self, mock_web_client):
        """Test sending a text message successfully"""
        mock_client = Mock()
        mock_client.chat_postMessage.return_value = {"ok": True, "ts": "1234567890.123456"}
        mock_web_client.return_value = mock_client

        service = SlackMessagingService(self.token, self.channel)
        result = service.send_message("Test message")

        self.assertTrue(result["success"])
        mock_client.chat_postMessage.assert_called_once_with(
            channel=self.channel,
            text="Test message"
        )

    @patch('slack_service.WebClient')
    def test_send_message_failure(self, mock_web_client):
        """Test handling of message sending failure"""
        mock_client = Mock()
        mock_client.chat_postMessage.side_effect = Exception("API Error")
        mock_web_client.return_value = mock_client

        service = SlackMessagingService(self.token, self.channel)
        result = service.send_message("Test message")

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @patch('slack_service.WebClient')
    def test_upload_image_success(self, mock_web_client):
        """Test uploading an image file successfully"""
        mock_client = Mock()
        mock_client.files_upload_v2.return_value = {
            "ok": True,
            "file": {"id": "F1234567890"}
        }
        mock_web_client.return_value = mock_client

        service = SlackMessagingService(self.token, self.channel)
        image_data = b"fake image data"
        result = service.upload_image(image_data, "test.jpg", "Test image")

        self.assertTrue(result["success"])
        self.assertEqual(result["file_id"], "F1234567890")
        mock_client.files_upload_v2.assert_called_once()

    @patch('slack_service.WebClient')
    def test_upload_image_failure(self, mock_web_client):
        """Test handling of image upload failure"""
        mock_client = Mock()
        mock_client.files_upload_v2.side_effect = Exception("Upload failed")
        mock_web_client.return_value = mock_client

        service = SlackMessagingService(self.token, self.channel)
        image_data = b"fake image data"
        result = service.upload_image(image_data, "test.jpg", "Test image")

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @patch('slack_service.WebClient')
    def test_send_message_with_image_success(self, mock_web_client):
        """Test sending a message with an image"""
        mock_client = Mock()
        mock_client.files_upload_v2.return_value = {
            "ok": True,
            "file": {"id": "F1234567890"}
        }
        mock_client.chat_postMessage.return_value = {"ok": True, "ts": "1234567890.123456"}
        mock_web_client.return_value = mock_client

        service = SlackMessagingService(self.token, self.channel)
        image_data = b"fake image data"
        result = service.send_message_with_image("Test message", image_data, "test.jpg")

        self.assertTrue(result["success"])
        mock_client.files_upload_v2.assert_called_once()
        # Verify message was sent after upload
        self.assertEqual(mock_client.chat_postMessage.call_count, 1)


if __name__ == '__main__':
    unittest.main()
