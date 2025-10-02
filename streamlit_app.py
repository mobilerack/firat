import streamlit as st
import requests
import base64

# --- FONTOS! ---
# Mielőtt deployolod, másold be ide a Colab notebook által generált ngrok URL-t!
# A végén a '/transcribe' rész is kell!
COLAB_API_URL = "https://IDE-MASOLD-AZ-NGROK-URL-ED.ngrok.io/transcribe"

# --- UI FELÉPÍTÉSE ---
st.set_page_config(layout="centered", page_title="Feliratkészítő")

# A "Power" gomb, ami megjeleníti a felületet
if 'app_started' not in st.session_state:
    st.session_state.app_started = False

power_button_placeholder = st.empty()

if st.session_state.app_started:
    if power_button_placeholder.button("🔴 Rendszer Leállítása", use_container_width=True):
        st.session_state.app_started = False
        st.rerun() # JAVÍTVA
else:
    if power_button_placeholder.button("🔌 Rendszer Indítása", use_container_width=True):
        st.session_state.app_started = True
        st.rerun() # JAVÍTVA

# Ha a rendszer "be van kapcsolva", megjelenik a többi elem
if st.session_state.app_started:
    st.title("Feliratkészítő")

    # Jobb felső sarok "könyv" gomb a tanításhoz (placeholder)
    with st.popover("📖 Tanítás"):
        st.write("Itt lesznek a tanítási opciók.")
        if st.button("Whisper tanítása"):
            st.info("Ez a funkció még fejlesztés alatt áll.")
        if st.button("Fordító tanítása"):
            st.info("Ez a funkció még fejlesztés alatt áll.")

    # Fő felület
    uploaded_file = st.file_uploader("1. Válassz egy audio- vagy videófájlt", type=["mp3", "mp4", "wav", "m4a", "ogg"])
    output_format = st.selectbox("2. Válassz kimeneti formátumot", ('srt', 'vtt'))
    
    start_button = st.button("3. Átírás Indítása", type="primary", use_container_width=True)

    if start_button and uploaded_file is not None:
        with st.spinner("Feldolgozás a Colab GPU-n... Ez a fájl hosszától függően sokáig tarthat..."):
            try:
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                payload = {'format': output_format}
                
                response = requests.post(COLAB_API_URL, files=files, data=payload, timeout=900) # 15 perces timeout
                response.raise_for_status()
                
                result_data = response.json()
                
                if "result" in result_data:
                    st.session_state.result_text = result_data["result"]
                    st.session_state.filename = f"{uploaded_file.name.split('.')[0]}.{output_format}"
                    st.success("Átírás kész!")
                else:
                    st.error(f"Hiba a szerver oldalon: {result_data.get('error', 'Ismeretlen hiba')}")

            except requests.exceptions.RequestException as e:
                st.error(f"Kommunikációs hiba a Colab szerverrel: {e}")
                st.info("Tipp: Biztos, hogy a Colab notebook még fut, és a helyes ngrok URL van beállítva a kódban?")
            except Exception as e:
                st.error(f"Váratlan hiba: {e}")

    # Eredmény és letöltés gomb megjelenítése
    if 'result_text' in st.session_state:
        st.text_area("Eredmény:", st.session_state.result_text, height=300)
        st.download_button(
            label="Letöltés",
            data=st.session_state.result_text.encode('utf-8'),
            file_name=st.session_state.filename,
            mime=f'text/{output_format}'
        )
