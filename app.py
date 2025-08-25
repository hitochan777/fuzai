from flask import Flask, request, jsonify, g, render_template
from servo_controller import ServoController
from otp_manager import OTPManager
from line_service import create_line_service
# from email_service import create_email_service
from sound_detector import SoundDetector
from audio_capture import AudioCapture
import os
import atexit
import time

API_ENDPOINT = os.environ.get("BASE_URL")
app = Flask(__name__)

def initialize_services(app, servo_controller):
    otp_manager = OTPManager(expiry_seconds=30)
    line = create_line_service(os.environ["CHANNEL_ACCESS_TOKEN"])
    # email_service = create_email_service(
    #     api_key=os.environ["RESEND_API_KEY"],
    #     from_email=os.environ["FROM_EMAIL"],
    #     to_emails=os.environ["TO_EMAILS"].split(",")
    # )
    
    def on_detection():
        print("Detected target frequencies!")
        otp = otp_manager.generate_otp()
        url = API_ENDPOINT + f"/unlock?otp={otp}"
        result = line.broadcast_message([
          {
            "type": "text",
            "text": f"Intercom rang just now: {url}"
          }
        ])
        if not result["success"]:
            print(f"Failed to notify via email: {result}")

    # Create DTW-based detector with reference audio file
    reference_audio_path = os.environ.get("REFERENCE_AUDIO_PATH", "reference_intercom.wav")
    detector = SoundDetector(
        reference_audio_path=reference_audio_path,
        similarity_threshold=0.8,  # Higher threshold since 0=match, 1=no match
        detection_duration=0.2,
    )
    detector.set_detection_callback(on_detection)
    
    # Create audio capture
    audio_capture = AudioCapture(
        sample_rate=detector.sample_rate,
        chunk_size=detector.chunk_size
    )
    
    print("Starting DTW pattern detection...")
    print(f"Reference audio: {reference_audio_path}")
    print(f"Similarity threshold: {detector.similarity_threshold}")
    
    print("Press Ctrl+C to stop")
    audio_capture.start_capture(detector.process_audio_chunk)
    # audio_capture.stop_capture()

    app.otp_manager = otp_manager
    app.servo_controller = servo_controller

@app.route('/unlock', methods=['GET'])
def unlock():
    otp = request.args.get('otp')
    
    if not otp:
        return jsonify({'status': 'error', 'message': 'OTP is required'}), 400
    
    return render_template('unlock.html', otp=otp)

@app.route('/perform-unlock', methods=['POST'])
def perform_unlock():
    data = request.get_json()
    otp = data.get('otp') if data else None
    
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
    with ServoController() as servo:
        initialize_services(app, servo)
        try:
            app.run(host='0.0.0.0', port=5000, debug=False)
        finally:
            pass
