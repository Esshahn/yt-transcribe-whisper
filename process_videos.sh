#!/bin/bash

echo "Starting video download process..."
python3 download_video.py
if [ $? -ne 0 ]; then
    echo "Error during download process"
    exit 1
fi

echo "Starting transcription process..."
python3 transcribe_audio.py
if [ $? -ne 0 ]; then
    echo "Error during transcription process"
    exit 1
fi

echo "All processes completed successfully"

