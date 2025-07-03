#!/usr/bin/env python3
"""
Simple transcription with faster-whisper and summarization with Claude CLI
"""
import os
import sys
import subprocess
from faster_whisper import WhisperModel

def transcribe_audio(audio_file, model_size="base"):
    """Transcribe audio using faster-whisper"""
    print(f"Loading {model_size} model...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    print(f"Transcribing {audio_file}...")
    segments, info = model.transcribe(audio_file, beam_size=5)
    
    print(f"Detected language: {info.language} with probability {info.language_probability}")
    
    transcription = ""
    for segment in segments:
        transcription += segment.text + " "
    
    return transcription.strip()

def summarize_with_claude(text):
    """Summarize text using Claude CLI"""
    print("\nSummarizing with Claude CLI...")
    
    # Create a prompt for Claude
    prompt = f"""Please provide a concise summary of the following transcription:

{text}

Summary:"""
    
    try:
        # Run Claude CLI
        result = subprocess.run(
            ["claude", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running Claude CLI: {e}")
        print("Make sure Claude CLI is installed: pip install anthropic && claude login")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python transcribe_and_summarize.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    if not os.path.exists(audio_file):
        print(f"Error: File '{audio_file}' not found")
        sys.exit(1)
    
    # Transcribe
    print("Starting transcription...")
    transcription = transcribe_audio(audio_file)
    
    # Save transcription
    transcript_file = audio_file.rsplit('.', 1)[0] + "_transcript.txt"
    with open(transcript_file, 'w') as f:
        f.write(transcription)
    
    print(f"\n✅ Transcription saved to: {transcript_file}")
    print("\n--- TRANSCRIPTION ---")
    print(transcription[:500] + "..." if len(transcription) > 500 else transcription)
    print("--- END ---\n")
    
    # Summarize with Claude
    summary = summarize_with_claude(transcription)
    
    if summary:
        summary_file = audio_file.rsplit('.', 1)[0] + "_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print("\n--- CLAUDE SUMMARY ---")
        print(summary)
        print("--- END ---\n")
        print(f"✅ Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()