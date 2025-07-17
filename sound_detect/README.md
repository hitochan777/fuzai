# Remote Intercom Control Tool

⚠️ **This project is currently under development** ⚠️

A remote intercom monitoring and control system that detects intercom sounds through audio frequency analysis and sends instant notifications via LINE messaging. This tool enables remote monitoring of door intercom systems, allowing users to be notified of visitors even when away from the intercom unit.

## Features

- **Remote Intercom Monitoring**: Continuously monitors audio input for intercom-specific frequencies
- **Real-time Detection**: Uses FFT analysis with configurable frequency targets and detection thresholds
- **Instant Notifications**: Sends immediate LINE messages when intercom sounds are detected
- **Configurable Settings**: Adjustable frequency targets, detection sensitivity, and sustained detection duration
- **Non-blocking Operation**: Runs detection in separate thread for responsive performance

## Quick Start

```bash
# Install dependencies
uv sync

# Set environment variable for LINE messaging
export CHANNEL_ACCESS_TOKEN=your_line_token

# Run the remote intercom monitoring tool
uv run main.py
```

## Testing

```bash
uv run python test_sound_detector.py
```