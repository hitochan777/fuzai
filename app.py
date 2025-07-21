from flask import Flask, request, jsonify, g
from servo_controller import ServoController
from otp_manager import OTPManager
from line_service import create_line_service
from sound_detector import SoundDetector
from audio_capture import AudioCapture
import os
import atexit
import time

BASE_URL = "TODO_HERE"
app = Flask(__name__)

def initialize_services(app):
    servo_controller = ServoController(pin=18)
    otp_manager = OTPManager(expiry_seconds=30)
    line = create_line_service(os.environ["CHANNEL_ACCESS_TOKEN"])
    
    def on_detection():
        print("Detected target frequencies!")
        otp = otp_manager.generate_otp()
        url = BASE_URL + f"?otp={otp}"
        line.broadcast_message([
          {
            "type": "text",
            "text": f"Intercom rang just now: {url}"
          }
        ])

    # Create detector with common musical frequencies
    detector = SoundDetector(
        target_frequencies=[502, 648],
        detection_threshold=0.2,
        detection_duration=3.0,
    )
    detector.set_detection_callback(on_detection)
    
    # Create audio capture
    audio_capture = AudioCapture(
        sample_rate=detector.sample_rate,
        chunk_size=detector.chunk_size
    )
    
    print("Starting frequency detection...")
    print(f"Target frequencies: {detector.target_frequencies}")
    
    print("Press Ctrl+C to stop")
    audio_capture.start_capture(detector.process_audio_chunk)
    # audio_capture.stop_capture()

    app.otp_manager = otp_manager
    app.servo_controller = servo_controller

@app.route('/unlock', methods=['POST'])
def unlock():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400
    
    otp = data.get('otp')
    
    if not otp:
        return jsonify({'status': 'error', 'message': 'OTP is required'}), 400
    
    if not app.otp_manager.validate_otp(otp):
        return jsonify({'status': 'error', 'message': 'Invalid or expired OTP'}), 401
    
    try:
        app.servo_controller.unlock()
        
        return jsonify({
            'status': 'success',
            'message': f'unlocked',
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy', 
        'message': 'Servo controller is running',
        'active_otps': app.otp_manager.get_active_otp_count()
    })

if __name__ == '__main__':
    initialize_services(app)
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        pass
    # TODO: clean up services
