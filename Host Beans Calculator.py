import streamlit as st
import pandas as pd
import glob, os
import io

st.title("📊 Broadcaster Performance Dashboard")

# Path to OneDrive–synced folder (local path)
drive_path = r"C:\Users\markj\OneDrive\Desktop\Broadcaster Data/"
excel_files = glob.glob(os.path.join(drive_path, "*.xlsx"))

if excel_files:
    latest_file = max(excel_files, key=os.path.getctime)
    st.success(f"Loaded latest file: {os.path.basename(latest_file)}")

    try:
        df = pd.read_excel(latest_file)
        # Fix column name typo if needed
        if "Effetive hours" in df.columns:
            df.rename(columns={"Effetive hours": "Effective Hours"}, inplace=True)
        elif "Effective hours" in df.columns:
            df.rename(columns={"Effective hours": "Effective Hours"}, inplace=True)

        required_columns = [
            "Host ID", "Effective Hours", "salary beans", "Basic Salary of broadcaster"
        ]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error(f"Missing columns in Excel file: {', '.join(missing)}")
        else:
            df = df[df["Effective Hours"] > 0].copy()
            # Derived metrics
            df["Beans per Hour"] = df["salary beans"] / df["Effective Hours"]
            df["Remuneration Efficiency"] = df["Basic Salary of broadcaster"] / df["salary beans"]

            # Display table
            st.dataframe(df[[
                "Host ID", "Effective Hours", "salary beans",
                "Basic Salary of broadcaster", "Beans per Hour", "Remuneration Efficiency"
            ]])

            # Optional download
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)
            st.download_button("Download Processed Data", data=buffer,
                               file_name="broadcaster_summary.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
else:
    st.warning("No Excel files found in your OneDrive folder.")