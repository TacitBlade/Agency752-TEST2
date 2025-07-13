import streamlit as st
import requests
from bs4 import BeautifulSoup
import os

st.set_page_config(page_title="📁 OneDrive Folder Viewer", layout="wide")
st.title("📁 View OneDrive Folder Contents")

folder_url = st.text_input("Enter the OneDrive folder share link:")
FOLDER_PATH = st.text_input("Enter the local folder path:")

def list_onedrive_files(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        links = soup.find_all('a')
        file_links = []

        for link in links:
            href = link.get('href')
            text = link.text.strip()
            if href and "redir" in href:  # crude filter for OneDrive file links
                file_links.append((text, href))
        
        return file_links, None

    except Exception as e:
        return [], str(e)

if folder_url:
    files, error = list_onedrive_files(folder_url)
    
    if error:
        st.error(f"Could not retrieve folder: {error}")
    elif not files:
        st.warning("No files found or unable to parse folder contents.")
    else:
        st.success(f"Found {len(files)} file(s) in the folder.")
        for name, link in files:
            st.markdown(f"[📄 {name}]({link})")

        # Optional: Allow preview of one of the links
        selected_link = st.selectbox("Select a file to preview", [f[1] for f in files])
        if selected_link:
            preview_response = requests.get(selected_link)
            if "image" in preview_response.headers.get("Content-Type", ""):
                st.image(preview_response.content)
            elif "text" in preview_response.headers.get("Content-Type", ""):
                st.text(preview_response.text[:500])
            else:
                st.info("File type not previewable. Use download below.")
                st.download_button("Download File", preview_response.content, "downloaded_file")

if FOLDER_PATH:
    if os.path.exists(FOLDER_PATH):
        st.write("Files in folder:", os.listdir(FOLDER_PATH))
        excel_files = [f for f in os.listdir(FOLDER_PATH) if f.endswith(('.xlsx', '.xls'))]
        st.write("Excel files found:", excel_files)
    else:
        st.error(f"Folder not found: {FOLDER_PATH}")
