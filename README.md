# fuzai

An automated system that listens for intercom sounds and provides remote door unlocking capabilities via LINE or email notifications.

## What It Does

When someone rings your intercom:
1. The system detects the intercom sound automatically
2. Sends you a LINE notification with an unlock link
3. You can click the link to remotely unlock the door via Raspberry Pi

## Setup

### Requirements

- Raspberry Pi with audio input (microphone)
- LINE messaging account (or Resend account for email notifications)
- Internet connection

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Configure environment variables:

For LINE notifications (default):
```bash
export CHANNEL_ACCESS_TOKEN="your-line-channel-access-token"
export BASE_URL="http://your-raspberry-pi-ip:5000"
```

For email notifications (alternative):
```bash
export RESEND_API_KEY="your-resend-api-key"
export FROM_EMAIL="sender@yourdomain.com"
export TO_EMAILS="recipient1@example.com,recipient2@example.com"
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
- Send LINE notifications when intercom is detected

## Notification

When intercom sound is detected, you'll receive a LINE/email message with:
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

## Time-based Pause Feature

The system includes a time-based pause feature that automatically disables sound detection during specified hours (e.g., nighttime). This prevents unwanted notifications during sleep hours.

### Default Configuration

By default, the pause feature is enabled with these settings:
- **Pause period**: 10:00 PM to 8:00 AM
- **Status**: Enabled

During the pause window, the system will not trigger any notifications

### Customizing Pause Settings

You can customize the pause behavior when initializing the SoundDetector in `app.py`:

## Changing notification method

To switch from LINE to email notifications:
1. Comment out LINE service imports in `app.py`
2. Uncomment email service imports in `app.py`
3. Update the service initialization in the `initialize_services()` function
4. Set the appropriate environment variables
