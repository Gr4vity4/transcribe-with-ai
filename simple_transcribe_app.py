import streamlit as st
import yt_dlp
import tempfile
import os

def download_audio(youtube_url, progress_bar, status_text):
    """Download audio from YouTube URL"""
    # Create downloads folder if it doesn't exist
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)
    
    # Use timestamp to make filename unique
    import time
    timestamp = int(time.time())
    output_path = os.path.join(download_dir, f"audio_{timestamp}.mp3")
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            
            if total > 0:
                percent = downloaded / total
                progress_bar.progress(percent)
                status_text.text(f"Downloading: {percent*100:.1f}%")
            else:
                status_text.text("Downloading...")
        elif d['status'] == 'finished':
            progress_bar.progress(1.0)
            status_text.text("Processing audio...")
    
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
        'progress_hooks': [progress_hook],
        'ffmpeg_location': '/usr/local/bin',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
        if os.path.exists(output_path):
            return output_path, video_title, duration
        else:
            raise Exception("Failed to download audio")
    except Exception as e:
        raise Exception(f"Error downloading video: {str(e)}")

def format_duration(seconds):
    """Convert seconds to human-readable format"""
    if seconds:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    return "Unknown"

def main():
    st.set_page_config(page_title="YouTube Audio Downloader", page_icon="🎥")
    
    st.title("🎥 YouTube Audio Downloader")
    st.markdown("Download audio from YouTube videos")
    
    youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("Download Audio", type="primary"):
        if youtube_url:
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                audio_path, video_title, duration = download_audio(youtube_url, progress_bar, status_text)
                
                progress_bar.empty()
                status_text.empty()
                
                st.success(f"✅ Downloaded: {video_title}")
                st.info(f"Duration: {format_duration(duration)}")
                
                with open(audio_path, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                
                st.audio(audio_bytes, format='audio/mp3')
                
                st.download_button(
                    label="Download Audio File",
                    data=audio_bytes,
                    file_name=f"{video_title[:50]}.mp3",
                    mime="audio/mp3"
                )
                
                st.info("ℹ️ For transcription, you can use services like:")
                st.markdown("- [AssemblyAI](https://www.assemblyai.com/)")
                st.markdown("- [Rev.ai](https://www.rev.ai/)")
                st.markdown("- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text)")
                st.markdown("- [AWS Transcribe](https://aws.amazon.com/transcribe/)")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("Make sure you have FFmpeg installed. Install with: `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux)")
        else:
            st.warning("⚠️ Please enter a YouTube URL")

if __name__ == "__main__":
    main()