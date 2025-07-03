import streamlit as st
import yt_dlp
import os

def download_audio(youtube_url, progress_bar, status_text):
    """Download audio from YouTube URL"""
    # Create downloads folder
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)
    
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
    
    # Download without conversion
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [progress_hook],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            # Get the actual filename
            filename = ydl.prepare_filename(info)
            # Check for m4a extension
            if not os.path.exists(filename) and os.path.exists(filename.replace('.webm', '.m4a')):
                filename = filename.replace('.webm', '.m4a')
            
        if os.path.exists(filename):
            return filename, video_title, duration
        else:
            raise Exception("Failed to download audio")
    except Exception as e:
        raise Exception(f"Error: {str(e)}")

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
    st.set_page_config(page_title="YouTube Downloader", page_icon="🎵")
    
    st.title("🎵 YouTube Audio Downloader")
    st.markdown("Download audio from YouTube videos to local folder")
    
    # Show downloads folder location
    download_dir = os.path.join(os.getcwd(), "downloads")
    st.info(f"📁 Files will be saved to: `{download_dir}`")
    
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
                st.info(f"⏱️ Duration: {format_duration(duration)}")
                st.success(f"💾 Saved to: `{audio_path}`")
                
                # Show file size
                file_size = os.path.getsize(audio_path) / (1024 * 1024)  # MB
                st.info(f"📊 File size: {file_size:.2f} MB")
                
                # Play audio
                with open(audio_path, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                
                st.audio(audio_bytes)
                
            except Exception as e:
                st.error(f"❌ {str(e)}")
        else:
            st.warning("⚠️ Please enter a YouTube URL")
    
    # Show existing downloads
    if os.path.exists(download_dir):
        files = [f for f in os.listdir(download_dir) if f.endswith(('.m4a', '.mp3', '.webm'))]
        if files:
            st.markdown("---")
            st.subheader("📂 Previous Downloads")
            for file in sorted(files, reverse=True)[:5]:  # Show last 5
                st.text(f"• {file}")

if __name__ == "__main__":
    main()