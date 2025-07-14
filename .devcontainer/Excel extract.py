import streamlit as st
import pandas as pd
from io import BytesIO

# Extract rows based on selected column and match value
def extract_matching_rows(df, filter_column, match_value):
    df.columns = df.columns.str.strip().str.lower()
    filter_column = filter_column.strip().lower()

    if filter_column not in df.columns:
        return pd.DataFrame()  # Skip if selected column is missing

    # Normalize column values for comparison
    filtered = df[df[filter_column].astype(str).str.strip().str.lower() == match_value.strip().lower()]

    return filtered if not filtered.empty else pd.DataFrame()

def process_sheets(file, filter_column, match_value):
    xl = pd.ExcelFile(file)
    output = pd.DataFrame()

    for sheet_name in ['Talent', 'Star Task']:
        if sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)
            st.write(f"✅ Processing sheet: {sheet_name}")
            st.write("📌 Columns found:", df.columns.tolist())
            st.write(df.head())  # Show top 5 rows
            matched_df = extract_matching_rows(df, filter_column, match_value)
            output = pd.concat([output, matched_df], ignore_index=True)

    return output

def to_excel_bytes(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Filtered Data')
    return buffer.getvalue()

# Streamlit UI
st.title("🔍 Excel Data Extractor by Column and Value")

uploaded_file = st.file_uploader("📂 Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    xl = pd.ExcelFile(uploaded_file)
    sheet_to_preview = xl.sheet_names[0]
    sample_df = xl.parse(sheet_to_preview)
    sample_df.columns = sample_df.columns.str.strip().str.lower()
    column_options = list(sample_df.columns)

    st.write("📑 Sample columns found in first sheet:", column_options)

    # User selects filter column and value
    selected_column = st.selectbox("🧩 Select column to filter by", column_options)
    match_value = st.text_input("🔎 Enter value to match (case-insensitive)", value="Alpha Agency")

    if selected_column and match_value:
        extracted_df = process_sheets(uploaded_file, selected_column, match_value)

        if not extracted_df.empty:
            st.success("✅ Matching data extracted!")
            st.dataframe(extracted_df)

            excel_bytes = to_excel_bytes(extracted_df)
            st.download_button(
                label="📥 Download Filtered Data as Excel",
                data=excel_bytes,
                file_name="Filtered_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ No rows matched your filter. Please double-check the column and value.")

