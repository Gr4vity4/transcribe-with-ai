# YouTube Transcription App

A simple web application that transcribes YouTube videos using OpenAI's Whisper model.

## Features
- Download audio from YouTube URLs
- Transcribe audio using Whisper (multiple model sizes available)
- Download transcription as text file
- Clean Streamlit UI

## Prerequisites
- Python 3.8+
- FFmpeg (required for audio processing)

## Installation

1. Install FFmpeg:
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt update && sudo apt install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the app:
```bash
streamlit run transcribe_app.py
```

Then:
1. Open your browser to http://localhost:8501
2. Enter a YouTube URL
3. Select a Whisper model (larger models are more accurate but slower)
4. Click "Transcribe"
5. Download the transcription when complete

## Model Options
- **tiny**: Fastest, least accurate (~1GB)
- **base**: Good balance (~1GB)
- **small**: Better accuracy (~2GB)
- **medium**: High accuracy (~5GB)
- **large**: Best accuracy (~10GB)

Note: First run will download the selected model.