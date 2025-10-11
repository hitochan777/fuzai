from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class Notifier(ABC):
    """Abstract base class for notification services"""

    @abstractmethod
    def send_notification(
        self,
        message: str,
        image_data: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Send a notification with optional image

        Args:
            message: The message text to send
            image_data: Optional image data as bytes

        Returns:
            Dict containing success status and response data
        """
        pass
