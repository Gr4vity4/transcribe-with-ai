import streamlit as st
import yt_dlp
import tempfile
import os

def download_audio(youtube_url, progress_bar, status_text):
    """Download audio from YouTube URL without conversion"""
    with tempfile.TemporaryDirectory() as temp_dir:
        
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
                status_text.text("Download complete!")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                video_title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                filename = ydl.prepare_filename(info)
                
                # Find the actual downloaded file
                for file in os.listdir(temp_dir):
                    if file.startswith(video_title[:20]):
                        filename = os.path.join(temp_dir, file)
                        break
                
            if os.path.exists(filename):
                return filename, video_title, duration
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
    st.markdown("Download audio from YouTube videos (no conversion)")
    
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
                
                # Get file extension
                ext = os.path.splitext(audio_path)[1]
                mime_type = "audio/mp4" if ext in ['.m4a', '.mp4'] else "audio/mpeg"
                
                with open(audio_path, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                
                st.audio(audio_bytes, format=mime_type)
                
                st.download_button(
                    label="Download Audio File",
                    data=audio_bytes,
                    file_name=f"{video_title[:50]}{ext}",
                    mime=mime_type
                )
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a YouTube URL")

if __name__ == "__main__":
    main()