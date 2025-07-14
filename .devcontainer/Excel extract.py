import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl.utils import get_column_letter
from openpyxl import load_workbook

# 🛠 Flexible column matching
def normalize_column(df, target_name, possible_names):
    for name in df.columns:
        if name.strip().lower() in [p.lower().strip() for p in possible_names]:
            df[target_name] = df[name]
            return
    df[target_name] = ""

# 🔍 Process and combine sheets into one DataFrame
def process_excel_file(uploaded_file, start_date, end_date):
    excel_data = pd.read_excel(uploaded_file, sheet_name=None)
    combined_df = []

    for sheet_name, df in excel_data.items():
        # Safely convert 'Agency Name'
        df['Agency Name'] = df['Agency Name'].astype(str) if 'Agency Name' in df.columns else ""
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce') if 'Date' in df.columns else pd.NaT

        filtered = df[
            df['Agency Name'].str.contains('Alpha Agency', case=False, na=False) &
            (df['Date'] >= start_date) &
            (df['Date'] <= end_date)
        ].copy()

        # Normalize column names
        normalize_column(filtered, 'Time', ['Time', 'Start Time', 'PK Time', 'Clock'])
        normalize_column(filtered, 'ID1', ['ID1', 'ID 1', 'Identifier1', 'Agent ID'])
        normalize_column(filtered, 'ID2', ['ID2', 'ID 2', 'Identifier2', 'Reference ID'])

        # Format Date and add PK Type
        filtered['Date'] = filtered['Date'].dt.strftime('%Y-%m-%d')
        filtered['PK Type'] = sheet_name

        final_cols = ['PK Type', 'Date', 'Time', 'Agency Name', 'ID1', 'ID2']
        combined_df.append(filtered[final_cols])

    # Merge all matching rows
    if combined_df:
        result_df = pd.concat(combined_df, ignore_index=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            result_df.to_excel(writer, sheet_name='Filtered PK Events', index=False)

        # 🧼 Auto-adjust column widths
        output.seek(0)
        workbook = load_workbook(output)
        sheet = workbook['Filtered PK Events']
        for col in sheet.columns:
            max_length = max((len(str(cell.value)) if cell.value else 0) for cell in col)
            sheet.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

        final_output = BytesIO()
        workbook.save(final_output)
        final_output.seek(0)
        return final_output, result_df
    else:
        return None, pd.DataFrame()

# 🖥️ Streamlit Interface
st.title("📊 Unified PK Filter — Combine All Sheets")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

if uploaded_file and start_date and end_date:
    st.info("⚙️ Processing and combining PK data...")

    result_excel, preview_df = process_excel_file(uploaded_file, pd.to_datetime(start_date), pd.to_datetime(end_date))

    if not preview_df.empty:
        st.success("✅ Filtered PK data is ready!")

        st.subheader("🔍 Preview: Combined Events")
        st.dataframe(preview_df)

        st.download_button(
            label="📥 Download Combined Excel",
            data=result_excel,
            file_name="combined_filtered_pk.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No matching 'Alpha Agency' events found in the selected date range.")