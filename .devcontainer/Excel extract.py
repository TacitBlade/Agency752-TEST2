import streamlit as st
import pandas as pd
from io import BytesIO

def process_excel_file(uploaded_file, start_date, end_date):
    excel_data = pd.read_excel(uploaded_file, sheet_name=None)
    filtered_data = {}
    required_columns = ['Date', 'Time', 'Agency Name', 'ID1', 'ID2']

    for sheet_name, df in excel_data.items():
        if 'Agency Name' in df.columns and 'Date' in df.columns:
            # Filter by agency
            df_filtered_agency = df[df['Agency Name'].astype(str).str.contains('Alpha Agency', case=False, na=False)]

            # Convert 'Date' to datetime
            df_filtered_agency['Date'] = pd.to_datetime(df_filtered_agency['Date'], errors='coerce')

            # Filter by date range
            df_filtered_agency = df_filtered_agency[
                (df_filtered_agency['Date'] >= start_date) &
                (df_filtered_agency['Date'] <= end_date)
            ]

            # Only include required columns if they exist
            available_columns = [col for col in required_columns if col in df_filtered_agency.columns]
            df_final = df_filtered_agency[available_columns]

            if not df_final.empty:
                filtered_data[sheet_name] = df_final

    if filtered_data:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, df in filtered_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)
        return output
    else:
        return None

st.title("📊 Filter Excel Data by 'Alpha Agency' and Date Range")

uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])

start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

if uploaded_file and start_date and end_date:
    filtered_output = process_excel_file(uploaded_file, pd.to_datetime(start_date), pd.to_datetime(end_date))

    if filtered_output:
        st.success("✅ Data filtered successfully.")
        st.download_button(
            label="📥 Download Filtered File",
            data=filtered_output,
            file_name="filtered_agency_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No matching data found for 'Alpha Agency' in the selected date range.")