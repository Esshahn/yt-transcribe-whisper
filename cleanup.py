import os
import shutil
import sys

def cleanup():
    """Remove downloads and transcripts directories."""
    try:
        for directory in ['downloads', 'transcripts']:
            if os.path.exists(directory):
                shutil.rmtree(directory)
                print(f"Deleted directory: {directory}")
        
        print("Successfully cleaned up directories")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cleanup()
