import requests
import json
from typing import Optional, Dict, Any, List, Union


class LineMessagingService:
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
    

def create_line_service(channel_access_token: str) -> LineMessagingService:
    """
    Factory function to create a LINE messaging service instance
    
    Args:
        channel_access_token: LINE Channel Access Token
        
    Returns:
        LineMessagingService instance
    """
    return LineMessagingService(channel_access_token)
