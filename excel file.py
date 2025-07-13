import streamlit as st
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

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

def list_drive_files(creds):
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        pageSize=20, fields="nextPageToken, files(id, name)").execute()
    return results.get('files', [])

# Streamlit interface
st.title("📁 Google Drive File Viewer")

if st.button("List Files"):
    with st.spinner("Connecting to Google Drive..."):
        try:
            creds = get_credentials()
            files = list_drive_files(creds)
            if files:
                st.success("Files retrieved successfully!")
                for file in files:
                    st.write(f"**{file['name']}** _(ID: {file['id']})_")
            else:
                st.warning("No files found.")
        except Exception as e:
            st.error(f"Error: {e}")