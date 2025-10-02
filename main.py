import streamlit as st
import openai
from pathlib import Path
import tempfile
import os

st.set_page_config(page_title="Transcrição de Áudio", layout="wide")

# Sidebar
st.sidebar.header("Configurações")

api_key = st.sidebar.text_input("OpenAI API Key:", type="password")
if api_key:
    openai.api_key = api_key

language = st.sidebar.selectbox(
    "Idioma do áudio:",
    [
        ("Detecção automática", "auto"),
        ("Português", "pt"),
        ("Inglês", "en"),
        ("Espanhol", "es"),
        ("Francês", "fr"),
        ("Alemão", "de"),
        ("Italiano", "it"),
        ("Japonês", "ja"),
        ("Coreano", "ko"),
        ("Chinês", "zh"),
        ("Russo", "ru"),
        ("Árabe", "ar"),
        ("Hindi", "hi"),
        ("Holandês", "nl"),
        ("Turco", "tr")
    ],
    format_func=lambda x: x[0]
)

translate = st.sidebar.checkbox("Traduzir para inglês")

# Main
st.title("Transcrição de Áudio - OpenAI Whisper")

uploaded_file = st.file_uploader(
    "Upload do arquivo de áudio",
    type=["mp3", "mp4", "wav", "m4a", "webm", "ogg", "flac"]
)

if uploaded_file:
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    
    if file_size_mb > 25:
        st.error(f"⚠️ Arquivo muito grande: {file_size_mb:.1f}MB. Limite da OpenAI: 25MB")
        st.stop()
    
    st.info(f"Tamanho do arquivo: {file_size_mb:.1f}MB")

if uploaded_file and st.button("Processar", type="primary"):
    
    if not api_key:
        st.error("⚠️ Insira a API key da OpenAI na barra lateral.")
        st.stop()
    
    with st.spinner("Processando áudio..."):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            with open(tmp_path, "rb") as audio:
                params = {
                    "model": "whisper-1",
                    "file": audio
                }
                
                if language[1] != "auto":
                    params["language"] = language[1]
                
                if translate:
                    result = openai.audio.translations.create(**params)
                else:
                    result = openai.audio.transcriptions.create(**params)
            
            transcript = result.text
            os.unlink(tmp_path)
            
            st.success("✅ Processamento concluído")
            st.text_area("Transcrição:", transcript, height=300)
            
            st.download_button(
                "📥 Baixar transcrição (.txt)",
                transcript,
                file_name="transcricao.txt",
                mime="text/plain"
            )
        
        except Exception as e:
            st.error(f"❌ Erro ao processar: {str(e)}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
