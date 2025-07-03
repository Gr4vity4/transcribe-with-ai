import streamlit as st
import yt_dlp
import os
import subprocess
import tempfile
from pathlib import Path
from faster_whisper import WhisperModel
import time

def download_audio(youtube_url, progress_bar, status_text):
    """Download audio from YouTube URL"""
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
            
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename) and os.path.exists(filename.replace('.webm', '.m4a')):
                filename = filename.replace('.webm', '.m4a')
            
        if os.path.exists(filename):
            return filename, video_title, duration
        else:
            raise Exception("Failed to download audio")
    except Exception as e:
        raise Exception(f"Error: {str(e)}")

def transcribe_audio(audio_file, model_size="base", progress_callback=None):
    """Transcribe audio using faster-whisper"""
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    segments, info = model.transcribe(audio_file, beam_size=2)
    
    transcription = []
    segment_count = 0
    
    for segment in segments:
        transcription.append(segment.text.strip())
        segment_count += 1
        if progress_callback and segment_count % 5 == 0:
            progress_callback(segment_count, segment.end)
    
    return " ".join(transcription), info.language, segment_count

def summarize_with_claude(text, language):
    """Summarize text using Claude CLI"""
    if language != "en":
        prompt = f"""This is a transcription in {language} language. Please:
1. Identify the main topic
2. Provide a brief English summary (2-3 sentences)
3. List 3-5 key points

Transcription (excerpt):
{text[:2500]}"""
    else:
        prompt = f"""Please analyze this transcription and provide:
1. A concise summary (2-3 sentences)
2. Main topics discussed
3. Key takeaways (3-5 bullet points)

Transcription (excerpt):
{text[:2500]}"""
    
    try:
        result = subprocess.run(
            ["claude", prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except:
        return None

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
    st.set_page_config(page_title="YouTube Transcribe & Summarize", page_icon="🎬")
    
    st.title("🎬 YouTube Transcribe & Summarize")
    st.markdown("Download, transcribe, and summarize YouTube videos with AI")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📥 Download & Transcribe", "📂 Previous Files", "ℹ️ Help"])
    
    with tab1:
        youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        
        col1, col2 = st.columns(2)
        with col1:
            model_size = st.selectbox(
                "Transcription Model",
                ["tiny", "base", "small", "medium"],
                index=1,
                help="Larger models are more accurate but slower"
            )
        
        with col2:
            auto_transcribe = st.checkbox("Auto-transcribe after download", value=True)
        
        if st.button("🚀 Start Process", type="primary"):
            if youtube_url:
                try:
                    # Step 1: Download
                    st.subheader("Step 1: Downloading Audio")
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    audio_path, video_title, duration = download_audio(youtube_url, progress_bar, status_text)
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success(f"✅ Downloaded: {video_title}")
                    st.info(f"⏱️ Duration: {format_duration(duration)}")
                    
                    # Save to session state
                    st.session_state['last_download'] = {
                        'path': audio_path,
                        'title': video_title,
                        'duration': duration
                    }
                    
                    if auto_transcribe:
                        # Step 2: Transcribe
                        st.subheader("Step 2: Transcribing Audio")
                        
                        progress_container = st.container()
                        with progress_container:
                            progress_text = st.empty()
                            progress_text.text(f"Loading {model_size} model...")
                        
                        def update_progress(segments, time_processed):
                            progress_text.text(f"Processed {segments} segments ({time_processed:.1f}s)...")
                        
                        start_time = time.time()
                        transcription, language, total_segments = transcribe_audio(
                            audio_path, model_size, update_progress
                        )
                        elapsed = time.time() - start_time
                        
                        progress_text.text(f"✅ Transcribed {total_segments} segments in {elapsed:.1f}s")
                        
                        # Save transcription
                        transcript_file = audio_path.rsplit('.', 1)[0] + "_transcript.txt"
                        with open(transcript_file, 'w', encoding='utf-8') as f:
                            f.write(transcription)
                        
                        st.success(f"📝 Language: {language}")
                        
                        # Show transcription
                        with st.expander("📄 View Transcription", expanded=False):
                            st.text_area("", transcription, height=200)
                        
                        # Download button for transcription
                        st.download_button(
                            "📥 Download Transcript",
                            transcription,
                            f"{video_title}_transcript.txt",
                            mime="text/plain"
                        )
                        
                        # Step 3: Claude Summary
                        st.subheader("Step 3: AI Summary")
                        
                        with st.spinner("🤖 Generating summary with Claude..."):
                            summary = summarize_with_claude(transcription, language)
                        
                        if summary:
                            st.write(summary)
                            
                            # Save summary
                            summary_file = audio_path.rsplit('.', 1)[0] + "_summary.txt"
                            with open(summary_file, 'w', encoding='utf-8') as f:
                                f.write(summary)
                            
                            st.download_button(
                                "📥 Download Summary",
                                summary,
                                f"{video_title}_summary.txt",
                                mime="text/plain"
                            )
                        else:
                            st.warning("Claude CLI not available. Install with: `pip install anthropic && claude login`")
                    
                    # Audio player
                    with open(audio_path, 'rb') as audio_file:
                        st.audio(audio_file.read())
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter a YouTube URL")
    
    with tab2:
        download_dir = os.path.join(os.getcwd(), "downloads")
        if os.path.exists(download_dir):
            files = sorted([f for f in os.listdir(download_dir) if f.endswith(('.m4a', '.mp3', '.webm'))], 
                          key=lambda x: os.path.getmtime(os.path.join(download_dir, x)), 
                          reverse=True)
            
            if files:
                st.subheader("📂 Previous Downloads")
                
                for file in files[:10]:  # Show last 10
                    file_path = os.path.join(download_dir, file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.text(f"🎵 {file[:50]}...")
                    
                    with col2:
                        st.text(f"{file_size:.1f} MB")
                    
                    with col3:
                        if st.button("Transcribe", key=f"trans_{file}"):
                            st.session_state['transcribe_file'] = file_path
                            st.rerun()
                
                # Handle transcription request
                if 'transcribe_file' in st.session_state:
                    file_to_transcribe = st.session_state['transcribe_file']
                    del st.session_state['transcribe_file']
                    
                    st.divider()
                    st.subheader(f"Transcribing: {Path(file_to_transcribe).name}")
                    
                    model = st.selectbox("Model", ["tiny", "base", "small"], key="model2")
                    
                    if st.button("Start Transcription"):
                        with st.spinner(f"Transcribing with {model} model..."):
                            transcription, language, segments = transcribe_audio(file_to_transcribe, model)
                        
                        st.success(f"✅ Transcribed! Language: {language}")
                        
                        with st.expander("View Transcription"):
                            st.text_area("", transcription, height=200)
                        
                        # Claude summary
                        with st.spinner("Getting Claude summary..."):
                            summary = summarize_with_claude(transcription, language)
                        
                        if summary:
                            st.subheader("AI Summary")
                            st.write(summary)
            else:
                st.info("No downloaded files yet")
        else:
            st.info("Downloads folder not found")
    
    with tab3:
        st.markdown("""
        ### 🚀 How to Use
        
        1. **Paste a YouTube URL** and click "Start Process"
        2. The app will:
           - Download the audio
           - Transcribe it using Whisper
           - Generate a summary with Claude
        
        ### 🎯 Model Selection
        - **Tiny**: Fastest, least accurate (~39MB)
        - **Base**: Good balance (~74MB)
        - **Small**: Better accuracy (~244MB)
        - **Medium**: Best accuracy (~769MB)
        
        ### 📋 Requirements
        - FFmpeg (for audio processing)
        - Claude CLI (for summaries): `pip install anthropic && claude login`
        
        ### 💡 Tips
        - First run will download the model (~1-5 min)
        - Longer videos take more time to process
        - Transcriptions and summaries are saved automatically
        """)

if __name__ == "__main__":
    main()