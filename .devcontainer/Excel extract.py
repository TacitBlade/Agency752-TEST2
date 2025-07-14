import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl.utils import get_column_letter
from openpyxl import load_workbook
from difflib import get_close_matches

def normalize_column(df, target_name, possible_names):
    for name in df.columns:
        match = get_close_matches(name.strip().lower(), [p.lower().strip() for p in possible_names], n=1, cutoff=0.8)
        if match:
            df[target_name] = df[name]
            return
    df[target_name] = ""

def process_excel_file(uploaded_file, start_date, end_date, agencies_input, host_name_input):
    agencies = [name.strip().lower() for name in agencies_input.split(",") if name.strip()]
    host_name = host_name_input.strip().lower() if host_name_input else ""
    excel_data = pd.read_excel(uploaded_file, sheet_name=None, usecols=None)
    combined_df = []

    for sheet_name, df in excel_data.items():
        if 'Agency Name' not in df.columns or 'Date' not in df.columns:
            st.warning(f"❌ Skipping sheet '{sheet_name}' – missing 'Agency Name' or 'Date' column.")
            continue

        df['Agency Name'] = df['Agency Name'].astype(str)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        df_filtered = df[
            df['Agency Name'].str.lower().apply(lambda name: any(agency == name.strip().lower() for agency in agencies)) &
            (df['Date'] >= start_date) & 
            (df['Date'] <= end_date)
        ].copy()

        normalize_column(df_filtered, 'Time', ['Time', 'Start Time', 'PK Time', 'Clock'])
        normalize_column(df_filtered, 'ID1', ['ID1', 'ID 1', 'Identifier1', 'Agent ID'])
        normalize_column(df_filtered, 'ID2', ['ID2', 'ID 2', 'Identifier2', 'Reference ID'])

        if host_name:
            df_filtered = df_filtered[
                df_filtered['ID1'].str.lower().str.contains(host_name) |
                df_filtered['ID2'].str.lower().str.contains(host_name)
            ]

        df_filtered['Date'] = df_filtered['Date'].dt.strftime('%Y-%m-%d')
        df_filtered['PK Type'] = sheet_name

        final_cols = ['PK Type', 'Date', 'Time', 'Agency Name', 'ID1', 'ID2']
        combined_df.append(df_filtered[final_cols])

    if combined_df:
        result_df = pd.concat(combined_df, ignore_index=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            result_df.to_excel(writer, sheet_name='Filtered PK Events', index=False)

        output.seek(0)
        workbook = load_workbook(output)
        sheet = workbook['Filtered PK Events']

        for col in sheet.columns:
            max_len = max((len(str(cell.value)) if cell.value else 0) for cell in col)
            sheet.column_dimensions[get_column_letter(col[0].column)].width = max_len + 2

        for cell in sheet[1]:
            cell.font = cell.font.copy(bold=True)
        sheet.freeze_panes = "A2"

        final_output = BytesIO()
        workbook.save(final_output)
        final_output.seek(0)
        return final_output, result_df
    else:
        return None, pd.DataFrame()

# 🎛 Streamlit UI
st.title("📊 Filter Multiple Agencies Across PK Events")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])
agency_input = st.text_input("Enter Agency Names (comma-separated)", value="Alpha Agency")
host_name_input = st.text_input("Enter Host Name to Search (optional)")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

if uploaded_file and agency_input and start_date and end_date:
    st.info("🔍 Filtering events from multiple agencies...")

    result_excel, preview_df = process_excel_file(
        uploaded_file,
        pd.to_datetime(start_date),
        pd.to_datetime(end_date),
        agency_input,
        host_name_input
    )

    if not preview_df.empty:
        st.success("✅ Results filtered!")

        st.subheader("📄 Combined Preview")
        st.dataframe(preview_df)

        st.write(f"🧮 Total events matched: {len(preview_df)}")

        st.download_button(
            label="📥 Download Combined Excel",
            data=result_excel,
            file_name="combined_filtered_pk.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No matches found for the given filters.")
