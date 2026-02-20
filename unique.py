import pandas as pd

# Read the CSV file
df = pd.read_csv("test.csv")

# Get unique values from 'unit' column
unique_units = df["unit"].drop_duplicates()

# Save to new CSV
unique_units.to_csv("unique_units.csv", index=False)

print("Done. Unique values saved to unique_units.csv")