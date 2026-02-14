import pandas as pd

file_path = "Bill.csv"

# Load CSV
df = pd.read_csv(file_path)

required_columns = ["S.n", "Work code", "Contract Bill No", "Work", "Item", "Cost"]

print("Checking required columns...\n")

# 1️⃣ Check missing columns
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    print("Missing required columns:", missing_columns)
    exit()

print("All required columns present.\n")

# 2️⃣ Check empty required fields
for col in required_columns:
    missing_rows = df[df[col].isna() | (df[col].astype(str).str.strip() == "")]
    if not missing_rows.empty:
        print(f"Rows with missing values in column '{col}':")
        print(missing_rows[["S.n", col]])
        print()

# Convert Cost to numeric safely
df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce")

print("Checking Coordination Charges...\n")

tolerance = 10

# Get unique bill numbers
bill_numbers = df["Contract Bill No"].dropna().unique()

for bill in bill_numbers:

    bill_df = df[df["Contract Bill No"] == bill]

    # Identify coordination charge row
    coord_rows = bill_df[
        (bill_df["Work"].str.contains("coordination", case=False, na=False)) |
        (bill_df["Work code"].astype(str).str.startswith("C"))
    ]

    if coord_rows.empty:
        print(f"⚠ No coordination charge found for Bill {bill}")
        continue

    actual_coord_cost = coord_rows["Cost"].sum()

    # Exclude Supervisor, Miscellaneous, Coordination rows
    base_df = bill_df[
        ~bill_df["Work"].str.contains("Supervisor", case=False, na=False) &
        ~bill_df["Work"].str.contains("Misc", case=False, na=False) &
        ~bill_df["Work"].str.contains("coordination", case=False, na=False) &
        ~bill_df["Work code"].astype(str).str.startswith("C")
    ]

    base_sum = base_df["Cost"].sum()

    expected_coord = base_sum * 0.15

    difference = abs(expected_coord - actual_coord_cost)

    print(f"Bill {bill}:")
    print(f"Base Amount = {base_sum:.2f}")
    print(f"Expected 15% = {expected_coord:.2f}")
    print(f"Actual Coordination = {actual_coord_cost:.2f}")
    print(f"Difference = {difference:.2f}")

    if difference <= tolerance:
        print("✅ Coordination charge is correct within tolerance.\n")
    else:
        print("❌ Coordination charge mismatch!\n")
