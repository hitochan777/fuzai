import unittest
from unittest.mock import Mock, patch, MagicMock
from email_service import EmailNotificationService, create_email_service


class TestEmailNotificationService(unittest.TestCase):
    
    def setUp(self):
        self.service = EmailNotificationService(
            api_key="re_test_api_key",
            from_email="test@example.com",
            to_emails=["recipient@example.com"]
        )
    
    
    @patch('email_service.resend.Emails.send')
    def test_broadcast_message_success(self, mock_send):
        """Test successful broadcast message sending"""
        mock_send.return_value = {"id": "email_123"}
        
        messages = [
            {"type": "text", "text": "Test message 1"},
            {"type": "text", "text": "Test message 2"}
        ]
        
        result = self.service.broadcast_message(messages)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["data"]["recipients"], ["recipient@example.com"])
        self.assertEqual(result["data"]["id"], "email_123")
        mock_send.assert_called_once_with({
            "from": "test@example.com",
            "to": ["recipient@example.com"],
            "subject": "Sound Detection Alert",
            "text": "Test message 1\nTest message 2"
        })
    
    def test_broadcast_message_empty_messages(self):
        """Test broadcast message with empty messages list"""
        messages = []
        
        result = self.service.broadcast_message(messages)
        
        self.assertFalse(result["success"])
        self.assertIn("No text content found", result["error"])
    
    @patch('email_service.resend.Emails.send')
    def test_broadcast_message_resend_error(self, mock_send):
        """Test broadcast message with Resend error"""
        mock_send.side_effect = Exception("Resend API error")
        
        messages = [{"type": "text", "text": "Test message"}]
        
        result = self.service.broadcast_message(messages)
        
        self.assertFalse(result["success"])
        self.assertIn("Resend API error", result["error"])
    
    def test_create_email_service_factory(self):
        """Test factory function creates EmailNotificationService correctly"""
        service = create_email_service(
            api_key="re_test_key",
            from_email="sender@test.com",
            to_emails=["recipient1@test.com", "recipient2@test.com"]
        )
        
        self.assertIsInstance(service, EmailNotificationService)
        self.assertEqual(service.api_key, "re_test_key")
        self.assertEqual(service.from_email, "sender@test.com")
        self.assertEqual(service.to_emails, ["recipient1@test.com", "recipient2@test.com"])


if __name__ == "__main__":
    unittest.main()
