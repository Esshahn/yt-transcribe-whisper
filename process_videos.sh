#!/bin/bash

# Set working directory
cd "$(dirname "$0")"

# Activate virtual environment (skip if running in Docker)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Update yt-dlp to latest version
echo "$(date): Updating yt-dlp to latest version..."
pip install --upgrade yt-dlp --quiet

# Create logs directory if it doesn't exist
mkdir -p logs

echo "Starting video download process..."
python3 download_video.py
if [ $? -ne 0 ]; then
    exit 1
fi

echo "Starting transcription process..."
python3 transcribe_audio.py
if [ $? -ne 0 ]; then
    echo "Error during transcription process"
    exit 1
fi

echo "Starting summary..."
python3 summarize_transcript.py
if [ $? -ne 0 ]; then
    echo "Error during summary"
    exit 1
fi

echo "Posting to Slack channel..."
python3 slack_poster.py
if [ $? -ne 0 ]; then
    echo "Error during posting to slack"
    exit 1
fi

echo "Cleaning up downloads and transcripts directories..."
python3 cleanup.py
if [ $? -ne 0 ]; then
    echo "Error during cleanup"
    exit 1
fi

echo "All processes completed successfully"

