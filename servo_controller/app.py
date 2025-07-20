from flask import Flask, request, jsonify
from servo_controller import ServoController
from otp_manager import OTPManager
from sound_detection import IntercomSoundMonitor
import os
import atexit

app = Flask(__name__)

# Global service instances
servo_controller = None
otp_manager = None
sound_monitor = None

def initialize_services():
    """Initialize all service classes"""
    global servo_controller, otp_manager, sound_monitor
    
    servo_controller = ServoController(pin=18)
    otp_manager = OTPManager(expiry_seconds=30)
    
    def generate_otp_for_notification():
        """Generate OTP for sound detection notifications"""
        return otp_manager.generate_otp()
    
    channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN')
    if channel_access_token:
        sound_monitor = IntercomSoundMonitor(
            channel_access_token=channel_access_token,
            notification_callback=generate_otp_for_notification,
            server_url="http://localhost:5000"
        )
        sound_monitor.start_monitoring()
        
        def cleanup_sound_monitor():
            if sound_monitor:
                sound_monitor.stop_monitoring()
        
        atexit.register(cleanup_sound_monitor)
        print("Intercom sound monitoring enabled")
    else:
        print("Warning: CHANNEL_ACCESS_TOKEN not set, sound monitoring disabled")

def cleanup_services():
    """Cleanup all services"""
    if servo_controller:
        servo_controller.cleanup()
    if sound_monitor:
        sound_monitor.stop_monitoring()


@app.route('/unlock', methods=['POST'])
def unlock():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'fail', 'message': 'No JSON data provided'}), 400
    
    otp = data.get('otp')
    
    if not otp:
        return jsonify({'status': 'fail', 'message': 'OTP is required'}), 400
    
    if not otp_manager.validate_otp(otp):
        return jsonify({'status': 'fail', 'message': 'Invalid or expired OTP'}), 401
    
    try:
        servo_controller.unlock()
        
        return jsonify({
            'status': 'success',
            'message': f'Servo unlocked to {servo_controller.unlock_angle} degrees',
            'angle': servo_controller.unlock_angle
        })
    except ValueError as e:
        return jsonify({'status': 'fail', 'message': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'status': 'fail', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy', 
        'message': 'Servo controller is running',
        'active_otps': otp_manager.get_active_otp_count()
    })

if __name__ == '__main__':
    initialize_services()
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        cleanup_services()
