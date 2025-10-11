# Environment Variables

This document describes all environment variables required and optional for running the intercom detection system.

## Core Configuration

### Required for All Notifiers

| Variable | Description | Example |
|----------|-------------|---------|
| `BASE_URL` | Public base URL for generating unlock links | `https://example.com` |
| `NOTIFIER_TYPE` | Type of notifier to use | `line`, `slack`, or `email` (default: `line`) |
| `REFERENCE_AUDIO_PATH` | Path to reference intercom audio file | `reference_intercom.wav` (default) |

## Camera Configuration

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `CAMERA_INDEX` | Camera device index (0 for primary camera) | `0` |

## Notifier-Specific Configuration

### LINE Notifier

Set `NOTIFIER_TYPE=line` and configure the following:

| Variable | Required | Description |
|----------|----------|-------------|
| `CHANNEL_ACCESS_TOKEN` | ✅ Yes | LINE Channel Access Token |

**Example:**
```bash
export NOTIFIER_TYPE=line
export CHANNEL_ACCESS_TOKEN=your-line-channel-access-token
```

**Features:**
- ✅ Text messages
- ❌ Image upload (not supported without external hosting)

---

### Slack Notifier

Set `NOTIFIER_TYPE=slack` and configure the following:

| Variable | Required | Description |
|----------|----------|-------------|
| `SLACK_BOT_TOKEN` | ✅ Yes | Slack Bot Token (starts with `xoxb-`) |
| `SLACK_CHANNEL` | ✅ Yes | Slack channel ID (e.g., `C1234567890`) |

**Example:**
```bash
export NOTIFIER_TYPE=slack
export SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
export SLACK_CHANNEL=C1234567890
```

**Features:**
- ✅ Text messages
- ✅ Direct image upload (captured from camera)

**How to get Slack credentials:**
1. Create a Slack App at https://api.slack.com/apps
2. Add Bot Token Scopes: `chat:write`, `files:write`
3. Install the app to your workspace
4. Copy the Bot User OAuth Token (starts with `xoxb-`)
5. Get the channel ID from Slack (right-click channel → View channel details)

---

### Email Notifier

Set `NOTIFIER_TYPE=email` and configure the following:

| Variable | Required | Description |
|----------|----------|-------------|
| `RESEND_API_KEY` | ✅ Yes | Resend API key |
| `FROM_EMAIL` | ✅ Yes | Sender email address |
| `TO_EMAILS` | ✅ Yes | Comma-separated list of recipient emails |

**Example:**
```bash
export NOTIFIER_TYPE=email
export RESEND_API_KEY=re_your_resend_api_key
export FROM_EMAIL=alerts@yourdomain.com
export TO_EMAILS=user1@example.com,user2@example.com
```

**Features:**
- ✅ Text messages
- ❌ Image attachments (not currently implemented)

**How to get Resend credentials:**
1. Sign up at https://resend.com
2. Create an API key in the dashboard
3. Verify your sender domain or use the test domain

---

## Complete Configuration Examples

### Example 1: Slack with Image Capture
```bash
export BASE_URL=https://myserver.example.com
export NOTIFIER_TYPE=slack
export SLACK_BOT_TOKEN=xoxb-aaaaaaaa
export SLACK_CHANNEL=C01234ABCDE
export CAMERA_INDEX=0
export REFERENCE_AUDIO_PATH=reference_intercom.wav
```

### Example 2: LINE (Text Only)
```bash
export BASE_URL=https://myserver.example.com
export NOTIFIER_TYPE=line
export CHANNEL_ACCESS_TOKEN=your-line-channel-access-token
export REFERENCE_AUDIO_PATH=reference_intercom.wav
```

### Example 3: Email Notifications
```bash
export BASE_URL=https://myserver.example.com
export NOTIFIER_TYPE=email
export RESEND_API_KEY=re_AbCdEfGh123456789
export FROM_EMAIL=intercom-alerts@mydomain.com
export TO_EMAILS=me@example.com,security@example.com
export REFERENCE_AUDIO_PATH=reference_intercom.wav
```

## Feature Comparison

| Feature | LINE | Slack | Email |
|---------|------|-------|-------|
| Text Messages | ✅ | ✅ | ✅ |
| Image Upload | ❌ | ✅ | ❌ |
| Setup Complexity | Low | Medium | Low |
| Real-time | ✅ | ✅ | ⚠️ (depends on email delivery) |
| Best For | Mobile users in Japan | Team collaboration | Traditional notifications |
