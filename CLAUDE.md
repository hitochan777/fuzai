# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a sound detection system that monitors microphone input for specific frequencies and sends notifications via LINE messaging when those frequencies are detected. The system is designed to detect intercom sounds and notify users automatically.

## Architecture

### Core Components

- **SoundDetector** (`sound_detect/sound_detector.py`): Main audio processing class that uses FFT analysis to detect target frequencies in real-time microphone input
- **LineMessagingService** (`sound_detect/line_service.py`): Handles LINE messaging API integration for sending broadcast notifications
- **Main Application** (`sound_detect/main.py`): Orchestrates the detection and notification workflow

### Key Technical Details

- Uses PyAudio for real-time microphone input capture
- Implements FFT analysis with Hanning window for frequency detection
- Supports configurable frequency targets, detection thresholds, and sustained detection duration
- Runs detection in a separate thread for non-blocking operation
- Requires LINE Channel Access Token via environment variable `CHANNEL_ACCESS_TOKEN`

## Development Commands

All commands should be run from the `sound_detect/` directory:

```bash
# Install dependencies
uv sync

# Run the main application
uv run main.py

# Install additional dependencies
uv add <package-name>

# Remove dependencies
uv remove <package-name>
```

## Testing

**Development Practice**: When adding new features or fixing bugs, write tests first following TDD (Test-Driven Development) principles.

The project includes unit tests for the core sound detection functionality:

```bash
# Run tests from the sound_detect/ directory
uv run python test_sound_detector.py

# Or run with verbose output
uv run python -m unittest test_sound_detector -v
```

## Environment Setup

The application requires:
- `CHANNEL_ACCESS_TOKEN`: LINE Channel Access Token for messaging API
- Python 3.10+ (specified in pyproject.toml)
- Audio input device (microphone) access
