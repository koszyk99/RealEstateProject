import pandas as pd
import os

def convert_csv_to_excel(csv_filename: str, excel_filename: str):
    print("--- STARTING EXCEL CONVERSION (Pandas) ---")

    if not os.path.exists(csv_filename):
        print(f"[ERROR] Source file {csv_filename} not found.")
        return

    # LOAD DATA WITH PANDAS
    print(f"[PANDAS] Loading data from {csv_filename}...")
    df = pd.read_csv(csv_filename)
    initial_rows = len(df)

    # CLEAN DATA
    print("[PANDAS] Cleaning duplicates and formating data types...")

    # Remove duplicate offers based on URL
    df.drop_duplicates(subset=['URL'], keep='first', inplace=True)
    deuplicates_removed = initial_rows - len(df)
    if deuplicates_removed > 0:
        print(f"[PANDAS] Cleaned {deuplicates_removed} duplicate records.")

    # Convert prices to proper numbers so Excel can sum and average them
    df['Total Price (PLN)'] = pd.to_numeric(df['Total Price (PLN)'], errors='coerce')
    df['Price per SQM (PLN)'] = pd.to_numeric(df['Price per SQM (PLN)'], errors='coerce')
    df['Area (SQM)'] = pd.to_numeric(df['Area (SQM)'], errors='coerce')

    # Fill empty text cells with clear indicators
    df['Rooms'] = df['Rooms'].fillna('N/A').astype(str).str.strip()

    # EXPORT TO EXCEL
    print(f"[EXCEL] Writing clean dataset to {excel_filename}...")
    try:
        df.to_excel(excel_filename, index=False, sheet_name="Warsaw Properties")
        print(f"\n[SUCCESS] Your Excel file is ready! Saved {len(df)} properties to: ./{excel_filename}")

    except Exception as error:
        print(f"[ERROR] Failed to save Excel file: {error}")

if __name__ == "__main__":
    SOURCE_CSV = "warsaw_detailed_properties.csv"
    TARGET_EXCEL = "warsaw_market_analsys.xlsx"

    convert_csv_to_excel(SOURCE_CSV, TARGET_EXCEL)
