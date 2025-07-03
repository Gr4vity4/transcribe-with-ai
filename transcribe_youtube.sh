#!/bin/bash

# Simple script to transcribe YouTube downloads with Claude

echo "🎙️ YouTube Transcription with Claude CLI"
echo "======================================="

# Check if downloads folder exists
if [ ! -d "downloads" ]; then
    echo "❌ No downloads folder found. Please download a video first."
    exit 1
fi

# List available audio files
echo -e "\n📁 Available audio files:"
ls -1 downloads/*.{m4a,mp3,webm} 2>/dev/null | nl -w2 -s'. '

# Get user selection
echo -e "\nEnter the number of the file to transcribe (or 0 to exit):"
read -r selection

if [ "$selection" = "0" ]; then
    echo "Exiting..."
    exit 0
fi

# Get the selected file
audio_file=$(ls -1 downloads/*.{m4a,mp3,webm} 2>/dev/null | sed -n "${selection}p")

if [ -z "$audio_file" ]; then
    echo "❌ Invalid selection"
    exit 1
fi

echo -e "\n📄 Selected: $audio_file"

# Choose Whisper model
echo -e "\n🤖 Select Whisper model:"
echo "1. tiny (fastest, ~1GB)"
echo "2. base (balanced, ~1GB)"
echo "3. small (better, ~2GB)"
echo "4. medium (good, ~5GB)"
echo "5. large (best, ~10GB)"
read -r model_choice

case $model_choice in
    1) model="tiny";;
    2) model="base";;
    3) model="small";;
    4) model="medium";;
    5) model="large";;
    *) model="base";;
esac

# Choose Claude task
echo -e "\n📝 Select Claude task:"
echo "1. Summarize"
echo "2. Translate"
echo "3. Format"
echo "4. Analyze"
read -r task_choice

case $task_choice in
    1) task="summarize";;
    2) task="translate";;
    3) task="format";;
    4) task="analyze";;
    *) task="summarize";;
esac

echo -e "\n🚀 Starting transcription with:"
echo "   Model: $model"
echo "   Task: $task"
echo "   File: $audio_file"

# Run transcription
python local_transcribe.py "$audio_file" --model "$model" --task "$task"

echo -e "\n✅ Done!"