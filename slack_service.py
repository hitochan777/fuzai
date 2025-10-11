from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any, Optional
from notifier import Notifier


class SlackMessagingService(Notifier):
    """Service class for sending messages and images via Slack API"""

    def __init__(self, token: str, channel: str):
        """
        Initialize Slack Messaging Service

        Args:
            token: Slack Bot Token (starts with xoxb-)
            channel: Default channel ID or name to send messages to
        """
        self.client = WebClient(token=token)
        self.channel = channel

    def send_message(self, text: str, channel: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a text message to a Slack channel

        Args:
            text: Message text to send
            channel: Channel to send to (uses default if not specified)

        Returns:
            Dict containing success status and response data
        """
        target_channel = channel or self.channel
        try:
            response = self.client.chat_postMessage(
                channel=target_channel,
                text=text
            )
            return {
                "success": True,
                "timestamp": response["ts"],
                "channel": response.get("channel")
            }
        except SlackApiError as e:
            return {
                "success": False,
                "error": str(e.response["error"]),
                "status_code": e.response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def upload_image(
        self,
        image_data: bytes,
        filename: str,
        title: Optional[str] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload an image file directly to Slack

        Args:
            image_data: Binary image data
            filename: Name for the uploaded file
            title: Optional title for the image
            channel: Channel to share the image in (uses default if not specified)

        Returns:
            Dict containing success status and file information
        """
        target_channel = channel or self.channel
        try:
            response = self.client.files_upload_v2(
                channel=target_channel,
                file=image_data,
                filename=filename,
                title=title or filename
            )
            return {
                "success": True,
                "file_id": response["file"]["id"],
                "file_url": response["file"].get("permalink")
            }
        except SlackApiError as e:
            return {
                "success": False,
                "error": str(e.response["error"]),
                "status_code": e.response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def send_message_with_image(
        self,
        text: str,
        image_data: bytes,
        filename: str,
        title: Optional[str] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload an image and send a message with it

        Args:
            text: Message text to send
            image_data: Binary image data
            filename: Name for the uploaded file
            title: Optional title for the image
            channel: Channel to send to (uses default if not specified)

        Returns:
            Dict containing success status and response data
        """
        target_channel = channel or self.channel

        # Upload the image first
        upload_result = self.upload_image(image_data, filename, title, target_channel)

        if not upload_result["success"]:
            return upload_result

        # Send the message
        message_result = self.send_message(text, target_channel)

        return {
            "success": message_result["success"],
            "file_id": upload_result.get("file_id"),
            "file_url": upload_result.get("file_url"),
            "message_timestamp": message_result.get("timestamp"),
            "error": message_result.get("error")
        }

    def send_notification(
        self,
        message: str,
        image_data: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Send notification via Slack with optional image (implements Notifier interface)

        Args:
            message: The message text to send
            image_data: Optional image data as bytes

        Returns:
            Dict containing success status and response data
        """
        if image_data:
            return self.send_message_with_image(
                text=message,
                image_data=image_data,
                filename="intercom_capture.jpg",
                title="Intercom Detection"
            )
        else:
            return self.send_message(message)


def create_slack_service(token: str, channel: str) -> SlackMessagingService:
    """
    Factory function to create a Slack messaging service instance

    Args:
        token: Slack Bot Token
        channel: Default channel for messages

    Returns:
        SlackMessagingService instance
    """
    return SlackMessagingService(token, channel)
