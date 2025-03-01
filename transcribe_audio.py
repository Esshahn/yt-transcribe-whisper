import whisper
import os
import time
import signal
from pathlib import Path
import argparse

class TranscriptionTimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TranscriptionTimeoutError("Transcription timeout reached")

def parse_args():
    parser = argparse.ArgumentParser(description='Audio transcription tool')
    parser.add_argument('--test', action='store_true', help='Test mode: Stop transcription after 1 minute')
    return parser.parse_args()

def transcribe_audio(audio_path, output_dir='transcripts', test_mode=False):
    print(f"Loading Whisper model...")
    model = whisper.load_model("turbo")
    
    print(f"Transcribing {audio_path}...")
    start_time = time.time()
    
    if test_mode:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(60)
    
    try:
        result = model.transcribe(
            audio_path,
            verbose=True,
            fp16=False,
            language='de',
            condition_on_previous_text=True,
            initial_prompt="Dies ist eine Aufzeichnung einer Ausschusssitzung."
        )
        
        if test_mode:
            signal.alarm(0)
        
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
        
    except TranscriptionTimeoutError:
        if test_mode:
            signal.alarm(0)
        print("Test mode: Transcription stopped after 1 minute")
        return None
    except Exception as e:
        if test_mode:
            signal.alarm(0)
        print(f"Error in transcription: {str(e)}")
        raise

def main():
    args = parse_args()
    
    try:
        # Read files to transcribe from the temporary file
        with open('pending_transcriptions.txt', 'r', encoding='utf-8') as f:
            files_to_transcribe = f.read().splitlines()
        
        for audio_path in files_to_transcribe:
            if os.path.exists(audio_path):
                transcribe_audio(audio_path, test_mode=args.test)
            else:
                print(f"File not found: {audio_path}")
        
        # Clean up the temporary file
        os.remove('pending_transcriptions.txt')
        
    except Exception as e:
        print(f"Error in transcribe_audio: {str(e)}")
        raise

if __name__ == "__main__":
    main()