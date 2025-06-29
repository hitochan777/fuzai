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
    
    def push_message(self, to: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send push message to a user, group, or room
        
        Args:
            to: User ID, Group ID, or Room ID
            messages: List of message objects (up to 5 messages)
            
        Returns:
            Dict containing response data or error information
        """
        url = f"{self.base_url}/message/push"
        payload = {
            "to": to,
            "messages": messages
        }
        
        return self._send_request(url, payload)
    
    def reply_message(self, reply_token: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send reply message (used in webhook responses)
        
        Args:
            reply_token: Reply token from LINE webhook event
            messages: List of message objects (up to 5 messages)
            
        Returns:
            Dict containing response data or error information
        """
        url = f"{self.base_url}/message/reply"
        payload = {
            "replyToken": reply_token,
            "messages": messages
        }
        
        return self._send_request(url, payload)
    
    def multicast_message(self, to: List[str], messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send message to multiple users
        
        Args:
            to: List of user IDs (up to 500 users)
            messages: List of message objects (up to 5 messages)
            
        Returns:
            Dict containing response data or error information
        """
        url = f"{self.base_url}/message/multicast"
        payload = {
            "to": to,
            "messages": messages
        }
        
        return self._send_request(url, payload)
    
    def broadcast_message(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send broadcast message to all friends
        
        Args:
            messages: List of message objects (up to 5 messages)
            
        Returns:
            Dict containing response data or error information
        """
        url = f"{self.base_url}/message/broadcast"
        payload = {
            "messages": messages
        }
        
        return self._send_request(url, payload)
    
    def narrowcast_message(self, messages: List[Dict[str, Any]], 
                          recipient: Optional[Dict[str, Any]] = None,
                          filter_: Optional[Dict[str, Any]] = None,
                          limit: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send narrowcast message with targeting
        
        Args:
            messages: List of message objects (up to 5 messages)
            recipient: Recipient object for audience targeting
            filter_: Filter object for demographic filtering
            limit: Limit object for delivery limits
            
        Returns:
            Dict containing response data or error information
        """
        url = f"{self.base_url}/message/narrowcast"
        payload = {
            "messages": messages
        }
        
        if recipient:
            payload["recipient"] = recipient
        if filter_:
            payload["filter"] = filter_
        if limit:
            payload["limit"] = limit
        
        return self._send_request(url, payload)
    
    def create_text_message(self, text: str, quick_reply: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a text message object
        
        Args:
            text: Message text (up to 5000 characters)
            quick_reply: Quick reply object (optional)
            
        Returns:
            Text message object
        """
        message = {
            "type": "text",
            "text": text
        }
        
        if quick_reply:
            message["quickReply"] = quick_reply
        
        return message
    
    def create_sticker_message(self, package_id: str, sticker_id: str,
                              quick_reply: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a sticker message object
        
        Args:
            package_id: Package ID of the sticker
            sticker_id: Sticker ID
            quick_reply: Quick reply object (optional)
            
        Returns:
            Sticker message object
        """
        message = {
            "type": "sticker",
            "packageId": package_id,
            "stickerId": sticker_id
        }
        
        if quick_reply:
            message["quickReply"] = quick_reply
        
        return message
    
    def create_image_message(self, original_content_url: str, preview_image_url: str,
                            quick_reply: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create an image message object
        
        Args:
            original_content_url: URL of the original image
            preview_image_url: URL of the preview image
            quick_reply: Quick reply object (optional)
            
        Returns:
            Image message object
        """
        message = {
            "type": "image",
            "originalContentUrl": original_content_url,
            "previewImageUrl": preview_image_url
        }
        
        if quick_reply:
            message["quickReply"] = quick_reply
        
        return message
    
    def create_video_message(self, original_content_url: str, preview_image_url: str,
                            quick_reply: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a video message object
        
        Args:
            original_content_url: URL of the video file
            preview_image_url: URL of the preview image
            quick_reply: Quick reply object (optional)
            
        Returns:
            Video message object
        """
        message = {
            "type": "video",
            "originalContentUrl": original_content_url,
            "previewImageUrl": preview_image_url
        }
        
        if quick_reply:
            message["quickReply"] = quick_reply
        
        return message
    
    def create_audio_message(self, original_content_url: str, duration: int,
                            quick_reply: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create an audio message object
        
        Args:
            original_content_url: URL of the audio file
            duration: Length of audio file in milliseconds
            quick_reply: Quick reply object (optional)
            
        Returns:
            Audio message object
        """
        message = {
            "type": "audio",
            "originalContentUrl": original_content_url,
            "duration": duration
        }
        
        if quick_reply:
            message["quickReply"] = quick_reply
        
        return message
    
    def create_location_message(self, title: str, address: str, latitude: float, longitude: float,
                               quick_reply: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a location message object
        
        Args:
            title: Title of the location
            address: Address of the location
            latitude: Latitude of the location
            longitude: Longitude of the location
            quick_reply: Quick reply object (optional)
            
        Returns:
            Location message object
        """
        message = {
            "type": "location",
            "title": title,
            "address": address,
            "latitude": latitude,
            "longitude": longitude
        }
        
        if quick_reply:
            message["quickReply"] = quick_reply
        
        return message
    
    def create_flex_message(self, alt_text: str, contents: Dict[str, Any],
                           quick_reply: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a flex message object
        
        Args:
            alt_text: Alternative text for devices that don't support flex messages
            contents: Flex message container object
            quick_reply: Quick reply object (optional)
            
        Returns:
            Flex message object
        """
        message = {
            "type": "flex",
            "altText": alt_text,
            "contents": contents
        }
        
        if quick_reply:
            message["quickReply"] = quick_reply
        
        return message
    
    def send_text(self, to: str, text: str, quick_reply: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convenience method to send a text message
        
        Args:
            to: User ID, Group ID, or Room ID
            text: Message text
            quick_reply: Quick reply object (optional)
            
        Returns:
            Dict containing response data or error information
        """
        message = self.create_text_message(text, quick_reply)
        return self.push_message(to, [message])
    
    def reply_text(self, reply_token: str, text: str, quick_reply: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convenience method to reply with a text message
        
        Args:
            reply_token: Reply token from LINE webhook event
            text: Message text
            quick_reply: Quick reply object (optional)
            
        Returns:
            Dict containing response data or error information
        """
        message = self.create_text_message(text, quick_reply)
        return self.reply_message(reply_token, [message])
    
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


def create_line_service(channel_access_token: str) -> LineMessagingService:
    """
    Factory function to create a LINE messaging service instance
    
    Args:
        channel_access_token: LINE Channel Access Token
        
    Returns:
        LineMessagingService instance
    """
    return LineMessagingService(channel_access_token)