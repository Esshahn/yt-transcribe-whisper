# YouTube Meeting Transcriber

This project automatically monitors a YouTube channel for new videos, downloads them, transcribes the audio, creates summaries, and posts the results to a Slack channel. It's specifically configured for monitoring committee meetings ("Ausschusssitzung") and creating German language summaries.

## Features

- 🎥 Automatic YouTube video monitoring and downloading
- 🔊 Audio extraction and silence removal
- 📝 German speech transcription using Whisper
- ✍️ AI-powered summarization using GPT-4
- 📢 Automatic posting to Slack
- 🧹 Automatic cleanup of downloaded files

## Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- Chrome browser (for cookies)
- Valid API keys and tokens

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd [your-repo-name]
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_CHANNEL_ID=your_slack_channel_id
```

5. Configure `config.json` with your YouTube channel details:
```json
{
    "channels": [
        {
            "channel_id": "your_channel_id",
            "search_phrase": "your_search_phrase"
        }
    ]
}
```

## Usage

### Manual Execution

Run the entire pipeline with:
```bash
./process_videos.sh
```

This script will:
1. Download new videos matching the search criteria
2. Extract and process the audio
3. Transcribe the audio to text
4. Generate a summary
5. Post the summary to Slack
6. Clean up downloaded files

### Automated Execution (Cron Job)

To run the script automatically every day at 09:00:

1. Make the script executable:
```bash
chmod +x /path/to/process_videos.sh
```

2. Open your crontab:
```bash
crontab -e
```

3. Add this line:
```
0 9 * * * cd /absolute/path/to/project && ./process_videos.sh >> logs/cron.log 2>&1
```

4. Verify your crontab entry:
```bash
crontab -l
```

5. Monitor the logs:
```bash
tail -f logs/cron.log
```

Note: Replace `/absolute/path/to/project` with the actual path to your project directory.

## Project Structure

- `download_video.py`: YouTube video monitoring and downloading
- `transcribe_audio.py`: Audio transcription using Whisper
- `summarize_transcript.py`: Text summarization using GPT-4
- `slack_poster.py`: Posts summaries to Slack
- `cleanup.py`: Removes downloaded files
- `process_videos.sh`: Main pipeline script

## Directory Structure

```
.
├── downloads/           # Temporary storage for downloaded files
├── transcripts/        # Storage for transcripts and summaries
├── logs/              # Cron job and application logs
├── config.json         # Channel configuration
├── requirements.txt    # Python dependencies
└── .env               # Environment variables (not in repo)
```

## Error Handling

- The pipeline stops if no new videos are found
- Each step includes error checking and logging
- Failed steps will stop the pipeline and exit with code 1

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
