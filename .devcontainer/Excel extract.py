import streamlit as st
import pandas as pd
from io import BytesIO

def extract_alpha_agency_data(df):
    # Filter for "Alpha Agency"
    filtered = df[df['agency'] == 'Alpha Agency']
    # Select relevant columns (adjust as needed based on actual column names)
    return filtered[['date', 'time', 'agency', 'id1', 'id2']]

def process_sheets(file):
    xl = pd.ExcelFile(file)
    output = pd.DataFrame()

    for sheet_name in ['Talent', 'Star Task']:
        if sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)
            cleaned_df = extract_alpha_agency_data(df)
            output = pd.concat([output, cleaned_df], ignore_index=True)

    return output

def to_excel_bytes(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Alpha Agency')
    return buffer.getvalue()

# Streamlit UI
st.title("📋 Alpha Agency Event Extractor")

uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    extracted_df = process_sheets(uploaded_file)
    st.success("Data extracted successfully!")
    st.dataframe(extracted_df)

    excel_bytes = to_excel_bytes(extracted_df)
    st.download_button(
        label="Download Filtered Data as Excel",
        data=excel_bytes,
        file_name="Alpha_Agency_Events.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )