import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not client.api_key:
    raise ValueError("OpenAI API key not found in .env file")

def create_summary(transcript_path, video_url):
    """Create a summary of the transcript using OpenAI."""
    with open(transcript_path, 'r', encoding='utf-8') as file:
        transcript = file.read()

    print("Creating summary...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Du bist ein hilfreicher Assistent, der das folgende Transcript zusammenfasst. Antworte ausschliesslich in deutscher Sprache, benutze kein Markdown. Es handelt sich um die Ausschusssitzung des Ausschusses für Digitalisierung und Datenschutz des Landes Berlin. Wichtige Personen: Frau Martina Klement (CDO des Landes Berlin, Partei CDU), Herr Johannes Kraft (Vorsitzender des Ausschusses, Partei CDU), Herr Carsten Schulz (Schriftführer, Partei Die Linke), Herr Stefan Ziller (Sprecher für Digitalisierung, Partei Die Grünen), Frau Meike Kamp (Datenschutzbeauftragte des Landes Berlin)."},
            {"role": "user", "content": f"Erstelle eine detaillierte Zusammenfassung des Transcriptes. Sollte das CityLAB Berlin wörtlich erwähnt werden, weise darauf hin. Beginne mit einer kurzen Aufzählung der besprochenen Themen. Diese Aufzählung sollte vollständig sein.\n\n{transcript}"}
        ],
        max_tokens=4000,
        temperature=0.7
    )

    summary = response.choices[0].message.content.strip()
    summary_filename = os.path.splitext(os.path.basename(transcript_path))[0] + "_summary.txt"
    summary_path = os.path.join(os.path.dirname(transcript_path), summary_filename)
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"{summary}\n\n{video_url}")

    print(f"Summary saved to {summary_path}")
    return summary_path

def main():
    transcripts_dir = 'transcripts'
    
    # Get the correct video ID from last-video.txt
    try:
        with open('last-video.txt', 'r', encoding='utf-8') as f:
            video_id = f.read().strip()
    except FileNotFoundError:
        print("Warning: Could not find video ID in last-video.txt")
        return

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    for transcript_file in os.listdir(transcripts_dir):
        if transcript_file.endswith('.txt') and not transcript_file.endswith('_summary.txt'):
            transcript_path = os.path.join(transcripts_dir, transcript_file)
            print(f"Creating summary for {transcript_path}")
            create_summary(transcript_path, video_url)

if __name__ == "__main__":
    main()
