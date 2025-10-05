import unittest
from unittest.mock import Mock, patch, MagicMock
from slack_service import SlackNotificationService, create_slack_service


class TestSlackNotificationService(unittest.TestCase):

    def setUp(self):
        self.service = SlackNotificationService(
            webhook_url="https://hooks.slack.com/services/test/webhook/url",
            channel="#test-channel",
            username="test-bot"
        )


    @patch('slack_service.requests.post')
    def test_broadcast_message_with_valid_messages_sends_successfully(self, mock_post):
        """Test successful broadcast message sending"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        messages = [
            {"type": "text", "text": "Test message 1"},
            {"type": "text", "text": "Test message 2"}
        ]

        result = self.service.broadcast_message(messages)

        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["data"]["text"], "Test message 1\nTest message 2")
        self.assertEqual(result["data"]["channel"], "#test-channel")
        self.assertEqual(result["data"]["username"], "test-bot")
        mock_post.assert_called_once_with(
            "https://hooks.slack.com/services/test/webhook/url",
            json={
                "text": "Test message 1\nTest message 2",
                "channel": "#test-channel",
                "username": "test-bot"
            },
            headers={"Content-Type": "application/json"}
        )

    @patch('slack_service.requests.post')
    def test_broadcast_message_without_optional_params_sends_successfully(self, mock_post):
        """Test successful broadcast message sending without channel/username"""
        service = SlackNotificationService("https://hooks.slack.com/services/test/webhook/url")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        messages = [{"type": "text", "text": "Test message"}]

        result = service.broadcast_message(messages)

        self.assertTrue(result["success"])
        mock_post.assert_called_once_with(
            "https://hooks.slack.com/services/test/webhook/url",
            json={"text": "Test message"},
            headers={"Content-Type": "application/json"}
        )

    def test_broadcast_message_with_empty_messages_returns_error(self):
        """Test broadcast message with empty messages list"""
        messages = []

        result = self.service.broadcast_message(messages)

        self.assertFalse(result["success"])
        self.assertIn("No text content found", result["error"])

    def test_broadcast_message_with_non_text_messages_returns_error(self):
        """Test broadcast message with non-text message types"""
        messages = [{"type": "image", "url": "http://example.com/image.jpg"}]

        result = self.service.broadcast_message(messages)

        self.assertFalse(result["success"])
        self.assertIn("No text content found", result["error"])

    @patch('slack_service.requests.post')
    def test_broadcast_message_with_slack_error_returns_error(self, mock_post):
        """Test broadcast message with Slack webhook error"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "invalid_payload"
        mock_post.return_value = mock_response

        messages = [{"type": "text", "text": "Test message"}]

        result = self.service.broadcast_message(messages)

        self.assertFalse(result["success"])
        self.assertEqual(result["status_code"], 400)
        self.assertIn("Slack API error", result["error"])

    @patch('slack_service.requests.post')
    def test_broadcast_message_with_network_error_returns_error(self, mock_post):
        """Test broadcast message with network error"""
        mock_post.side_effect = Exception("Network error")

        messages = [{"type": "text", "text": "Test message"}]

        result = self.service.broadcast_message(messages)

        self.assertFalse(result["success"])
        self.assertIn("Network error", result["error"])

    def test_create_slack_service_with_all_parameters_returns_configured_instance(self):
        """Test factory function creates SlackNotificationService with all parameters"""
        service = create_slack_service(
            webhook_url="https://hooks.slack.com/test",
            channel="#alerts",
            username="alert-bot"
        )

        self.assertIsInstance(service, SlackNotificationService)
        self.assertEqual(service.webhook_url, "https://hooks.slack.com/test")
        self.assertEqual(service.channel, "#alerts")
        self.assertEqual(service.username, "alert-bot")

    def test_create_slack_service_with_minimal_parameters_returns_configured_instance(self):
        """Test factory function creates SlackNotificationService with minimal parameters"""
        service = create_slack_service("https://hooks.slack.com/test")

        self.assertIsInstance(service, SlackNotificationService)
        self.assertEqual(service.webhook_url, "https://hooks.slack.com/test")
        self.assertIsNone(service.channel)
        self.assertIsNone(service.username)


if __name__ == "__main__":
    unittest.main()