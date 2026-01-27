FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy crontab file
COPY crontab /etc/cron.d/yt-transcribe

# Set permissions for cron.d file (no need for crontab command - cron reads /etc/cron.d/ directly)
RUN chmod 0644 /etc/cron.d/yt-transcribe

# Create log file
RUN touch /var/log/cron.log

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
