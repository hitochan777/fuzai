import resend
from typing import Optional, Dict, Any, List, Union


class EmailNotificationService:
    """Service class for sending email notifications via Resend SDK"""
    
    def __init__(self, api_key: str, from_email: str, to_emails: List[str]):
        """
        Initialize Email Notification Service with Resend SDK
        
        Args:
            api_key: Resend API key
            from_email: Sender email address
            to_emails: List of recipient email addresses
        """
        self.api_key = api_key
        self.from_email = from_email
        self.to_emails = to_emails
        # FIXME: changing global variable here so it can contaminate other instances
        resend.api_key = api_key

    
    def broadcast_message(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send broadcast email to all recipients
        
        Args:
            messages: List of message objects (expects 'text' type with 'text' content)
            
        Returns:
            Dict containing response data or error information
        """
        try:
            # Extract text content from messages (similar to LINE message format)
            email_content = ""
            for message in messages:
                if message.get("type") == "text":
                    email_content += message.get("text", "") + "\n"
            
            if not email_content.strip():
                return {
                    "success": False,
                    "error": "No text content found in messages",
                    "status_code": None
                }
            
            return self._send_email("Sound Detection Alert", email_content.strip())
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }
    
    def _send_email(self, subject: str, body: str) -> Dict[str, Any]:
        """
        Send email via Resend SDK
        
        Args:
            subject: Email subject
            body: Email body content
            
        Returns:
            Dict containing response data or error information
        """
        try:
            email_data = {
                "from": self.from_email,
                "to": self.to_emails,
                "subject": subject,
                "text": body
            }
            
            response = resend.Emails.send(email_data)
            
            return {
                "success": True,
                "status_code": 200,
                "data": {"recipients": self.to_emails, "subject": subject, "id": response.get("id")}
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }
    

def create_email_service(api_key: str, from_email: str, to_emails: List[str]) -> EmailNotificationService:
    """
    Factory function to create an email notification service instance
    
    Args:
        api_key: Resend API key
        from_email: Sender email address
        to_emails: List of recipient email addresses
        
    Returns:
        EmailNotificationService instance
    """
    return EmailNotificationService(api_key, from_email, to_emails)
