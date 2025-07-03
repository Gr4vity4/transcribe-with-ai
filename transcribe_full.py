#!/usr/bin/env python3
"""
Full transcription with language detection and Claude processing
"""
import os
import sys
import subprocess
from faster_whisper import WhisperModel
from pathlib import Path

def transcribe_file(audio_file, model_size="small"):
    """Full file transcription with progress"""
    print(f"\n🎙️ Transcribing: {Path(audio_file).name}")
    print(f"📊 Model: {model_size}")
    print("⏳ This may take several minutes...\n")
    
    # Load model
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    # Transcribe
    segments, info = model.transcribe(audio_file, beam_size=2)
    
    print(f"🌐 Language detected: {info.language} (confidence: {info.language_probability:.2%})")
    print(f"⏱️ Duration: {info.duration:.1f} seconds\n")
    
    # Collect transcription with progress
    transcription = []
    segment_count = 0
    
    print("📝 Transcribing segments:")
    for segment in segments:
        transcription.append(segment.text.strip())
        segment_count += 1
        if segment_count % 10 == 0:
            print(f"   Processed {segment_count} segments... ({segment.end:.1f}s)")
    
    print(f"✅ Total segments: {segment_count}\n")
    
    return " ".join(transcription), info.language

def process_with_claude(text, language):
    """Process transcription with Claude"""
    print("🤖 Processing with Claude CLI...\n")
    
    # Different prompts based on language
    if language != "en":
        prompt = f"""This is a transcription in {language} language. Please:
1. Identify the main topic
2. Provide a brief English summary (2-3 sentences)
3. List 3-5 key points mentioned

Transcription:
{text[:3000]}"""
    else:
        prompt = f"""Please analyze this transcription and provide:
1. A concise summary (2-3 sentences)
2. Main topics discussed
3. Key takeaways (3-5 bullet points)

Transcription:
{text[:3000]}"""
    
    try:
        result = subprocess.run(
            ["claude", prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except:
        return None

def main():
    # Get audio file
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        # List available files
        downloads = Path("downloads")
        if downloads.exists():
            files = list(downloads.glob("*.m*"))
            if files:
                print("📂 Available files:")
                for i, f in enumerate(files):
                    size = f.stat().st_size / (1024 * 1024)
                    print(f"  {i+1}. {f.name} ({size:.1f} MB)")
                
                choice = input("\nSelect file number (or 0 to exit): ")
                if choice == "0":
                    return
                
                try:
                    audio_file = str(files[int(choice) - 1])
                except:
                    print("❌ Invalid selection")
                    return
            else:
                print("❌ No audio files found in downloads/")
                return
        else:
            print("❌ No downloads folder found")
            return
    
    if not os.path.exists(audio_file):
        print(f"❌ File not found: {audio_file}")
        return
    
    # Choose model
    print("\n🎯 Select model size:")
    print("  1. Tiny (fastest, ~39 MB)")
    print("  2. Base (fast, ~74 MB)")
    print("  3. Small (balanced, ~244 MB)")
    print("  4. Medium (accurate, ~769 MB)")
    
    model_choice = input("Choice (default=2): ") or "2"
    models = {"1": "tiny", "2": "base", "3": "small", "4": "medium"}
    model_size = models.get(model_choice, "base")
    
    # Transcribe
    transcription, language = transcribe_file(audio_file, model_size)
    
    # Save transcription
    base_name = Path(audio_file).stem
    transcript_file = f"{base_name}_full_transcript.txt"
    
    with open(transcript_file, 'w', encoding='utf-8') as f:
        f.write(transcription)
    
    print(f"💾 Transcription saved to: {transcript_file}")
    print(f"📏 Length: {len(transcription)} characters\n")
    
    # Show preview
    print("--- PREVIEW ---")
    preview = transcription[:500] + "..." if len(transcription) > 500 else transcription
    print(preview)
    print("--- END ---\n")
    
    # Process with Claude
    claude_result = process_with_claude(transcription, language)
    
    if claude_result:
        summary_file = f"{base_name}_claude_analysis.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(claude_result)
        
        print("📊 CLAUDE ANALYSIS:")
        print(claude_result)
        print(f"\n💾 Analysis saved to: {summary_file}")
    else:
        print("⚠️ Claude CLI not available. Install with:")
        print("   pip install anthropic")
        print("   claude login")
    
    print("\n✨ Complete!")

if __name__ == "__main__":
    main()