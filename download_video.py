import json
import yt_dlp
import os
import subprocess
from pathlib import Path
import sys


def load_config(config_path='config.json'):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_last_video_id(filename='last-video.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_video_id(video_id, filename='last-video.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(video_id)

def search_latest_video(channel_id, search_phrase):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        channel_url = f'https://www.youtube.com/channel/{channel_id}/videos'
        channel_data = ydl.extract_info(channel_url, download=False)
        
        matching_videos = [
            video for video in channel_data['entries']
            if search_phrase.lower() in video['title'].lower()
        ]
        
        return matching_videos[0] if matching_videos else None

def download_audio(video_url, output_path='downloads'):
    os.makedirs(output_path, exist_ok=True)
    
    ydl_opts = {
        'format': 'm4a/bestaudio[ext=m4a]',
        'paths': {'home': output_path},
        'outtmpl': {
            'default': '%(title)s.%(ext)s'
        },
        'cookiesfrombrowser': ('chrome',),
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print("Starting download...")
        info = ydl.extract_info(video_url, download=True)
        filename = os.path.join(output_path, f"{info['title']}.m4a")
        print("Download completed")
        
        trimmed_filename = os.path.join(output_path, f"trimmed_{os.path.basename(filename)}")
        
        print("Removing silence with FFmpeg...")
        subprocess.run([
            'ffmpeg', '-y', '-i', filename,
            '-af', 'silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.3,areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.3,areverse',
            '-c:a', 'aac',
            trimmed_filename
        ], check=True)
        
        os.replace(trimmed_filename, filename)
        return filename

def main():

    try:
        config = load_config()
        downloaded_files = []
        new_videos_found = False
        
        for channel in config['channels']:
            channel_id = channel['channel_id']
            search_phrase = channel['search_phrase']
            
            print(f"Searching for videos with '{search_phrase}' in channel {channel_id}")
            
            latest_video = search_latest_video(channel_id, search_phrase)
            
            if latest_video:
                video_id = latest_video['id']
                last_processed_id = load_last_video_id()
                
                if last_processed_id == video_id:
                    print(f"Video '{latest_video['title']}' has already been processed. Skipping...")
                    continue
                    
                print(f"Found new video: {latest_video['title']}")
                
                audio_path = download_audio(latest_video['url'])
                save_last_video_id(video_id)
                downloaded_files.append(audio_path)
                new_videos_found = True
                print(f"Successfully downloaded video: {latest_video['title']}")
            else:
                print(f"No new videos found matching '{search_phrase}'")
        
        # Exit with code 1 if no new videos were found to stop the pipeline
        if not new_videos_found:
            print("No new videos to process. Stopping pipeline...")
            sys.exit(1)
                 
    except Exception as e:
        print(f"Error in download_video: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()





