from flask import Flask, request, jsonify, g
from servo_controller.servo_controller import ServoController
from servo_controller.otp_manager import OTPManager
from sound_detect.line_service import create_line_service
from sound_detect.sound_detector import SoundDetector
import os
import atexit

BASE_URL = "TODO_HERE"
app = Flask(__name__)

def initialize_services():
    servo_controller = ServoController(pin=18)
    otp_manager = OTPManager(expiry_seconds=30)
    
    def generate_otp_for_notification():
        """Generate OTP for sound detection notifications"""
        return otp_manager.generate_otp()

    line = create_line_service(os.environ["CHANNEL_ACCESS_TOKEN"])
    
    def on_detection():
        print("Detected target frequencies!")
        otp = otp_manager().generate_otp()
        url = BASEURL + f"?otp={otp}"
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
    
    if audio_capture.start_capture(detector.process_audio_chunk):
        try:
            while True:
                time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            audio_capture.stop_capture()
    else:
        print("Failed to start audio detection")

def cleanup_services():
    """Cleanup shared services at app shutdown"""
    if _servo_controller:
        _servo_controller.cleanup()


@app.route('/unlock', methods=['POST'])
def unlock():
    println(f"g.count={g.count}")
    g.count += 1
    data = request.get_json()
    if not data:
        return jsonify({'status': 'fail', 'message': 'No JSON data provided'}), 400
    
    otp = data.get('otp')
    
    if not otp:
        return jsonify({'status': 'fail', 'message': 'OTP is required'}), 400
    
    if not g.otp_manager.validate_otp(otp):
        return jsonify({'status': 'fail', 'message': 'Invalid or expired OTP'}), 401
    
    try:
        g.servo_controller.unlock()
        
        return jsonify({
            'status': 'success',
            'message': f'Servo unlocked to {g.servo_controller.unlock_angle} degrees',
            'angle': g.servo_controller.unlock_angle
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
        'active_otps': g.otp_manager.get_active_otp_count()
    })

if __name__ == '__main__':
    initialize_services()
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        cleanup_services()
