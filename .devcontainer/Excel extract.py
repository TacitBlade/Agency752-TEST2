import streamlit as st
import pandas as pd
from io import BytesIO

def process_excel_file(uploaded_file, start_date, end_date):
    excel_data = pd.read_excel(uploaded_file, sheet_name=None)
    filtered_data = {}
    required_columns = ['Date', 'Time', 'Agency Name', 'ID1', 'ID2']

    for sheet_name, df in excel_data.items():
        if 'Agency Name' in df.columns and 'Date' in df.columns:
            df['Agency Name'] = df['Agency Name'].astype(str)

            # Filter by agency name
            df_filtered = df[df['Agency Name'].str.contains('Alpha Agency', case=False, na=False)].copy()

            # Convert Date to datetime
            df_filtered['Date'] = pd.to_datetime(df_filtered['Date'], errors='coerce')

            # Filter by date range
            df_filtered = df_filtered[
                (df_filtered['Date'] >= start_date) &
                (df_filtered['Date'] <= end_date)
            ]

            # Ensure all required columns exist
            for col in required_columns:
                if col not in df_filtered.columns:
                    df_filtered[col] = ""

            df_final = df_filtered[required_columns]

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

# Streamlit Interface
st.title("📊 Filter Excel by Agency & Date Range")

uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])
start_date = st.date_input("Select Start Date")
end_date = st.date_input("Select End Date")

if uploaded_file and start_date and end_date:
    st.info("Processing file, please wait...")
    output_excel = process_excel_file(uploaded_file, pd.to_datetime(start_date), pd.to_datetime(end_date))

    if output_excel:
        st.success("✅ Data filtered and ready.")

        # Preview each sheet
        output_excel.seek(0)
        preview_data = pd.read_excel(output_excel, sheet_name=None)

        for sheet_name, df in preview_data.items():
            st.subheader(f"📄 Preview: {sheet_name}")
            st.dataframe(df)

        # Download button
        st.download_button(
            label="📥 Download Filtered File",
            data=output_excel,
            file_name="filtered_agency_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No matching data found for 'Alpha Agency' in the selected range.")