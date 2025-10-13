from flask import Flask, request, jsonify, g, render_template
from servo_controller import ServoController
from otp_manager import OTPManager
from line_service import create_line_service
from slack_service import create_slack_service
from email_service import create_email_service
from image_capturer import ImageCapturer
from sound_detector import SoundDetector
from audio_capture import AudioCapture
import os
import time

API_ENDPOINT = os.environ.get("BASE_URL")
app = Flask(__name__)


def create_notifier_from_env():
    """
    Factory function to create a notifier based on environment variables

    Returns:
        Tuple of (notifier, notifier_type)

    Raises:
        ValueError: If required environment variables are missing or notifier type is unsupported
    """
    notifier_type = os.environ.get("NOTIFIER_TYPE", "line").lower()

    if notifier_type == "slack":
        slack_token = os.environ.get("SLACK_BOT_TOKEN")
        slack_channel = os.environ.get("SLACK_CHANNEL")
        if not slack_token or not slack_channel:
            raise ValueError("SLACK_BOT_TOKEN and SLACK_CHANNEL must be set when using Slack notifier")
        return create_slack_service(slack_token, slack_channel), notifier_type
    elif notifier_type == "line":
        line_token = os.environ.get("CHANNEL_ACCESS_TOKEN")
        if not line_token:
            raise ValueError("CHANNEL_ACCESS_TOKEN must be set when using LINE notifier")
        return create_line_service(line_token), notifier_type
    elif notifier_type == "email":
        api_key = os.environ.get("RESEND_API_KEY")
        from_email = os.environ.get("FROM_EMAIL")
        to_emails = os.environ.get("TO_EMAILS")
        if not api_key or not from_email or not to_emails:
            raise ValueError("RESEND_API_KEY, FROM_EMAIL, and TO_EMAILS must be set when using Email notifier")
        return create_email_service(api_key, from_email, to_emails.split(",")), notifier_type
    else:
        raise ValueError(f"Unsupported notifier type: {notifier_type}. Use 'line', 'slack', or 'email'")


def capture_and_encode_image(image_capturer):
    """
    Capture an image from the camera and return as JPEG bytes

    Args:
        image_capturer: ImageCapturer instance

    Returns:
        Optional[bytes]: Image data as bytes, or None if capture fails
    """
    # capture_image() now returns bytes directly (JPEG format)
    return image_capturer.capture_image()


def initialize_services(app, servo_controller, image_capturer):
    otp_manager = OTPManager(expiry_seconds=30)
    notifier, notifier_type = create_notifier_from_env()

    def on_detection():
        print("Detected target frequencies!")
        otp = otp_manager.generate_otp()
        url = API_ENDPOINT + f"/unlock?otp={otp}"
        message = f"Intercom rang just now: {url}"
        image_bytes = capture_and_encode_image(image_capturer)
        result = notifier.send_notification(message, image_bytes)

        if not result["success"]:
            print(f"Failed to send notification via {notifier_type}: {result}")
        else:
            print(f"Notification sent successfully via {notifier_type}!")

    # Create DTW-based detector with reference audio file
    reference_audio_path = os.environ.get("REFERENCE_AUDIO_PATH", "reference_intercom.wav")
    detector = SoundDetector(
        reference_audio_path=reference_audio_path,
        similarity_threshold=0.82,  # Higher threshold since 0=match, 1=no match
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
    camera_index = int(os.environ.get("CAMERA_INDEX", "0"))
    with ServoController() as servo, ImageCapturer(camera_index=camera_index) as image_capturer:
        initialize_services(app, servo, image_capturer)
        try:
            app.run(host='0.0.0.0', port=5000, debug=False)
        finally:
            pass
