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

def upload_file_to_slack(client, channel_id, file_path, title):
    """Upload a file to Slack channel."""
    try:
        response = client.files_upload_v2(
            channel=channel_id,
            file=file_path,
            title=title,
            filename=os.path.basename(file_path)
        )
        print(f"Successfully uploaded {file_path} to Slack channel {channel_id}")
        return True
    except SlackApiError as e:
        print(f"Error uploading file to Slack: {e.response['error']}")
        raise

def post_to_slack(client, channel_id, summary_path, transcript_path):
    """Post summary to Slack channel and upload full transcript."""
    try:
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary = f.read()

        response = client.chat_postMessage(
            channel=channel_id,
            text=summary
        )
        print(f"Successfully posted summary to Slack channel {channel_id}")

        # Upload full transcript as file
        if transcript_path and os.path.exists(transcript_path):
            try:
                upload_file_to_slack(
                    client,
                    channel_id,
                    transcript_path,
                    f"Vollständiges Transkript: {os.path.basename(transcript_path)}"
                )
            except SlackApiError as e:
                if e.response['error'] == 'missing_scope':
                    print(f"Warning: Cannot upload transcript file - missing 'files:write' scope")
                    print(f"To enable file uploads, add 'files:write' scope to your Slack Bot at:")
                    print(f"https://api.slack.com/apps -> Your App -> OAuth & Permissions -> Scopes")
                else:
                    raise

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

                # Find corresponding transcript file (without _summary suffix)
                base_name = file.replace('_summary.txt', '.txt')
                transcript_path = os.path.join(transcripts_dir, base_name)

                print(f"Posting summary from {summary_path} to Slack")
                post_to_slack(slack_client, slack_channel_id, summary_path, transcript_path)

    except Exception as e:
        print(f"Error in slack_poster: {str(e)}")
        raise

if __name__ == "__main__":
    main()
