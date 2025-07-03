#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import tempfile
import json
from pathlib import Path
import google.generativeai as genai
import mimetypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found in environment variables. Please check your .env file.")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

def get_mime_type(audio_path):
    """Get MIME type for audio file"""
    mime_type, _ = mimetypes.guess_type(audio_path)
    if mime_type and mime_type.startswith('audio/'):
        return mime_type
    
    # Default fallback based on file extension
    ext = os.path.splitext(audio_path)[1].lower()
    mime_map = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.m4a': 'audio/mp4',
        '.aac': 'audio/aac',
        '.flac': 'audio/flac',
        '.ogg': 'audio/ogg'
    }
    return mime_map.get(ext, 'audio/wav')

def transcribe_with_gemini(audio_path):
    """Transcribe audio using Gemini API"""
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Get MIME type for the audio file
        mime_type = get_mime_type(audio_path)
        
        # Upload audio file
        uploaded_file = genai.upload_file(path=audio_path, mime_type=mime_type)
        
        # Generate transcription
        response = model.generate_content([
            "Please transcribe this audio file accurately. Return only the transcribed text without any additional commentary or formatting.",
            uploaded_file
        ])
        
        # Clean up uploaded file
        genai.delete_file(uploaded_file.name)
        
        return response.text
    
    except Exception as e:
        print(f"Error transcribing with Gemini: {e}")
        return None

def summarize_with_claude(text, task="summarize"):
    """Summarize text using Claude CLI"""
    try:
        # Prepare the prompt based on task
        if task == "summarize":
            prompt = f"Please provide a concise summary of the following transcript:\n\n{text}"
        elif task == "translate":
            prompt = f"Please translate the following transcript to English:\n\n{text}"
        elif task == "analyze":
            prompt = f"Please analyze the key points and themes in the following transcript:\n\n{text}"
        else:
            prompt = f"Please {task} the following transcript:\n\n{text}"
        
        # Use Claude CLI to process the text
        result = subprocess.run([
            'claude', 'say', prompt
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error with Claude CLI: {result.stderr}")
            return None
    
    except Exception as e:
        print(f"Error summarizing with Claude: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Transcribe audio with Gemini API and process with Claude CLI')
    parser.add_argument('audio_file', help='Path to the audio file')
    parser.add_argument('--task', default='summarize', 
                       choices=['summarize', 'translate', 'analyze'],
                       help='Task to perform with Claude (default: summarize)')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    # Check if audio file exists
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file '{args.audio_file}' not found")
        sys.exit(1)
    
    print(f"Transcribing audio file: {args.audio_file}")
    print("Using Gemini API for transcription...")
    
    # Transcribe with Gemini
    transcript = transcribe_with_gemini(args.audio_file)
    
    if not transcript:
        print("Failed to transcribe audio")
        sys.exit(1)
    
    print("Transcription completed!")
    print(f"Processing transcript with Claude CLI ({args.task})...")
    
    # Process with Claude
    processed_text = summarize_with_claude(transcript, args.task)
    
    if not processed_text:
        print("Failed to process transcript with Claude")
        processed_text = transcript  # Fall back to original transcript
    
    # Prepare output
    output_content = f"=== ORIGINAL TRANSCRIPT ===\n{transcript}\n\n=== CLAUDE {args.task.upper()} ===\n{processed_text}"
    
    # Save or print output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"Output saved to: {args.output}")
    else:
        print("\n" + "="*50)
        print(output_content)
        print("="*50)

if __name__ == "__main__":
    main()