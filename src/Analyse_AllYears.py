import pandas as pd
import glob as gl
import os 

all_df=[]
for year in range(2011,2018):
 df = pd.read_csv("data_raw/2017.csv", header=[0,1])


 df = df.dropna() # drops the empty rows to make it easier to read the data.

 
 df = df.drop(columns=[('Unnamed: 3_level_0', 'Note')]) # we are also droppign the note column because it serves no purpose. 

 df.columns = ['_'.join(col).strip() for col in df.columns]


 df.columns = df.columns.str.replace('Unnamed: \d+_level_0_', '', regex=True)

# Clean up the "Entry + Exit" column name
 df.columns = df.columns.str.replace('Entry \+ Exit_', 'Total_', regex=True)

# Add Year column
#df['Year'] = 2017

# Remove "Total" rows if they exist
#df = df[df['Station'] != 'Total']

# Reorder columns to put Year after Borough
#cols = df.columns.tolist()
#year_col = cols.pop()  # Remove Year from the end
#cols.insert(2, year_col)  # Insert Year after Borough (position 2)
#df = df[cols]

# Display results
#print("\nCleaned DataFrame:")

print(f"\nTotal rows: {len(df)}")
#print(f"\nColumn names: {list(df.columns)}")

print(df)
