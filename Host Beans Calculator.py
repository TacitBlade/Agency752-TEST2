import streamlit as st
import pandas as pd
import os

# Set up folder path and create if missing
folder_name = "Broadcaster Data"
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
FOLDER_PATH = os.path.join(desktop_path, folder_name)

if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)

st.title("📊 Excel File Viewer")

# List all Excel files in the folder
excel_files = [f for f in os.listdir(FOLDER_PATH) if f.endswith(('.xlsx', '.xls'))]

# Check if any Excel files found
if not excel_files:
    st.error("No Excel files found in the specified folder.")
else:
    # File selection
    selected_file = st.selectbox("Select an Excel file:", excel_files)

    # Load the selected Excel file
    file_path = os.path.join(FOLDER_PATH, selected_file)

    try:
        df = pd.read_excel(file_path)
        st.success(f"Successfully loaded: {selected_file}")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
