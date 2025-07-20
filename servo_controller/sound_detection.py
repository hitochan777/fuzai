import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'sound_detect'))

from sound_detector import SoundDetector
from line_service import LineMessagingService
import threading
import time
from typing import Callable, Optional

class IntercomSoundMonitor:
    def __init__(self, 
                 channel_access_token: str,
                 notification_callback: Callable[[], str],
                 server_url: str = "http://localhost:5000"):
        """
        Monitor for intercom sounds and send notifications
        
        Args:
            channel_access_token: LINE Channel Access Token
            notification_callback: Function to call when sound detected, should return OTP
            server_url: Base URL of the servo controller server
        """
        self.line_service = LineMessagingService(channel_access_token)
        self.notification_callback = notification_callback
        self.server_url = server_url
        self.sound_detector = None
        self.monitoring_thread = None
        self.is_running = False
        
    def _on_sound_detected(self):
        """Handle sound detection event"""
        try:
            otp = self.notification_callback()
            unlock_url = f"{self.server_url}/unlock"
            
            message = {
                "type": "text",
                "text": f"🔔 Intercom detected!\n\nClick to unlock:\n{unlock_url}\n\nOTP: {otp}\n\n⏰ Valid for 30 seconds"
            }
            
            self.line_service.broadcast_message([message])
            print(f"Notification sent with OTP: {otp}")
            
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    def start_monitoring(self, 
                        target_frequencies=None,
                        detection_threshold=0.1,
                        detection_duration=0.5):
        """Start monitoring for intercom sounds"""
        if self.is_running:
            return
            
        self.sound_detector = SoundDetector(
            target_frequencies=target_frequencies or [440.0, 880.0, 1320.0],
            detection_threshold=detection_threshold,
            detection_duration=detection_duration,
            throttle_duration=30.0
        )
        
        self.sound_detector.set_detection_callback(self._on_sound_detected)
        
        def monitor_loop():
            try:
                self.sound_detector.start_detection()
            except Exception as e:
                print(f"Sound detection error: {e}")
        
        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.is_running = True
        self.monitoring_thread.start()
        print("Intercom sound monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring for sounds"""
        self.is_running = False
        if self.sound_detector:
            self.sound_detector.stop_detection()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        print("Intercom sound monitoring stopped")