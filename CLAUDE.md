# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup & Installation
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (required for audio processing)
brew install ffmpeg      # macOS
sudo apt install ffmpeg  # Ubuntu/Debian

# Configure Gemini API
cp config.toml.example config.toml
# Edit config.toml and add your Gemini API key
```

### Running the Application
```bash
# Run the Streamlit app
streamlit run gemini_app.py
```

## Architecture Overview

This is a YouTube and audio transcription application that uses Google's Gemini API for both transcription and post-processing tasks.

### Core Components

1. **Main Application (`gemini_app.py`)**
   - Streamlit web interface with two input methods: file upload and YouTube URL
   - Uses Gemini API directly for audio transcription (no local Whisper models)
   - Supports multiple audio formats: MP3, WAV, M4A, AAC, FLAC, OGG
   - Provides three processing tasks: summarize, translate, and analyze
   - Features a reading mode for better text viewing experience

2. **Configuration (`config.toml`)**
   - Uses TOML format for configuration management
   - Structure: `[gemini]` section with `api_key` and `model` settings
   - Default model: `gemini-1.5-flash` (configurable)

### Key Dependencies
- **Streamlit**: Web interface framework
- **Google Generative AI**: Gemini API client for transcription and processing
- **yt-dlp**: YouTube audio extraction
- **toml**: Configuration file parsing

### Audio Processing Pipeline
1. **Input**: YouTube URL or uploaded audio file
2. **Download** (if YouTube): Extract audio using yt-dlp (m4a format preferred)
3. **Upload to Gemini**: Upload audio file with proper MIME type
4. **Transcription**: Use Gemini model to transcribe audio
5. **Processing**: Apply selected task (summarize/translate/analyze) in target language
6. **Output**: Display results with reading mode option and download capability

### Gemini Integration Details
- Transcription uses configurable model (default: `gemini-1.5-flash`)
- Processing uses fixed model: `gemini-2.0-flash`
- Files are uploaded to Gemini API and deleted after processing
- Supports multiple target languages: English, Thai, Japanese, Korean, Chinese, French, German, Spanish

### Session State Management
The app uses Streamlit session state to store:
- `transcript`: Original transcription text
- `processed_text`: Gemini-processed output
- `task`: Selected processing task
- `target_language`: Selected output language
- `filename`: Source file name
- `reading_mode`: Toggle for reading mode display