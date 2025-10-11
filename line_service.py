import requests
import json
from typing import Optional, Dict, Any, List, Union
from notifier import Notifier


class LineMessagingService(Notifier):
    """Service class for sending messages via LINE Messaging API"""
    
    def __init__(self, channel_access_token: str):
        """
        Initialize LINE Messaging Service
        
        Args:
            channel_access_token: LINE Channel Access Token
        """
        self.channel_access_token = channel_access_token
        self.base_url = "https://api.line.me/v2/bot"
        self.headers = {
            "Authorization": f"Bearer {channel_access_token}",
            "Content-Type": "application/json"
        }

    
    def broadcast_message(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send broadcast message to all friends
        
        Args:
            messages: List of message objects
            
        Returns:
            Dict containing response data or error information
        """
        url = f"{self.base_url}/message/broadcast"
        payload = {
            "messages": messages
        }
        
        return self._send_request(url, payload)
    
    def _send_request(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send HTTP request to LINE API
        
        Args:
            url: API endpoint URL
            payload: Request payload
            
        Returns:
            Dict containing response data or error information
        """
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json() if response.content else None
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_data.get("message", "Unknown error"),
                    "details": error_data.get("details", [])
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }

    def send_notification(
        self,
        message: str,
        image_data: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Send notification via LINE (implements Notifier interface)

        Note: LINE doesn't support direct image upload without hosting,
        so image_data is ignored.

        Args:
            message: The message text to send
            image_data: Ignored (LINE requires hosted image URLs)

        Returns:
            Dict containing response data or error information
        """
        return self.broadcast_message([
            {
                "type": "text",
                "text": message
            }
        ])


def create_line_service(channel_access_token: str) -> LineMessagingService:
    """
    Factory function to create a LINE messaging service instance
    
    Args:
        channel_access_token: LINE Channel Access Token
        
    Returns:
        LineMessagingService instance
    """
    return LineMessagingService(channel_access_token)
