# Servo Controller

Flask server that controls a servo motor on Raspberry Pi with OTP authentication.

## Features

- Generate one-time passcodes (OTP) valid for 30 seconds
- Control servo motor rotation via `/unlock` endpoint
- Secure authentication using time-based OTPs
- RESTful API with JSON responses

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

### Unlock (rotate servo)
```bash
curl -X POST http://localhost:5000/unlock \
  -H "Content-Type: application/json" \
  -d '{"otp": "123456", "angle": 90}'
```

Response:
```json
{
  "status": "success",
  "message": "Servo rotated to 90 degrees",
  "angle": 90
}
```

## API Endpoints

- `POST /generate-otp`: Generate a new OTP
- `POST /unlock`: Rotate servo (requires valid OTP and angle 0-180)
- `GET /health`: Health check endpoint