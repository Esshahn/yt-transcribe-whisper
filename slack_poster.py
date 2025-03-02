import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_slack_client():
    """Initialize Slack client with bot token from .env file."""
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        raise ValueError("Slack Bot Token not found in .env file")
    return WebClient(token=slack_token)

def post_to_slack(client, channel_id, summary_path):
    """Post summary to Slack channel."""
    try:
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary = f.read()

        response = client.chat_postMessage(
            channel=channel_id,
            text=summary
        )
        print(f"Successfully posted to Slack channel {channel_id}")
        return True
    except SlackApiError as e:
        print(f"Error posting to Slack: {e.response['error']}")
        raise

def main():
    try:
        slack_client = initialize_slack_client()
        slack_channel_id = os.getenv("SLACK_CHANNEL_ID")
        if not slack_channel_id:
            raise ValueError("Slack Channel ID not found in .env file")
        
        # Look for summary files in transcripts directory
        transcripts_dir = 'transcripts'
        for file in os.listdir(transcripts_dir):
            if file.endswith('_summary.txt'):
                summary_path = os.path.join(transcripts_dir, file)
                print(f"Posting summary from {summary_path} to Slack")
                post_to_slack(slack_client, slack_channel_id, summary_path)

    except Exception as e:
        print(f"Error in slack_poster: {str(e)}")
        raise

if __name__ == "__main__":
    main()
