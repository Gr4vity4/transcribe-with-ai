import streamlit as st
import subprocess
import os
import tempfile
from pathlib import Path

def check_claude_cli():
    """Check if Claude CLI is installed"""
    try:
        result = subprocess.run(["claude", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def transcribe_and_process(audio_file, model="base", task="summarize"):
    """Run the local transcription script"""
    script_path = os.path.join(os.path.dirname(__file__), "local_transcribe.py")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.name).suffix) as tmp_file:
        tmp_file.write(audio_file.read())
        tmp_path = tmp_file.name
    
    try:
        # Run transcription script
        cmd = [
            "python", script_path,
            tmp_path,
            "--model", model,
            "--task", task
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Get transcript file
        transcript_file = Path(tmp_path).stem + "_transcript.txt"
        transcript_text = ""
        if os.path.exists(transcript_file):
            with open(transcript_file, 'r') as f:
                transcript_text = f.read()
            os.remove(transcript_file)
        
        return result.stdout, result.stderr, transcript_text
        
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def main():
    st.set_page_config(page_title="Transcribe with Claude", page_icon="🎙️")
    
    st.title("🎙️ Local Transcription with Claude")
    st.markdown("Transcribe audio files using Whisper and process with Claude CLI")
    
    # Check Claude CLI
    if not check_claude_cli():
        st.error("⚠️ Claude CLI not found! Please install it first:")
        st.code("pip install anthropic", language="bash")
        st.code("claude login", language="bash")
        st.markdown("See [Claude CLI docs](https://github.com/anthropics/anthropic-sdk-python) for setup")
    
    # File upload
    audio_file = st.file_uploader(
        "Upload audio file",
        type=['mp3', 'm4a', 'wav', 'flac', 'aac', 'ogg', 'wma']
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        model = st.selectbox(
            "Whisper Model",
            ["tiny", "base", "small", "medium", "large"],
            index=1,
            help="Larger models are more accurate but slower"
        )
    
    with col2:
        task = st.selectbox(
            "Claude Task",
            ["summarize", "translate", "format", "analyze"],
            help="What Claude should do with the transcription"
        )
    
    if audio_file:
        st.audio(audio_file)
        
        if st.button("Transcribe & Process", type="primary"):
            with st.spinner("Installing dependencies..."):
                # Install whisper if needed
                subprocess.run([
                    "pip", "install", "openai-whisper"
                ], capture_output=True)
            
            with st.spinner(f"Transcribing with {model} model..."):
                stdout, stderr, transcript = transcribe_and_process(audio_file, model, task)
            
            if transcript:
                st.success("✅ Transcription complete!")
                
                # Show transcription
                with st.expander("📝 Raw Transcription", expanded=False):
                    st.text_area("", transcript, height=200)
                
                # Show Claude output
                if "Claude's response:" in stdout:
                    claude_output = stdout.split("Claude's response:")[1].split("=" * 50)[1].strip()
                    st.subheader(f"🤖 Claude's {task.title()}")
                    st.write(claude_output)
                
                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "Download Transcription",
                        transcript,
                        f"{Path(audio_file.name).stem}_transcript.txt",
                        mime="text/plain"
                    )
                with col2:
                    if "Claude's response:" in stdout:
                        st.download_button(
                            f"Download {task.title()}",
                            claude_output,
                            f"{Path(audio_file.name).stem}_{task}.txt",
                            mime="text/plain"
                        )
            
            if stderr:
                st.error("Error occurred:")
                st.code(stderr)
    
    # Instructions
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. **Upload an audio file** from your computer
        2. **Select Whisper model** (base is recommended for balance)
        3. **Choose Claude task** for processing
        4. **Click Transcribe & Process**
        
        The app will:
        - Transcribe audio locally using Whisper
        - Process the transcription with Claude CLI
        - Show both raw transcription and Claude's output
        """)

if __name__ == "__main__":
    main()