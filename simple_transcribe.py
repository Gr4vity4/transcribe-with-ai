#!/usr/bin/env python3
"""
Simple transcription demo - processes first 30 seconds only for quick testing
"""
import os
import subprocess
from faster_whisper import WhisperModel

# Get the audio file
audio_file = "downloads/audio_1751525714.mp3"

if not os.path.exists(audio_file):
    print("❌ Audio file not found!")
    exit(1)

print("🎙️ Transcribing first 30 seconds...")
print("(Using tiny model for speed)")
print("⏳ Please wait, this may take a minute...")

# Load tiny model for quick processing
model = WhisperModel("tiny", device="cpu", compute_type="int8")

# Transcribe audio
segments, info = model.transcribe(
    audio_file,
    beam_size=1
)

print(f"Language: {info.language}")

# Collect transcription (limit to first 30 seconds worth)
transcription = ""
segment_count = 0
for segment in segments:
    if segment.start > 30:  # Stop after 30 seconds
        break
    transcription += segment.text + " "
    segment_count += 1

print("\n--- TRANSCRIPTION (first 30 seconds) ---")
print(transcription)
print("--- END ---\n")

# Save to file
with open("sample_transcript.txt", "w") as f:
    f.write(transcription)

print("✅ Saved to: sample_transcript.txt")

# Try Claude summarization
print("\n🤖 Sending to Claude CLI...")

prompt = f"Summarize this transcription in 2-3 bullet points:\n\n{transcription}"

try:
    result = subprocess.run(
        ["claude", prompt],
        capture_output=True,
        text=True,
        timeout=20
    )
    
    if result.returncode == 0:
        print("\n📊 CLAUDE SUMMARY:")
        print(result.stdout)
    else:
        print("❌ Claude CLI not working. Install with:")
        print("   pip install anthropic")
        print("   claude login")

except:
    print("⚠️ Claude CLI not found")

print("\n✨ Done!")