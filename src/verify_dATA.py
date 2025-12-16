import pandas as pd

try:
    # Load your new master file
    df = pd.read_csv("all_years_combined.csv")
    
    print("--- DATA VERIFICATION ---")
    print(f"Total Rows: {len(df)}")
    
    # Check how many rows we have for EACH year
    # This proves you combined them, didn't just overwrite them
    print("\nRows per Year:")
    print(df['Year'].value_counts().sort_index())
    
    # Check for that "Total" row bug
    print("\nDo we have any 'Total' rows sneaking in?")
    if len(df[df['Station'] == 'Total']) > 0:
        print("YES! We need to fix the script to drop them.")
    else:
        print("NO! The data is clean.")

except FileNotFoundError:
    print("Error: Could not find 'all_years_combined.csv'. Did the previous script finish?")