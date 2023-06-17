import pandas as pd

# Read the Excel file into a pandas DataFrame
excel_file = pd.ExcelFile('Attachement -dummydataset.xlsx')

# Access all the sheet names in the Excel file
sheet_names = excel_file.sheet_names

# Create an empty list to store the DataFrames for each sheet
dfs = []

# Loop through each sheet name and read the data into separate DataFrames
for sheet_name in sheet_names:
    df = excel_file.parse(sheet_name)
    dfs.append(df)

# Concatenate all the DataFrames into a single DataFrame
combined_df = pd.concat(dfs, ignore_index=True)
combined_df = combined_df.drop('Unnamed: 8', axis=1)