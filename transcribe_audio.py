import whisper
import os
from pathlib import Path
import time

def transcribe_audio(audio_path: str, output_dir: str = 'transcripts') -> str:
    """
    Transcribe an audio file using Whisper model.
    
    Args:
        audio_path: Path to the audio file
        output_dir: Directory to save the transcript
        
    Returns:
        Path to the generated transcript file
    """
    print(f"Loading Whisper model...")
    model = whisper.load_model("turbo")
    
    print(f"Transcribing {audio_path}...")
    start_time = time.time()
    
    try:
        result = model.transcribe(
            audio_path,
            verbose=True,
            fp16=False,
            language='de',
            condition_on_previous_text=True,
            initial_prompt="Dies ist eine Aufzeichnung einer Ausschusssitzung.",
            beam_size=1  # Default is 5, reducing saves time
        )
        
        os.makedirs(output_dir, exist_ok=True)
        audio_filename = Path(audio_path).stem
        transcript_path = os.path.join(output_dir, f"{audio_filename}.txt")
        
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(result["text"])
        
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print(f"Transcription completed in {minutes} minutes and {seconds} seconds")
        print(f"Transcription saved to {transcript_path}")
        return transcript_path
        
    except Exception as e:
        print(f"Error in transcription: {str(e)}")
        raise

def main():
    try:
        downloads_dir = 'downloads'
        for file in os.listdir(downloads_dir):
            if file.endswith(('.mp3', '.m4a')):
                audio_path = os.path.join(downloads_dir, file)
                transcribe_audio(audio_path)
        
    except Exception as e:
        print(f"Error in transcribe_audio: {str(e)}")
        raise

if __name__ == "__main__":
    main()
