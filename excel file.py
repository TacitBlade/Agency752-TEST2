import streamlit as st
import os

def list_folder_contents(folder_path):
    if not os.path.exists(folder_path):
        return [], f"Path '{folder_path}' does not exist."
    if not os.path.isdir(folder_path):
        return [], f"Path '{folder_path}' is not a directory."

    try:
        items = os.listdir(folder_path)
        return items, None
    except Exception as e:
        return [], str(e)

st.set_page_config(page_title="Folder Viewer", layout="wide")
st.title("📂 Local Folder Viewer")

folder_path = st.text_input("Enter the full folder path on your PC:")

if folder_path:
    contents, error = list_folder_contents(folder_path)
    if error:
        st.error(error)
    else:
        st.success(f"Found {len(contents)} items in: {folder_path}")
        for item in sorted(contents):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                st.markdown(f"📁 **{item}**")
            else:
                st.markdown(f"📄 {item}")
