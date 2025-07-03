import streamlit as st
import yt_dlp
import whisper
import os
import tempfile
from pathlib import Path

def download_audio(youtube_url):
    """Download audio from YouTube URL"""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "audio.mp3")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_path.replace('.mp3', '.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_title = info.get('title', 'Unknown')
            
        if os.path.exists(output_path):
            with open(output_path, 'rb') as f:
                audio_data = f.read()
            return audio_data, video_title
        else:
            raise Exception("Failed to download audio")

def transcribe_audio(audio_data, model_name="base"):
    """Transcribe audio using Whisper"""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file.write(audio_data)
        tmp_file_path = tmp_file.name
    
    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(tmp_file_path)
        return result["text"]
    finally:
        os.unlink(tmp_file_path)

def main():
    st.set_page_config(page_title="YouTube Transcription App", page_icon="🎥")
    
    st.title("🎥 YouTube Transcription App")
    st.markdown("Enter a YouTube URL to transcribe the audio content")
    
    youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    
    model_options = ["tiny", "base", "small", "medium", "large"]
    selected_model = st.selectbox("Select Whisper Model", model_options, index=1)
    
    if st.button("Transcribe", type="primary"):
        if youtube_url:
            try:
                with st.spinner("Downloading audio from YouTube..."):
                    audio_data, video_title = download_audio(youtube_url)
                
                st.success(f"Downloaded: {video_title}")
                
                with st.spinner(f"Transcribing audio using {selected_model} model..."):
                    transcription = transcribe_audio(audio_data, selected_model)
                
                st.subheader("Transcription")
                st.text_area("", transcription, height=300)
                
                st.download_button(
                    label="Download Transcription",
                    data=transcription,
                    file_name=f"{video_title[:50]}_transcription.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a YouTube URL")

if __name__ == "__main__":
    main()