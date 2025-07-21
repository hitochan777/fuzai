# fuzai

An automated system that listens for intercom sounds and provides remote door unlocking capabilities via LINE notifications.

## What It Does

When someone rings your intercom:
1. The system detects the intercom sound automatically
2. Sends you a LINE notification with an unlock link
3. You can click the link to remotely unlock the door via Raspberry Pi

## Setup

### Requirements

- Raspberry Pi with audio input (microphone)
- LINE messaging account
- Internet connection

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Set your LINE Channel Access Token:
```bash
export CHANNEL_ACCESS_TOKEN="your-line-channel-access-token"
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


## LINE Notification

When intercom sound is detected, you'll receive a LINE message with:
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
```
