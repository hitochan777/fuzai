from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
import time
import random
import string
from datetime import datetime, timedelta
import threading

app = Flask(__name__)

SERVO_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

otps = {}
otp_lock = threading.Lock()

def angle_to_duty_cycle(angle):
    return 2 + (angle / 18)

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def cleanup_expired_otps():
    with otp_lock:
        current_time = datetime.now()
        expired_keys = [key for key, (otp, timestamp) in otps.items() 
                       if current_time - timestamp > timedelta(seconds=30)]
        for key in expired_keys:
            del otps[key]

@app.route('/generate-otp', methods=['POST'])
def generate_otp_endpoint():
    cleanup_expired_otps()
    
    otp = generate_otp()
    timestamp = datetime.now()
    
    with otp_lock:
        otps[otp] = (otp, timestamp)
    
    return jsonify({
        'otp': otp,
        'expires_in': 30,
        'message': 'OTP generated successfully'
    })

@app.route('/unlock', methods=['POST'])
def unlock():
    cleanup_expired_otps()
    
    data = request.get_json()
    if not data:
        return jsonify({'status': 'fail', 'message': 'No JSON data provided'}), 400
    
    otp = data.get('otp')
    angle = data.get('angle')
    
    if not otp or angle is None:
        return jsonify({'status': 'fail', 'message': 'OTP and angle are required'}), 400
    
    try:
        angle = float(angle)
        if angle < 0 or angle > 180:
            return jsonify({'status': 'fail', 'message': 'Angle must be between 0 and 180 degrees'}), 400
    except ValueError:
        return jsonify({'status': 'fail', 'message': 'Invalid angle value'}), 400
    
    with otp_lock:
        if otp not in otps:
            return jsonify({'status': 'fail', 'message': 'Invalid or expired OTP'}), 401
        
        _, timestamp = otps[otp]
        if datetime.now() - timestamp > timedelta(seconds=30):
            del otps[otp]
            return jsonify({'status': 'fail', 'message': 'OTP expired'}), 401
        
        del otps[otp]
    
    try:
        duty = angle_to_duty_cycle(angle)
        servo.ChangeDutyCycle(duty)
        time.sleep(0.5)
        servo.ChangeDutyCycle(0)
        
        return jsonify({
            'status': 'success',
            'message': f'Servo rotated to {angle} degrees',
            'angle': angle
        })
    except Exception as e:
        return jsonify({'status': 'fail', 'message': f'Servo control error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Servo controller is running'})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        servo.stop()
        GPIO.cleanup()