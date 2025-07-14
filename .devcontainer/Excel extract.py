import streamlit as st
import pandas as pd
from io import BytesIO

# 🔧 Helper to rename/normalize column variants
def normalize_column(df, target_name, possible_names):
    for name in possible_names:
        if name in df.columns:
            df[target_name] = df[name]
            return
    df[target_name] = ""  # Default empty if not found

# 🚀 Main processing logic
def process_excel_file(uploaded_file, start_date, end_date):
    excel_data = pd.read_excel(uploaded_file, sheet_name=None)
    filtered_data = {}

    for sheet_name, df in excel_data.items():
        # Safely handle missing columns
        if 'Agency Name' in df.columns:
            df['Agency Name'] = df['Agency Name'].astype(str)
        else:
            df['Agency Name'] = ""

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce') if 'Date' in df.columns else pd.NaT

        # Filter by agency name and date range
        df_filtered = df[
            df['Agency Name'].str.contains('Alpha Agency', case=False, na=False) &
            (df['Date'] >= start_date) &
            (df['Date'] <= end_date)
        ].copy()

        # Normalize columns
        normalize_column(df_filtered, 'Time', ['Time', 'Start Time', 'Clock', 'Timestamp'])
        normalize_column(df_filtered, 'ID1', ['ID1', 'Identifier1', 'Agent ID'])
        normalize_column(df_filtered, 'ID2', ['ID2', 'Identifier2', 'Reference ID'])

        # Final structure
        output_columns = ['Date', 'Time', 'Agency Name', 'ID1', 'ID2']
        df_final = df_filtered[output_columns]

        if not df_final.empty:
            filtered_data[sheet_name] = df_final

    # Return compiled Excel file
    if filtered_data:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet, df in filtered_data.items():
                df.to_excel(writer, sheet_name=sheet, index=False)
        output.seek(0)
        return output
    else:
        return None

# 🌐 Streamlit UI
st.title("📊 Filter Excel File — Agency, Date Range & Fields")

uploaded_file = st.file_uploader("📁 Upload an Excel file", type=["xlsx"])
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

if uploaded_file and start_date and end_date:
    st.info("⚙️ Filtering file, one moment...")
    result_excel = process_excel_file(uploaded_file, pd.to_datetime(start_date), pd.to_datetime(end_date))

    if result_excel:
        st.success("✅ Data ready and filtered!")

        result_excel.seek(0)
        preview = pd.read_excel(result_excel, sheet_name=None)

        for sheet_name, df in preview.items():
            st.subheader(f"🔍 Sheet Preview: {sheet_name}")
            st.dataframe(df)

        st.download_button(
            label="📥 Download Filtered File",
            data=result_excel,
            file_name="filtered_agency_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No matching entries found for 'Alpha Agency' in selected range.")