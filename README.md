# fuzai

An automated system that listens for intercom sounds and provides remote door unlocking capabilities via email or LINE notifications.

## What It Does

When someone rings your intercom:
1. The system detects the intercom sound automatically
2. Sends you an email notification with an unlock link
3. You can click the link to remotely unlock the door via Raspberry Pi

## Setup

### Requirements

- Raspberry Pi with audio input (microphone)
- Resend account for email notifications (or LINE messaging account)
- Internet connection

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Configure environment variables:

For email notifications (default):
```bash
export RESEND_API_KEY="your-resend-api-key"
export FROM_EMAIL="sender@yourdomain.com"
export TO_EMAILS="recipient1@example.com,recipient2@example.com"
export BASE_URL="http://your-raspberry-pi-ip:5000"
```

For LINE notifications (alternative):
```bash
export CHANNEL_ACCESS_TOKEN="your-line-channel-access-token"
export BASE_URL="http://your-raspberry-pi-ip:5000"
```

## Usage

### Start the System

```bash
uv run app.py
```

The system will:
- Begin monitoring for intercom sounds
- Run in the background continuously
- Send email notifications when intercom is detected

## Notification

When intercom sound is detected, you'll receive an email/LINE message with:
- Alert that someone is at the door
- One-click unlock link

## Door Unlock

The unlock mechanism works through:
- Secure web endpoint on your Raspberry Pi
- One-time use unlock links for security
- Integration with door lock hardware

## Security Notes

- Unlock links expire after use for security
- Ensure your Raspberry Pi is on a secure network

## Testing

Test the complete workflow:

```bash
# Test sound detection
uv run python test_sound_detector.py

# Test email service
uv run python test_email_service.py
```

## Changing notification method

To switch from email to LINE notifications:
1. Comment out email service imports in `app.py`
2. Uncomment LINE service imports in `app.py`
3. Update the service initialization in the `initialize_services()` function
4. Set the appropriate environment variables
