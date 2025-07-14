import streamlit as st
import pandas as pd
from io import BytesIO

def process_excel_file(uploaded_file):
    excel_data = pd.read_excel(uploaded_file, sheet_name=None)
    filtered_data = {}

    for sheet_name, df in excel_data.items():
        if 'Agency Name' in df.columns:
            filtered_df = df[df['Agency Name'].astype(str).str.contains('Alpha Agency', case=False, na=False)]
            if not filtered_df.empty:
                filtered_data[sheet_name] = filtered_df

    if filtered_data:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, df in filtered_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)
        return output
    else:
        return None

st.title("🔍 Filter Excel Sheets by 'Alpha Agency'")

uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    filtered_output = process_excel_file(uploaded_file)

    if filtered_output:
        st.success("✅ Matching data found and filtered.")
        st.download_button(
            label="📥 Download Filtered File",
            data=filtered_output,
            file_name="filtered_agency_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No data found for 'Alpha Agency' in the uploaded sheets.")