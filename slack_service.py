import requests
import json
from typing import Optional, Dict, Any, List, Union


class SlackNotificationService:
    """Service class for sending notifications via Slack Incoming Webhooks"""

    def __init__(self, webhook_url: str, channel: Optional[str] = None, username: Optional[str] = None):
        """
        Initialize Slack Notification Service

        Args:
            webhook_url: Slack Incoming Webhook URL
            channel: Optional channel to post to (overrides webhook default)
            username: Optional username for the bot (overrides webhook default)
        """
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username


    def broadcast_message(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send broadcast message to Slack channel

        Args:
            messages: List of message objects (expects 'text' type with 'text' content)

        Returns:
            Dict containing response data or error information
        """
        try:
            # Extract text content from messages (similar to LINE/email message format)
            slack_text = ""
            for message in messages:
                if message.get("type") == "text":
                    slack_text += message.get("text", "") + "\n"

            if not slack_text.strip():
                return {
                    "success": False,
                    "error": "No text content found in messages",
                    "status_code": None
                }

            return self._send_message(slack_text.strip())

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }

    def _send_message(self, text: str) -> Dict[str, Any]:
        """
        Send message to Slack via webhook

        Args:
            text: Message text content

        Returns:
            Dict containing response data or error information
        """
        try:
            payload = {
                "text": text
            }

            # Add optional parameters if specified
            if self.channel:
                payload["channel"] = self.channel
            if self.username:
                payload["username"] = self.username

            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": {"text": text, "channel": self.channel, "username": self.username}
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"Slack API error: {response.text}",
                    "details": []
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }


def create_slack_service(webhook_url: str, channel: Optional[str] = None, username: Optional[str] = None) -> SlackNotificationService:
    """
    Factory function to create a Slack notification service instance

    Args:
        webhook_url: Slack Incoming Webhook URL
        channel: Optional channel to post to (overrides webhook default)
        username: Optional username for the bot (overrides webhook default)

    Returns:
        SlackNotificationService instance
    """
    return SlackNotificationService(webhook_url, channel, username)