import streamlit as st
import os
import io
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def list_drive_files(service):
    results = service.files().list(
        pageSize=20,
        fields="nextPageToken, files(id, name, mimeType)").execute()
    return results.get('files', [])

def download_file(service, file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">📥 Download {file_name}</a>'
    return href

st.title("📁 Google Drive File Viewer + Downloader")

if st.button("List & Download Files"):
    with st.spinner("Connecting to Google Drive..."):
        try:
            creds = get_credentials()
            service = build('drive', 'v3', credentials=creds)
            files = list_drive_files(service)
            if files:
                st.success("Files retrieved successfully!")
                for file in files:
                    st.write(f"**{file['name']}** _(MIME type: {file['mimeType']})_")
                    if file['mimeType'] != 'application/vnd.google-apps.folder':
                        download_link = download_file(service, file['id'], file['name'])
                        st.markdown(download_link, unsafe_allow_html=True)
            else:
                st.warning("No files found.")
        except Exception as e:
            st.error(f"Error: {e}")