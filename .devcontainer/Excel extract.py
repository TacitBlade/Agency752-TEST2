import streamlit as st
import pandas as pd
from io import BytesIO
from difflib import get_close_matches

# 🔍 Column header normalization
def normalize_header(name):
    return name.strip().lower().replace(" ", "").replace("-", "").replace("_", "")

# 🧬 Sheet profiler
def profile_excel_structure(uploaded_file, expected_cols=None):
    if expected_cols is None:
        expected_cols = ["date", "agencyname", "id1", "id2", "pktime"]

    sheet_data = pd.read_excel(uploaded_file, sheet_name=None)
    profiles = {}

    for sheet_name, df in sheet_data.items():
        raw_cols = df.columns.tolist()
        normalized = [normalize_header(col) for col in raw_cols]
        missing = [col for col in expected_cols if col not in normalized]

        profiles[sheet_name] = {
            "Raw Columns": raw_cols,
            "Normalized": normalized,
            "Missing Expected": missing
        }

    return profiles

# 📦 Normalize columns in each sheet
def normalize_column(df, target_name, possible_names):
    for name in df.columns:
        cleaned = normalize_header(name)
        possible = [normalize_header(p) for p in possible_names]
        if cleaned in possible:
            df[target_name] = df[name]
            return
    df[target_name] = ""

# 🔁 Enhanced filter logic
def enhanced_process_excel(uploaded_file, start_date, end_date, agencies_input, host_name_input, suggest_on_empty=True):
    agencies = [name.strip().lower() for name in agencies_input.split(",") if name.strip()]
    host_name = host_name_input.strip().lower() if host_name_input else ""

    def clean_columns(df):
        df.columns = [col.strip() for col in df.columns]

    def match_agency(name):
        name = name.lower().strip()
        return any(agency in name for agency in agencies)

    def suggest_names(target, all_names):
        return get_close_matches(target.lower(), [n.lower() for n in all_names], n=3, cutoff=0.7)

    excel_data = pd.read_excel(uploaded_file, sheet_name=None)
    combined_df = []
    skipped_sheets = []
    debug_agencies = set()

    for sheet_name, df in excel_data.items():
        clean_columns(df)
        df.columns = [col.strip() for col in df.columns]

        if 'Agency Name' not in df.columns or 'Date' not in df.columns:
            skipped_sheets.append(sheet_name)
            continue

        df['Agency Name'] = df['Agency Name'].astype(str)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        debug_agencies.update(df['Agency Name'].unique())

        df_filtered = df[
            df['Agency Name'].apply(match_agency) &
            (df['Date'] >= start_date) & 
            (df['Date'] <= end_date)
        ].copy()

        normalize_column(df_filtered, 'Time', ['Time', 'Start Time', 'PK Time', 'Clock'])
        normalize_column(df_filtered, 'ID1', ['ID1', 'ID 1', 'UID 1', 'Identifier1'])
        normalize_column(df_filtered, 'ID2', ['ID2', 'ID 2', 'UID 2', 'Identifier2'])

        if host_name:
            df_filtered = df_filtered[
                df_filtered['ID1'].str.lower().str.contains(host_name) |
                df_filtered['ID2'].str.lower().str.contains(host_name)
            ]

        df_filtered['Date'] = df_filtered['Date'].dt.strftime('%Y-%m-%d')
        df_filtered['PK Type'] = sheet_name.strip().replace("  ", " ")

        final_cols = ['PK Type', 'Date', 'Time', 'Agency Name', 'ID1', 'ID2']
        combined_df.append(df_filtered[final_cols])

    result_df = pd.concat(combined_df, ignore_index=True) if combined_df else pd.DataFrame()
    suggestions = {}

    if suggest_on_empty and result_df.empty and debug_agencies:
        for input_name in agencies:
            match = suggest_names(input_name, list(debug_agencies))
            if match:
                suggestions[input_name] = match

    return result_df, skipped_sheets, suggestions

# 🧮 Streamlit UI
st.set_page_config(page_title="Multi-Agency PK Filter", layout="wide")
st.title("📊 Multi-Agency Event Filter + Profiler")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
agency_input = st.text_input("Enter Agency Names (comma-separated)", value="Alpha Agency")
host_name_input = st.text_input("Enter Host Name (optional)")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")
suggest_mode = st.checkbox("Suggest closest matches if none found", value=True)

if uploaded_file and agency_input and start_date and end_date:
    expected_cols = ["date", "agencyname", "id1", "id2", "pktime"]
    profiles = profile_excel_structure(uploaded_file, expected_cols)

    st.subheader("🧬 Sheet Profiler Results")
    for sheet_name, details in profiles.items():
        with st.expander(f"📄 {sheet_name}", expanded=False):
            st.write("🔤 Raw Columns:")
            st.code(details["Raw Columns"])
            st.write("🔣 Normalized Columns:")
            st.code(details["Normalized"])
            if details["Missing Expected"]:
                st.warning(f"⚠️ Missing: {', '.join(details['Missing Expected'])}")
            else:
                st.success("✅ All expected columns present")

    # Optional safety: stop if no usable sheets
    all_missing = all(p["Missing Expected"] for p in profiles.values())
    if all_missing:
        st.error("🚫 All sheets missing required columns. Upload a different file.")
        st.stop()

    st.info("🔍 Running event filter...")
    filtered_df, skipped_sheets, suggestions = enhanced_process_excel(
        uploaded_file,
        pd.to_datetime(start_date),
        pd.to_datetime(end_date),
        agency_input,
        host_name_input,
        suggest_on_empty=suggest_mode
    )

    if not filtered_df.empty:
        pk_type_options = sorted(filtered_df['PK Type'].dropna().unique())
        selected_pk = st.multiselect("Filter by PK Type", pk_type_options, default=pk_type_options)

        time_filter = st.text_input("Filter by Time (optional)")
        id1_filter = st.text_input("Filter by ID1 (optional)")
        id2_filter = st.text_input("Filter by ID2 (optional)")

        if selected_pk:
            filtered_df = filtered_df[filtered_df['PK Type'].isin(selected_pk)]
        if time_filter:
            filtered_df = filtered_df[filtered_df['Time'].str.contains(time_filter, case=False, na=False)]
        if id1_filter:
            filtered_df = filtered_df[filtered_df['ID1'].str.contains(id1_filter, case=False, na=False)]
        if id2_filter:
            filtered_df = filtered_df[filtered_df['ID2'].str.contains(id2_filter, case=False, na=False)]

        st.success(f"✅ {len(filtered_df)} events matched")
        st.dataframe(filtered_df)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, sheet_name='Filtered PK Events', index=False)
        output.seek(0)

        st.download_button("📥 Download Results", data=output, file_name="filtered_pk_events.xlsx")

        if skipped_sheets:
            with st.expander("🛠 Skipped Sheets"):
                for sheet in skipped_sheets:
                    st.markdown(f"- `{sheet}`")

    else:
        st.warning("⚠️ No matches found.")
        if suggestions:
            for name, matches in suggestions.items():
                st.info(f"🤔 Closest for `{name}`: {', '.join(matches)}")
