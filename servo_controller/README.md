# Servo Controller

Flask server that controls a servo motor on Raspberry Pi with OTP authentication.

## Features

- Generate one-time passcodes (OTP) valid for 30 seconds
- Control servo motor unlock via `/unlock` endpoint (90° default)
- Secure authentication using time-based OTPs
- RESTful API with JSON responses
- Modular architecture with separated concerns

## Architecture

- **app.py**: Flask application with API endpoints
- **servo_controller.py**: ServoController class for hardware control
- **otp_manager.py**: OTPManager class for secure authentication
- **requirements.txt**: Python dependencies

## Hardware Setup

- Servo motor connected to GPIO pin 18
- Raspberry Pi with GPIO access

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Start the server
```bash
python app.py
```

Server runs on `http://0.0.0.0:5000`

### Generate OTP
```bash
curl -X POST http://localhost:5000/generate-otp
```

Response:
```json
{
  "otp": "123456",
  "expires_in": 30,
  "message": "OTP generated successfully"
}
```

### Unlock servo
```bash
curl -X POST http://localhost:5000/unlock \
  -H "Content-Type: application/json" \
  -d '{"otp": "123456"}'
```

Response:
```json
{
  "status": "success",
  "message": "Servo unlocked to 90 degrees",
  "angle": 90
}
```

## API Endpoints

- `POST /generate-otp`: Generate a new OTP
- `POST /unlock`: Unlock servo to predetermined angle (requires valid OTP only)
- `GET /health`: Health check endpoint with active OTP count