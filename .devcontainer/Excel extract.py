import streamlit as st
import pandas as pd
from io import BytesIO

def extract_alpha_agency_data(df):
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    if 'agency' not in df.columns:
        return pd.DataFrame()  # Skip if 'agency' column is missing

    # Filter for 'Alpha Agency' (case-insensitive and trimmed)
    filtered = df[df['agency'].str.strip().str.lower() == 'alpha agency']

    # Expected columns
    expected_cols = ['date', 'time', 'agency', 'id1', 'id2']
    available_cols = [col for col in expected_cols if col in df.columns]

    return filtered[available_cols] if not filtered.empty else pd.DataFrame()

def process_sheets(file):
    xl = pd.ExcelFile(file)
    output = pd.DataFrame()

    for sheet_name in ['Talent', 'Star Task']:
        if sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)
            st.write(f"✅ Processing sheet: {sheet_name}")
            st.write("🧾 Columns found:", df.columns.tolist())
            st.write(df.head())  # Preview top 5 rows
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

uploaded_file = st.file_uploader("📂 Upload your Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    extracted_df = process_sheets(uploaded_file)

    if not extracted_df.empty:
        st.success("✅ Data extracted successfully!")
        st.dataframe(extracted_df)

        excel_bytes = to_excel_bytes(extracted_df)
        st.download_button(
            label="📥 Download Filtered Data as Excel",
            data=excel_bytes,
            file_name="Alpha_Agency_Events.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No matching 'Alpha Agency' data found. Please check your file.")
