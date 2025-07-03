import streamlit as st
import google.generativeai as genai
import subprocess
import tempfile
import os
import mimetypes
from datetime import datetime
import yt_dlp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY not found in environment variables. Please check your .env file.")
    st.stop()

# Get Gemini model from environment with default fallback
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

genai.configure(api_key=GEMINI_API_KEY)

def get_mime_type(audio_path):
    """Get MIME type for audio file"""
    mime_type, _ = mimetypes.guess_type(audio_path)
    if mime_type and mime_type.startswith('audio/'):
        return mime_type
    
    # Default fallback based on file extension
    ext = os.path.splitext(audio_path)[1].lower()
    mime_map = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.m4a': 'audio/mp4',
        '.aac': 'audio/aac',
        '.flac': 'audio/flac',
        '.ogg': 'audio/ogg'
    }
    return mime_map.get(ext, 'audio/wav')

def transcribe_with_gemini(audio_path):
    """Transcribe audio using Gemini API"""
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Get MIME type for the audio file
        mime_type = get_mime_type(audio_path)
        
        # Upload audio file
        uploaded_file = genai.upload_file(path=audio_path, mime_type=mime_type)
        
        # Generate transcription
        response = model.generate_content([
            "Please transcribe this audio file accurately. Return only the transcribed text without any additional commentary or formatting.",
            uploaded_file
        ])
        
        # Clean up uploaded file
        genai.delete_file(uploaded_file.name)
        
        return response.text
    
    except Exception as e:
        st.error(f"Error transcribing with Gemini: {e}")
        return None

def process_with_claude(text, task="summarize", target_language="English"):
    """Process text using Claude CLI"""
    try:
        # Prepare the prompt based on task and target language
        if task == "summarize":
            prompt = f"Please provide a concise summary of the following transcript in {target_language}:\n\n{text}"
        elif task == "translate":
            prompt = f"Please translate the following transcript to {target_language}:\n\n{text}"
        elif task == "analyze":
            prompt = f"Please analyze the key points and themes in the following transcript in {target_language}:\n\n{text}"
        else:
            prompt = f"Please {task} the following transcript in {target_language}:\n\n{text}"
        
        # Use Claude CLI with --print flag for non-interactive mode
        result = subprocess.run([
            'claude', '--print', prompt
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            st.error(f"Error with Claude CLI: {result.stderr}")
            return None
    
    except Exception as e:
        st.error(f"Error processing with Claude: {e}")
        return None

def download_youtube_audio(youtube_url, progress_bar, status_text):
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
                progress_bar.progress(percent * 0.3)  # Use 30% of progress bar for download
                status_text.text(f"Downloading: {percent*100:.1f}%")
            else:
                status_text.text("Downloading...")
        elif d['status'] == 'finished':
            progress_bar.progress(0.3)
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
    st.set_page_config(
        page_title="Gemini + Claude Transcription",
        page_icon="🎙️",
        layout="wide"
    )
    
    # Add custom CSS for reading mode
    st.markdown("""
    <style>
    .reading-mode {
        max-width: 100%;
        margin: 0;
        padding: 80px 40px 40px 40px;
        line-height: 1.8;
        font-size: 18px;
        font-family: 'Charter', 'Georgia', serif;
        color: #292929;
        background: #ffffff;
        min-height: 100vh;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 999;
        overflow-y: auto;
        box-sizing: border-box;
    }
    
    .reading-mode h1, .reading-mode h2, .reading-mode h3 {
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 600;
        margin-top: 2em;
        margin-bottom: 0.5em;
        color: #242424;
    }
    
    .reading-mode h1 {
        font-size: 32px;
        margin-bottom: 16px;
    }
    
    .reading-mode h2 {
        font-size: 24px;
        margin-bottom: 12px;
    }
    
    .reading-mode p {
        margin-bottom: 1.5em;
        text-align: justify;
    }
    
    .reading-mode ul, .reading-mode ol {
        margin-bottom: 1.5em;
        padding-left: 1.5em;
    }
    
    .reading-mode li {
        margin-bottom: 0.5em;
    }
    
    .reading-mode blockquote {
        border-left: 3px solid #e6e6e6;
        margin: 1.5em 0;
        padding-left: 1.5em;
        font-style: italic;
        color: #6b6b6b;
    }
    
    .reading-mode-button {
        background: #1a73e8;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        cursor: pointer;
        margin-bottom: 20px;
        transition: background-color 0.3s;
    }
    
    .reading-mode-button:hover {
        background: #1557b0;
    }
    
    .exit-reading-mode {
        text-align: center;
        margin-bottom: 20px;
        position: sticky;
        top: 0;
        background: #ffffff;
        padding: 20px 0;
        border-bottom: 1px solid #e0e0e0;
        z-index: 1001;
    }
    
    .exit-reading-mode button {
        background: #f8f9fa;
        color: #5f6368;
        border: 1px solid #dadce0;
        padding: 12px 24px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .exit-reading-mode button:hover {
        background: #e8f0fe;
        border-color: #1a73e8;
        color: #1a73e8;
    }
    
    /* Hide Streamlit elements in reading mode */
    .reading-mode-active .stSidebar {
        display: none;
    }
    
    .reading-mode-active .stMainBlockContainer {
        padding: 0;
    }
    
    .reading-mode-active .stAppHeader {
        display: none;
    }
    
    .reading-mode-content {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 40px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🎙️ Audio Transcription with Gemini + Claude")
    st.markdown("Upload an audio file to transcribe with Gemini API and process with Claude CLI")
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # Display current Gemini model
    st.sidebar.info(f"📡 Using Gemini Model: **{GEMINI_MODEL}**")
    
    # Task selection
    task = st.sidebar.selectbox(
        "Claude Processing Task",
        ["summarize", "translate", "analyze"],
        index=0,
        help="Choose how Claude should process the transcript"
    )
    
    # Language selection
    target_language = st.sidebar.selectbox(
        "Target Language",
        ["English", "Thai", "Japanese", "Korean", "Chinese", "French", "German", "Spanish"],
        index=0,
        help="Choose the language for Claude's output"
    )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Audio Input")
        
        # Create tabs for different input methods
        input_tab1, input_tab2 = st.tabs(["📁 Upload File", "🎥 YouTube URL"])
        
        with input_tab1:
            uploaded_file = st.file_uploader(
                "Choose an audio file",
                type=['mp3', 'wav', 'm4a', 'aac', 'flac', 'ogg'],
                help="Supported formats: MP3, WAV, M4A, AAC, FLAC, OGG"
            )
            
            if uploaded_file is not None:
                # Display file info
                st.info(f"File: {uploaded_file.name}")
                st.info(f"Size: {uploaded_file.size / (1024*1024):.2f} MB")
                
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_path = tmp_file.name
                
                # Process button
                if st.button("🚀 Transcribe & Process", type="primary", key="upload_process"):
                    try:
                        # Progress tracking
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Step 1: Transcribe with Gemini
                        status_text.text("Transcribing audio with Gemini API...")
                        progress_bar.progress(25)
                        
                        transcript = transcribe_with_gemini(temp_path)
                        
                        if transcript:
                            progress_bar.progress(50)
                            status_text.text("Transcription completed! Processing with Claude...")
                            
                            # Step 2: Process with Claude
                            progress_bar.progress(75)
                            processed_text = process_with_claude(transcript, task, target_language)
                            
                            progress_bar.progress(100)
                            status_text.text("Processing completed!")
                            
                            # Store results in session state
                            st.session_state.transcript = transcript
                            st.session_state.processed_text = processed_text
                            st.session_state.task = task
                            st.session_state.target_language = target_language
                            st.session_state.filename = uploaded_file.name
                            
                        else:
                            st.error("Failed to transcribe audio")
                            
                    except Exception as e:
                        st.error(f"Error during processing: {e}")
                    
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
        
        with input_tab2:
            youtube_url = st.text_input(
                "YouTube URL",
                placeholder="https://www.youtube.com/watch?v=...",
                help="Enter a YouTube video URL to download and transcribe"
            )
            
            if youtube_url:
                # Process YouTube URL
                if st.button("🚀 Download & Transcribe", type="primary", key="youtube_process"):
                    try:
                        # Progress tracking
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Step 1: Download YouTube audio
                        status_text.text("Downloading YouTube audio...")
                        audio_path, video_title, duration = download_youtube_audio(youtube_url, progress_bar, status_text)
                        
                        # Step 2: Transcribe with Gemini
                        status_text.text("Transcribing audio with Gemini API...")
                        progress_bar.progress(60)
                        
                        transcript = transcribe_with_gemini(audio_path)
                        
                        if transcript:
                            progress_bar.progress(80)
                            status_text.text("Transcription completed! Processing with Claude...")
                            
                            # Step 3: Process with Claude
                            processed_text = process_with_claude(transcript, task, target_language)
                            
                            progress_bar.progress(100)
                            status_text.text("Processing completed!")
                            
                            # Store results in session state
                            st.session_state.transcript = transcript
                            st.session_state.processed_text = processed_text
                            st.session_state.task = task
                            st.session_state.target_language = target_language
                            st.session_state.filename = f"{video_title} ({format_duration(duration)})"
                            
                            # Show video info
                            st.success(f"✅ Processed: {video_title}")
                            st.info(f"⏱️ Duration: {format_duration(duration)}")
                            
                        else:
                            st.error("Failed to transcribe audio")
                            
                    except Exception as e:
                        st.error(f"Error during processing: {e}")
            else:
                st.info("Enter a YouTube URL above to get started")
    
    with col2:
        st.header("📝 Results")
        
        # Display results if available
        if hasattr(st.session_state, 'transcript') and st.session_state.transcript:
            
            # Check if reading mode is enabled
            reading_mode = st.session_state.get('reading_mode', False)
            
            if reading_mode:
                # Reading Mode View
                # Add custom styles for the exit button
                st.markdown("""
                <style>
                /* Hide ALL Streamlit UI elements */
                .stApp > header,
                header[data-testid="stHeader"],
                .stDeployButton,
                [data-testid="stToolbar"],
                [data-testid="stDecoration"],
                #MainMenu,
                footer,
                .viewerBadge_container__1QSob,
                .styles_viewerBadge__1yB5_ {
                    display: none !important;
                    visibility: hidden !important;
                    opacity: 0 !important;
                    height: 0 !important;
                    overflow: hidden !important;
                }
                
                /* Hide any element containing "Deploy" text */
                *:has-text("Deploy") {
                    display: none !important;
                }
                
                /* Ensure our button is the only one visible */
                .element-container:has(.stButton) {
                    position: fixed !important;
                    top: 20px !important;
                    right: 20px !important;
                    z-index: 999999 !important;
                    width: auto !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    isolation: isolate !important;
                }
                
                /* Style the exit button */
                .stButton > button {
                    background-color: #ff4b4b;
                    color: white;
                    font-weight: bold;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-size: 16px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    transition: all 0.3s ease;
                }
                
                .stButton > button:hover {
                    background-color: #ff3333;
                    box-shadow: 0 6px 16px rgba(0,0,0,0.4);
                    transform: translateY(-2px);
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Add the exit button first
                if st.button("✕ Exit Full Screen", key="exit_fullscreen_btn"):
                    st.session_state.reading_mode = False
                    st.rerun()
                
                # Format content for reading mode
                content = st.session_state.processed_text or st.session_state.transcript
                
                # Convert content to HTML with proper formatting
                formatted_content = content.replace('\n\n', '</p><p>').replace('\n', '<br>')
                formatted_content = f"<p>{formatted_content}</p>"
                
                # Add headers for sections marked with **
                import re
                formatted_content = re.sub(r'\*\*(.*?)\*\*', r'<h3>\1</h3>', formatted_content)
                
                # Create the full screen reading mode
                st.markdown(f"""
                <div class="reading-mode">
                    <div class="reading-mode-content">
                        <h1>{st.session_state.get('task', 'Summarize').title() if hasattr(st.session_state, 'task') else 'Summarize'} ({st.session_state.get('target_language', 'Thai')})</h1>
                        <p><em>Source: {st.session_state.get('filename', 'Unknown')}</em></p>
                        {formatted_content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                # Normal Tabs View
                # Tabs for different outputs
                tab1, tab2, tab3 = st.tabs(["Original Transcript", f"Claude {st.session_state.task.title()}", "Download"])
                
                with tab1:
                    st.subheader("Original Transcript")
                    st.text_area(
                        "Transcript from Gemini API",
                        value=st.session_state.transcript,
                        height=300,
                        disabled=True
                    )
                
                with tab2:
                    st.subheader(f"Claude {st.session_state.task.title()} ({st.session_state.target_language})")
                    
                    # Add reading mode button
                    col_btn, col_space = st.columns([1, 4])
                    with col_btn:
                        if st.button("📖 Reading Mode", key="enter_reading"):
                            st.session_state.reading_mode = True
                            st.rerun()
                    
                    if st.session_state.processed_text:
                        st.text_area(
                            f"Processed by Claude CLI in {st.session_state.target_language}",
                            value=st.session_state.processed_text,
                            height=300,
                            disabled=True
                        )
                    else:
                        st.warning("Claude processing failed or returned no result")
                
                with tab3:
                    st.subheader("Download Results")
                    
                    # Prepare download content
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    download_content = f"""Audio Transcription Results
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Source File: {st.session_state.filename}
Task: {st.session_state.task.title()} in {st.session_state.target_language}

=== ORIGINAL TRANSCRIPT ===
{st.session_state.transcript}

=== CLAUDE {st.session_state.task.upper()} ({st.session_state.target_language.upper()}) ===
{st.session_state.processed_text or "Processing failed"}
"""
                    
                    st.download_button(
                        label="📥 Download Results",
                        data=download_content,
                        file_name=f"transcript_{timestamp}.txt",
                        mime="text/plain",
                        type="primary"
                    )
                    
                    # Copy to clipboard option
                    st.code(download_content, language=None)
        
        else:
            st.info("Upload an audio file and click 'Transcribe & Process' to see results here.")
    
    # Footer
    st.markdown("---")
    st.markdown("🔧 **Tech Stack**: Gemini API for transcription • Claude CLI for processing")

if __name__ == "__main__":
    main()