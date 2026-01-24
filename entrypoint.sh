#!/bin/bash

# Export environment variables for cron
printenv | grep -E "^(OPENAI_API_KEY|SLACK_BOT_TOKEN|SLACK_CHANNEL_ID|TZ)=" >> /etc/environment

# Create necessary directories
mkdir -p /app/logs /app/downloads /app/transcripts

echo "$(date): Starting cron daemon..."
echo "$(date): Cron job scheduled for 8:00 AM daily"

# Start cron in foreground and tail the log
cron && tail -f /var/log/cron.log
