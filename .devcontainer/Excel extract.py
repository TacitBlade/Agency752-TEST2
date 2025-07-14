
import pandas as pd

def process_excel_file(input_file_path, output_file_path):
    excel_data = pd.read_excel(input_file_path, sheet_name=None)
    filtered_data = {}

    for sheet_name, df in excel_data.items():
        if 'Agency Name' in df.columns:
            # Filter rows where 'Agency Name' contains 'Alpha Agency'
            filtered_df = df[df['Agency Name'].astype(str).str.contains('Alpha Agency', case=False, na=False)]
            if not filtered_df.empty:
                filtered_data[sheet_name] = filtered_df

    if filtered_data:
        with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
            for sheet_name, df in filtered_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        return True
    else:
        return False

if __name__ == '__main__':
    input_path = '/home/ubuntu/upload/July2025UKAgency&HostEvents.xlsx'
    output_path = '/home/ubuntu/filtered_agency_data.xlsx'

    if process_excel_file(input_path, output_path):
        print(f'Filtered data saved to {output_path}')
    else:
        print('No data found for "Alpha Agency" in the specified sheets.')