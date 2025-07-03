# GEMINI.md

This file provides guidance when working with code in this repository.

## Development Commands

### Setup & Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install FFmpeg (required for audio processing)
brew install ffmpeg      # macOS
sudo apt install ffmpeg  # Ubuntu/Debian
```

### Running Applications
```bash
# Main YouTube transcription app
streamlit run transcribe_app.py

# Local transcription with Gemini integration
streamlit run transcribe_with_gemini.py

# Command-line transcription with Gemini
python local_transcribe.py <audio_file> --model base --task summarize

# Transcription with faster-whisper and Gemini summarization
python transcribe_and_summarize.py <audio_file>
```

## Architecture Overview

This is a YouTube transcription project with multiple interfaces and processing options:

### Core Components

1. **Streamlit Web Apps**
   - `transcribe_app.py`: Main YouTube-to-text transcription interface
   - `transcribe_with_gemini.py`: Local audio file processing with Gemini integration
   - `youtube_transcribe_app.py`: Alternative YouTube transcription interface

2. **Command-Line Scripts**
   - `local_transcribe.py`: CLI tool for transcribing local audio files with Gemini post-processing
   - `transcribe_and_summarize.py`: Uses faster-whisper for transcription and Gemini for summarization
   - `transcribe_full.py`: Full transcription pipeline
   - `quick_transcribe.py`: Simplified transcription script

3. **Utility Scripts**
   - `youtube_downloader.py`: YouTube audio download functionality
   - `simple_download_app.py`: Simple download interface
   - `transcribe_youtube.sh`: Shell script for YouTube transcription

### Key Dependencies
- **OpenAI Whisper**: Primary transcription engine with multiple model sizes (tiny, base, small, medium, large)
- **yt-dlp**: YouTube audio extraction
- **Streamlit**: Web interface framework
- **Gemini API**: Integration with Google's Gemini for transcription and post-processing tasks

### Audio Processing Pipeline
1. **Download**: YouTube URLs → audio files (mp3) via yt-dlp
2. **Transcription**: Audio files → text via Whisper models
3. **Processing**: Text → enhanced output via Gemini (summarization, translation, formatting, analysis)
4. **Output**: Downloadable text files with transcriptions and processed content

### Model Selection Strategy
- **tiny**: Fastest, least accurate (~1GB) - good for quick testing
- **base**: Balanced speed/accuracy (~1GB) - recommended default
- **small**: Better accuracy (~2GB) - good for production use
- **medium**: High accuracy (~5GB) - for high-quality transcriptions
- **large**: Best accuracy (~10GB) - for maximum quality

The codebase supports both online (YouTube) and offline (local file) transcription workflows with optional Gemini integration for post-processing tasks.