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
    skipped_sheets = []

    for sheet_name, df in excel_data.items():
        if 'Agency Name' not in df.columns or 'Date' not in df.columns:
            skipped_sheets.append(sheet_name)
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
        return result_df, skipped_sheets
    else:
        return pd.DataFrame(), skipped_sheets

# 🎛 Streamlit UI
st.title("📊 Multi Agency PK Event Filter")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])
agency_input = st.text_input("Enter Agency Names (comma-separated)", value="Alpha Agency")
host_name_input = st.text_input("Enter Host Name to Search (optional)")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

if uploaded_file and agency_input and start_date and end_date:
    st.info("🔍 Filtering events from multiple agencies...")

    raw_df, skipped_sheets = process_excel_file(
        uploaded_file,
        pd.to_datetime(start_date),
        pd.to_datetime(end_date),
        agency_input,
        host_name_input
    )

    if not raw_df.empty:
        # Dynamically populate PK type filter
        pk_type_options = sorted(raw_df['PK Type'].dropna().unique())
        pk_type_filter = st.multiselect("Filter by PK Type", options=pk_type_options, default=pk_type_options)

        time_filter = st.text_input("Filter by Time (optional, partial match)")
        id1_filter = st.text_input("Filter by ID1 (optional, partial match)")
        id2_filter = st.text_input("Filter by ID2 (optional, partial match)")

        filtered_df = raw_df.copy()

        if pk_type_filter:
            filtered_df = filtered_df[filtered_df['PK Type'].isin(pk_type_filter)]
        if time_filter:
            filtered_df = filtered_df[filtered_df['Time'].str.contains(time_filter, case=False, na=False)]
        if id1_filter:
            filtered_df = filtered_df[filtered_df['ID1'].str.contains(id1_filter, case=False, na=False)]
        if id2_filter:
            filtered_df = filtered_df[filtered_df['ID2'].str.contains(id2_filter, case=False, na=False)]

        if not filtered_df.empty:
            st.success("✅ Results filtered!")

            st.subheader("📄 Combined Preview")
            st.dataframe(filtered_df)

            st.write(f"🧮 Total events matched: {len(filtered_df)}")

            # Generate downloadable Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, sheet_name='Filtered PK Events', index=False)
            output.seek(0)

            st.download_button(
                label="📥 Download Filtered Excel",
                data=output,
                file_name="filtered_pk_events.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            if skipped_sheets:
                with st.expander("🧾 Skipped Sheets (Developer Only)", expanded=False):
                    st.write("Sheets skipped due to missing required columns:")
                    for sheet in skipped_sheets:
                        st.markdown(f"- `{sheet}`")
        else:
            st.warning("⚠️ No matches found for the applied filters.")
    else:
        st.warning("⚠️ No matching records found in any sheet.")

