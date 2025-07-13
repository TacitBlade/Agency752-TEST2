import streamlit as st
import requests

st.set_page_config(page_title="📄 OneDrive File Viewer", layout="centered")
st.title("📄 View File from OneDrive Link")

file_url = st.text_input("https://1drv.ms/f/c/5b477b3909c98aee/Es1gCTDMmUxKkg-n16H88HkBur_Pq9neRe7pVDCUAspFHw?e=p0DD88")

if file_url:
    try:
        response = requests.get(file_url)
        response.raise_for_status()

        # Guess file type by content-type header
        content_type = response.headers.get('Content-Type', '')
        
        if 'text' in content_type:
            st.subheader("🔍 File Preview (Text)")
            st.text(response.text[:500])  # Display first 500 characters
        elif 'image' in content_type:
            st.subheader("🖼️ File Preview (Image)")
            st.image(response.content)
        else:
            st.info("File downloaded successfully, but type not previewable.")
            st.download_button("Download File", response.content, "file_download")

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching file: {e}")
