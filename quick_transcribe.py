#!/usr/bin/env python3
"""
Quick transcription and Claude summarization
"""
import os
import sys
import subprocess
from faster_whisper import WhisperModel
from pathlib import Path

def transcribe_audio(audio_file, model_size="tiny"):
    """Transcribe using tiny model for speed"""
    print(f"🎙️ Transcribing with {model_size} model (this may take a moment)...")
    
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_file, beam_size=1)
    
    print(f"📝 Language: {info.language}")
    
    transcription = []
    for i, segment in enumerate(segments):
        transcription.append(segment.text)
        if i % 10 == 0:
            print(f"   Processing... {i} segments")
    
    return " ".join(transcription)

def main():
    # Check for audio file argument
    if len(sys.argv) < 2:
        # List available files
        downloads_dir = Path("downloads")
        if downloads_dir.exists():
            files = list(downloads_dir.glob("*.m*"))  # m4a, mp3
            if files:
                print("Available files:")
                for i, f in enumerate(files):
                    print(f"{i+1}. {f.name}")
                print("\nUsage: python quick_transcribe.py downloads/filename.mp3")
        else:
            print("Usage: python quick_transcribe.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    if not os.path.exists(audio_file):
        print(f"❌ File not found: {audio_file}")
        sys.exit(1)
    
    # Step 1: Transcribe
    print(f"\n🚀 Processing: {audio_file}")
    transcription = transcribe_audio(audio_file, "tiny")  # Use tiny for speed
    
    # Save transcription
    base_name = Path(audio_file).stem
    transcript_file = f"{base_name}_transcript.txt"
    
    with open(transcript_file, 'w') as f:
        f.write(transcription)
    
    print(f"\n✅ Transcription saved to: {transcript_file}")
    print(f"📄 Length: {len(transcription)} characters")
    
    # Show preview
    print("\n--- PREVIEW ---")
    print(transcription[:300] + "..." if len(transcription) > 300 else transcription)
    print("--- END ---\n")
    
    # Step 2: Summarize with Claude
    print("🤖 Summarizing with Claude CLI...")
    
    prompt = f"Summarize this transcription in 3-5 key points:\n\n{transcription[:4000]}"  # Limit for CLI
    
    try:
        result = subprocess.run(
            ["claude", prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            summary = result.stdout
            summary_file = f"{base_name}_summary.txt"
            
            with open(summary_file, 'w') as f:
                f.write(summary)
            
            print("\n📊 CLAUDE SUMMARY:")
            print(summary)
            print(f"\n✅ Summary saved to: {summary_file}")
        else:
            print("❌ Claude CLI error. Make sure it's installed:")
            print("   pip install anthropic")
            print("   claude login")
            if result.stderr:
                print(f"Error: {result.stderr}")
    
    except FileNotFoundError:
        print("\n⚠️ Claude CLI not found. Install with:")
        print("   pip install anthropic")
        print("   claude login")
    except subprocess.TimeoutExpired:
        print("\n⚠️ Claude took too long to respond")

if __name__ == "__main__":
    main()