#!/usr/bin/env python3
"""
Local transcription using Whisper and Claude CLI
"""
import os
import sys
import subprocess
import argparse
import json
from pathlib import Path

def install_whisper():
    """Install whisper if not already installed"""
    try:
        import whisper
    except ImportError:
        print("Installing OpenAI Whisper...")
        subprocess.run([sys.executable, "-m", "pip", "install", "openai-whisper"], check=True)
        import whisper
    return whisper

def transcribe_audio(audio_file, model="base"):
    """Transcribe audio using local Whisper model"""
    whisper = install_whisper()
    
    print(f"Loading Whisper {model} model...")
    model = whisper.load_model(model)
    
    print(f"Transcribing {audio_file}...")
    result = model.transcribe(audio_file)
    
    return result["text"]

def process_with_claude(text, prompt="Summarize this transcription:"):
    """Process transcription with Claude CLI"""
    # Save text to temporary file
    temp_file = "temp_transcription.txt"
    with open(temp_file, 'w') as f:
        f.write(text)
    
    # Use Claude CLI to process the transcription
    claude_prompt = f"{prompt}\n\n{text}"
    
    try:
        # Run Claude CLI command
        result = subprocess.run(
            ["claude", "-m", "claude-3-haiku-20240307", claude_prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running Claude CLI: {e}")
        print("Make sure Claude CLI is installed and configured")
        return None
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio and process with Claude CLI")
    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model to use (default: base)")
    parser.add_argument("--task", default="summarize", 
                        choices=["summarize", "translate", "format", "analyze"],
                        help="Task for Claude to perform (default: summarize)")
    parser.add_argument("--output", help="Output file (optional)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file '{args.audio_file}' not found")
        sys.exit(1)
    
    # Transcribe audio
    print("Starting transcription...")
    transcription = transcribe_audio(args.audio_file, args.model)
    print("\nTranscription complete!")
    print("-" * 50)
    print(transcription[:500] + "..." if len(transcription) > 500 else transcription)
    print("-" * 50)
    
    # Define Claude prompts based on task
    prompts = {
        "summarize": "Please provide a concise summary of this transcription:",
        "translate": "Please translate this transcription to English (if not already in English):",
        "format": "Please format this transcription with proper punctuation and paragraphs:",
        "analyze": "Please analyze the key points and themes in this transcription:"
    }
    
    # Process with Claude
    print(f"\nProcessing with Claude ({args.task})...")
    claude_result = process_with_claude(transcription, prompts[args.task])
    
    if claude_result:
        print("\nClaude's response:")
        print("=" * 50)
        print(claude_result)
        print("=" * 50)
        
        # Save output if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(f"Original Transcription:\n{transcription}\n\n")
                f.write(f"Claude's {args.task.title()}:\n{claude_result}")
            print(f"\nOutput saved to: {args.output}")
    
    # Save raw transcription
    transcript_file = Path(args.audio_file).stem + "_transcript.txt"
    with open(transcript_file, 'w') as f:
        f.write(transcription)
    print(f"\nRaw transcription saved to: {transcript_file}")

if __name__ == "__main__":
    main()