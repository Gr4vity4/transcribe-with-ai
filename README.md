# YouTube Transcription & Processing App

A powerful web application that transcribes YouTube videos and audio files using Google's Gemini API with additional processing capabilities (summarization, translation, and analysis).

## Features
- Download audio from YouTube URLs
- Upload local audio files (MP3, WAV, M4A, AAC, FLAC, OGG)
- Transcribe audio using Google's Gemini API
- Process transcripts with Gemini (summarize, translate, analyze)
- Support for multiple languages
- Download transcription and processed results
- Reading mode for better text viewing
- Clean Streamlit UI

## Prerequisites
- Python 3.8+
- FFmpeg (required for audio processing)
- Google Gemini API key

## Installation

1. Install FFmpeg:
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt update && sudo apt install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

## Usage

Run the app:
```bash
streamlit run gemini_app.py
```

Then:
1. Open your browser to http://localhost:8501
2. Either:
   - Enter a YouTube URL, or
   - Upload an audio file
3. Select a processing task (summarize, translate, or analyze)
4. Choose target language if needed
5. Click "Transcribe & Process" or "Download & Transcribe"
6. View results in tabs or reading mode
7. Download the transcription and processed results

## Gemini Models
The app uses Google's Gemini API for transcription and processing:
- Default: `gemini-1.5-flash` (fast and efficient)
- Latest: `gemini-2.0-flash` (newest model with improved capabilities)

You can set the model in your `.env` file:
```
GEMINI_MODEL=gemini-2.0-flash
```

## Processing Tasks
- **Summarize**: Get concise summaries of transcripts
- **Translate**: Translate transcripts to different languages
- **Analyze**: Extract key points and themes

## Supported Languages
- English, Thai, Japanese, Korean, Chinese, French, German, Spanish