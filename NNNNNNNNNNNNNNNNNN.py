# import pandas as pd
# import numpy as np

# # Read the CSV file
# df = pd.read_csv('data/processed/sale_0.csv')

# # Add the new columns with NaN values
# new_columns = ['metadata', 'image', 'link']
# for column in new_columns:
#     df[column] = np.nan

# # Save the modified dataframe back to CSV
# df.to_csv('data/processed/sale_0.csv', index=False)

# print("New columns added successfully with NA values!")






import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('data/processed/sale_0.csv')

# Replace NA values with 0 in specific columns
columns_to_fix = ['metadata', 'image', 'link']
df[columns_to_fix] = df[columns_to_fix].fillna(0)

# Save the modified dataframe back to CSV
df.to_csv('data/processed/sale_0.csv', index=False)
print("NA values successfully replaced with zeros!")