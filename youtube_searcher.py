import json
import yt_dlp
import whisper
import os
import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import signal
from functools import partial
import time

class TranscriptionTimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TranscriptionTimeoutError("Transcription timeout reached")

def parse_args():
    parser = argparse.ArgumentParser(description='YouTube video transcription tool')
    parser.add_argument('--config', default='config.json', help='Path to config file')
    parser.add_argument('--test', action='store_true', help='Test mode: Stop transcription after 1 minute')
    return parser.parse_args()

def load_config(config_path='config.json'):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_last_video_id(filename='last-video.txt'):
    """Load the ID of the last processed video."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_video_id(video_id, filename='last-video.txt'):
    """Save the ID of the last processed video."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(video_id)

def search_latest_video(channel_id, search_phrase):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Search in channel
        channel_url = f'https://www.youtube.com/channel/{channel_id}/videos'
        channel_data = ydl.extract_info(channel_url, download=False)
        
        # Filter videos by search phrase
        matching_videos = [
            video for video in channel_data['entries']
            if search_phrase.lower() in video['title'].lower()
        ]
        
        # Get the latest video
        if matching_videos:
            return matching_videos[0]  # Videos are already sorted by date
        return None

def download_audio(video_url, output_path='downloads'):
    """Download audio from video URL and return the path to the downloaded file."""
    os.makedirs(output_path, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio',
        'paths': {'home': output_path},
        'outtmpl': {
            'default': '%(title)s.mp3'
        },
        'cookiesfrombrowser': ('chrome',),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print("Starting download...")
            info = ydl.extract_info(video_url, download=True)
            print("Download completed")
            
            # Get the final filename
            filename = os.path.join(output_path, f"{info['title']}.mp3")
            print(f"Processing file: {filename}")
            
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Expected output file not found: {filename}")
            
            # Create a temporary filename for the trimmed version
            trimmed_filename = os.path.join(output_path, f"trimmed_{os.path.basename(filename)}")
            
            print("Removing silence with FFmpeg...")
            # Use ffmpeg to remove silence from start and end
            ffmpeg_cmd = [
                'ffmpeg', '-y', '-i', filename,
                '-af', 'silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.3,areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.3,areverse',
                '-c:a', 'libmp3lame', '-q:a', '2',
                trimmed_filename
            ]
            
            try:
                result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
                print("FFmpeg processing completed")
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg error: {e.stderr}")
                return filename  # Return original file if FFmpeg fails
            
            # Replace original file with trimmed version
            try:
                os.replace(trimmed_filename, filename)
                print("Trimmed file saved successfully")
            except Exception as e:
                print(f"Error replacing file: {e}")
                if os.path.exists(trimmed_filename):
                    os.remove(trimmed_filename)
                return filename
            
            return filename
            
        except Exception as e:
            print(f"Error in download_audio: {str(e)}")
            raise

def transcribe_audio(audio_path, output_dir='transcripts', test_mode=False):
    """Transcribe the audio file using Whisper and save to a text file."""
    print(f"Loading Whisper model...")
    model = whisper.load_model("turbo")
    
    print(f"Transcribing {audio_path}...")
    start_time = time.time()
    
    # Set up timeout if in test mode
    if test_mode:
        # Set up signal handler for timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(60)  # 60 seconds = 1 minute
    
    try:
        result = model.transcribe(
            audio_path,
            verbose=True,          # Show progress
            fp16=False,           # Use CPU if GPU not available
            language='de',        # Specify German language
            condition_on_previous_text=True,  # Improve consistency
            initial_prompt="Dies ist eine Aufzeichnung einer Ausschusssitzung."  # Context hint
        )
        
        # Disable alarm if in test mode
        if test_mode:
            signal.alarm(0)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filename
        audio_filename = Path(audio_path).stem
        transcript_path = os.path.join(output_dir, f"{audio_filename}.txt")
        
        # Save transcription
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(result["text"])
        
        # Calculate and display elapsed time
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print(f"Transcription completed in {minutes} minutes and {seconds} seconds")
        print(f"Transcription saved to {transcript_path}")
        return transcript_path
        
    except TranscriptionTimeoutError:
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print(f"Test transcription stopped after {minutes} minutes and {seconds} seconds")
        print("Test mode: Transcription stopped after 1 minute")
        if test_mode:
            signal.alarm(0)  # Disable alarm
            # Save partial transcription if available
            try:
                if 'result' in locals() and result.get("text"):
                    partial_path = os.path.join(output_dir, f"{Path(audio_path).stem}_partial.txt")
                    with open(partial_path, 'w', encoding='utf-8') as f:
                        f.write(result["text"])
                    print(f"Partial transcription saved to {partial_path}")
            except Exception as e:
                print(f"Could not save partial transcription: {e}")
        return None
    except Exception as e:
        if test_mode:
            signal.alarm(0)  # Disable alarm
        print(f"Error in transcription: {str(e)}")
        raise

def main():
    args = parse_args()
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        for channel in config['channels']:
            channel_id = channel['channel_id']
            search_phrase = channel['search_phrase']
            
            print(f"Searching for videos with '{search_phrase}' in channel {channel_id}")
            
            # Search for latest matching video
            latest_video = search_latest_video(channel_id, search_phrase)
            
            if latest_video:
                video_id = latest_video['id']
                
                # Check if we've already processed this video
                last_processed_id = load_last_video_id()
                if last_processed_id == video_id:
                    print(f"Video '{latest_video['title']}' has already been processed. Skipping...")
                    continue
                    
                print(f"Found new video: {latest_video['title']}")
                
                try:
                    # Download audio
                    audio_path = download_audio(latest_video['url'])
                    
                    # Transcribe audio with test mode if specified
                    transcript_path = transcribe_audio(audio_path, test_mode=args.test)
                    
                    # Save the video ID as processed regardless of test mode
                    save_last_video_id(video_id)
                    
                    print(f"Successfully processed video: {latest_video['title']}")
                    
                except Exception as e:
                    print(f"Error processing video {latest_video['title']}: {str(e)}")
                    raise
            else:
                print(f"No new videos found matching '{search_phrase}'")
                
    except Exception as e:
        print(f"Fatal error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
