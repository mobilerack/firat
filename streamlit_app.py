import streamlit as st
import requests
import base64

# --- FONTOS! ---
# Másold be ide a Colab notebook által generált ngrok URL-t!
# A végén a '/process' rész is kell!
COLAB_API_URL = "https://scoreless-robbi-priorly.ngrok-free.dev/transcribe"

# --- UI FELÉPÍTÉSE ---
st.set_page_config(layout="centered", page_title="Automata Feliratgyár")
st.title("🤖 Automata Feliratgyár")
st.write("Tölts fel egy audio/videó fájlt, és a rendszer elkészíti a magyar nyelvű SRT feliratot.")

uploaded_file = st.file_uploader("Válassz egy fájlt", type=["mp3", "mp4", "wav", "m4a", "ogg"])
start_button = st.button("Feldolgozás Indítása", type="primary", use_container_width=True, disabled=not uploaded_file)

if start_button:
    st.subheader("Élő napló a Colab szerverről:")
    log_area = st.empty()
    log_messages = []

    try:
        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        
        # Streamelő kérés indítása a Colab API-ra
        response = requests.post(COLAB_API_URL, files=files, stream=True, timeout=900)
        response.raise_for_status()

        b64_data = None
        filename = None
        
        # A beérkező stream feldolgozása darabonként
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            lines = chunk.split('\n')
            for line in lines:
                if not line.strip():
                    continue
                
                prefix, _, content = line.partition(':')
                content = content.strip()

                if prefix == 'LOG':
                    log_messages.append(f"> {content}")
                    log_area.text_area("Napló:", "\n".join(log_messages), height=300)
                elif prefix == 'DATA':
                    b64_data = content
                elif prefix == 'FILENAME':
                    filename = content
        
        if b64_data and filename:
            st.success("Feldolgozás kész! A felirat letölthető.")
            decoded_content = base64.b64decode(b64_data)
            
            st.download_button(
                label="Kész Magyar Felirat Letöltése",
                data=decoded_content,
                file_name=f"magyar_{os.path.splitext(filename)[0]}.srt",
                mime='application/x-subrip'
            )
        else:
            st.error("A szerver nem küldött letölthető fájlt.")

    except requests.exceptions.RequestException as e:
        st.error(f"Kommunikációs hiba a Colab szerverrel: {e}")
        st.info("Tipp: Biztos, hogy a Colab notebook még fut, és a helyes ngrok URL van beállítva?")
    except Exception as e:
        st.error(f"Váratlan hiba: {e}")
