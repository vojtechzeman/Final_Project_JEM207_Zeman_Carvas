import pandas as pd

# Read CSV with semicolon delimiter and specified column names
df = pd.read_csv('data/processed/sale.csv', sep=';', encoding='utf-8')
df = pd.read_json("data/raw/deleted_sale.json")


# If you want to check the data was read correctly:
print(df.head())  # Shows first few rows
print(df.shape)   # Shows number of rows and columns