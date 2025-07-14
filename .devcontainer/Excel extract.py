import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl.utils import get_column_letter
from openpyxl import load_workbook

def normalize_column(df, target_name, possible_names):
    for name in df.columns:
        if name.strip().lower() in [p.lower().strip() for p in possible_names]:
            df[target_name] = df[name]
            return
    df[target_name] = ""

def process_excel_file(uploaded_file, start_date, end_date):
    excel_data = pd.read_excel(uploaded_file, sheet_name=None)
    filtered_data = {}

    for sheet_name, df in excel_data.items():
        df['Agency Name'] = df['Agency Name'].astype(str) if 'Agency Name' in df.columns else ""
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce') if 'Date' in df.columns else pd.NaT

        df_filtered = df[
            df['Agency Name'].str.contains('Alpha Agency', case=False, na=False) &
            (df['Date'] >= start_date) &
            (df['Date'] <= end_date)
        ].copy()

        normalize_column(df_filtered, 'Time', ['Time', 'Start Time', 'PK Time', 'Clock'])
        normalize_column(df_filtered, 'ID1', ['ID1', 'ID 1', 'Identifier1', 'Agent ID'])
        normalize_column(df_filtered, 'ID2', ['ID2', 'ID 2', 'Identifier2', 'Reference ID'])

        # Format Date cleanly
        df_filtered['Date'] = df_filtered['Date'].dt.strftime('%Y-%m-%d')

        # ✨ Add PK Type column based on sheet name
        df_filtered['PK Type'] = sheet_name

        final_cols = ['PK Type', 'Date', 'Time', 'Agency Name', 'ID1', 'ID2']
        df_final = df_filtered[final_cols]

        if not df_final.empty:
            filtered_data[sheet_name] = df_final

    if filtered_data:
        temp_output = BytesIO()
        with pd.ExcelWriter(temp_output, engine='openpyxl') as writer:
            for sheet, df in filtered_data.items():
                df.to_excel(writer, sheet_name=sheet, index=False)

        # 🧼 Auto-adjust columns for clean display
        temp_output.seek(0)
        workbook = load_workbook(temp_output)
        for sheet in workbook.worksheets:
            for col in sheet.columns:
                max_length = max((len(str(cell.value)) if cell.value else 0) for cell in col)
                sheet.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2
        final_output = BytesIO()
        workbook.save(final_output)
        final_output.seek(0)
        return final_output
    else:
        return None

# 🎛 Streamlit UI
st.title("📊 Filter Excel — Add PK Type & Clean Output")

uploaded_file = st.file_uploader("📁 Upload Excel File (.xlsx)", type=["xlsx"])
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

if uploaded_file and start_date and end_date:
    st.info("🔧 Processing with PK labeling...")
    result_excel = process_excel_file(uploaded_file, pd.to_datetime(start_date), pd.to_datetime(end_date))

    if result_excel:
        st.success("✅ Filter complete!")

        result_excel.seek(0)
        preview_data = pd.read_excel(result_excel, sheet_name=None)
        for sheet_name, df in preview_data.items():
            st.subheader(f"📄 Sheet Preview: {sheet_name}")
            st.dataframe(df)

        st.download_button(
            label="📥 Download Filtered File with PK Type",
            data=result_excel,
            file_name="filtered_agency_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No matching data found for 'Alpha Agency' in selected range.")