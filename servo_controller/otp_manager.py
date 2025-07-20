import random
import string
import threading
from datetime import datetime, timedelta

class OTPManager:
    def __init__(self, expiry_seconds=30, otp_length=6):
        self.expiry_seconds = expiry_seconds
        self.otp_length = otp_length
        self.otps = {}
        self.lock = threading.Lock()
    
    def generate_otp(self):
        otp = ''.join(random.choices(string.digits, k=self.otp_length))
        timestamp = datetime.now()
        
        with self.lock:
            self.otps[otp] = timestamp
        
        return otp
    
    def validate_otp(self, otp):
        self._cleanup_expired_otps()
        
        with self.lock:
            if otp not in self.otps:
                return False
            
            timestamp = self.otps[otp]
            if datetime.now() - timestamp > timedelta(seconds=self.expiry_seconds):
                del self.otps[otp]
                return False
            
            del self.otps[otp]
            return True
    
    def _cleanup_expired_otps(self):
        with self.lock:
            current_time = datetime.now()
            expired_keys = [
                key for key, timestamp in self.otps.items() 
                if current_time - timestamp > timedelta(seconds=self.expiry_seconds)
            ]
            for key in expired_keys:
                del self.otps[key]
    
    def get_active_otp_count(self):
        self._cleanup_expired_otps()
        with self.lock:
            return len(self.otps)