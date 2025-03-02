import os
import shutil
import sys

def cleanup_downloads():
    """Remove all files from the downloads directory."""
    downloads_dir = 'downloads'
    
    if not os.path.exists(downloads_dir):
        print(f"Downloads directory '{downloads_dir}' does not exist.")
        return
    
    try:
        # Remove all files in the downloads directory
        for filename in os.listdir(downloads_dir):
            file_path = os.path.join(downloads_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f"Deleted: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Deleted directory: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
                sys.exit(1)
        
        print("Successfully cleaned up downloads directory")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cleanup_downloads()