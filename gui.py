import tkinter as tk
from tkinter import scrolledtext, messagebox
import pandas as pd
import os

FILE_PATH = "Bill.csv"
EXCLUDE_PATH = "exclude_patterns.csv"
TOLERANCE = 10


def load_exclude_patterns():
    """Load exclusion patterns from CSV file"""
    exclude_item_patterns = []
    exclude_workcode_patterns = []
    
    # Check if file exists
    if not os.path.exists(EXCLUDE_PATH):
        print(f"Debug: {EXCLUDE_PATH} not found")
        return exclude_item_patterns, exclude_workcode_patterns
    
    try:
        print(f"Debug: Reading {EXCLUDE_PATH}")
        exclude_df = pd.read_csv(EXCLUDE_PATH)
        print(f"Debug: CSV columns: {list(exclude_df.columns)}")
        print(f"Debug: CSV data:\n{exclude_df}")
        
        # Get non-NaN values from Item column
        if 'Item' in exclude_df.columns:
            exclude_item_patterns = exclude_df['Item'].dropna().astype(str).tolist()
            print(f"Debug: Item patterns found: {exclude_item_patterns}")
        
        # Get non-NaN values from Work code column
        if 'Work code' in exclude_df.columns:
            exclude_workcode_patterns = exclude_df['Work code'].dropna().astype(str).tolist()
            print(f"Debug: Work code patterns found: {exclude_workcode_patterns}")
                
    except Exception as e:
        print(f"Debug: Error reading CSV: {e}")
        messagebox.showwarning("Warning", f"Could not read exclude_patterns.csv:\n{e}")
    
    return exclude_item_patterns, exclude_workcode_patterns


def is_coordination_row(item_text):
    """Check if a row is a coordination charge by looking in Item column"""
    return "coordination charge" in str(item_text).lower()


def should_exclude_row(item_text, work_code, item_patterns, workcode_patterns):
    """Check if a row should be excluded from base calculation based on Item column"""
    
    # Check Item column patterns (case-insensitive contains)
    for pattern in item_patterns:
        if pattern and pd.notna(pattern) and pattern.lower() in str(item_text).lower():
            print(f"Debug: Excluding '{item_text}' because it matches pattern '{pattern}'")
            return True
    
    # Check Work code column patterns
    for pattern in workcode_patterns:
        if not pattern or pd.isna(pattern):
            continue
            
        pattern_str = str(pattern)
        
        # Handle "starts with" pattern
        if pattern_str.lower().startswith("starts with "):
            prefix = pattern_str[12:].strip()  # Remove "starts with " prefix
            if str(work_code).startswith(prefix):
                print(f"Debug: Excluding work code '{work_code}' because it starts with '{prefix}'")
                return True
        # Handle exact match pattern
        elif pattern_str == str(work_code):
            print(f"Debug: Excluding work code '{work_code}' because it exactly matches '{pattern_str}'")
            return True
        # Handle contains pattern
        elif pattern_str and pattern_str.lower() in str(work_code).lower():
            print(f"Debug: Excluding work code '{work_code}' because it contains '{pattern_str}'")
            return True
    
    return False


def run_check():
    output_box.delete(1.0, tk.END)

    if not os.path.exists(FILE_PATH):
        messagebox.showerror("Error", "Bill.csv not found!")
        return

    try:
        df = pd.read_csv(FILE_PATH)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read CSV:\n{e}")
        return

    required_columns = ["S.n", "Work code", "Contract Bill No", "Work", "Item", "Cost"]

    # Check missing columns
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        output_box.insert(tk.END, f"❌ Missing Columns: {missing_columns}\n")
        return
    else:
        output_box.insert(tk.END, "✅ All required columns present.\n\n")

    # Load exclusion patterns from CSV
    exclude_item_patterns, exclude_workcode_patterns = load_exclude_patterns()
    
    # Show loaded exclusion patterns
    if exclude_item_patterns or exclude_workcode_patterns:
        output_box.insert(tk.END, "📋 Loaded exclusion patterns from CSV:\n")
        if exclude_item_patterns:
            output_box.insert(tk.END, f"   Item patterns (excluded from base): {exclude_item_patterns}\n")
        if exclude_workcode_patterns:
            output_box.insert(tk.END, f"   Work code patterns (excluded from base): {exclude_workcode_patterns}\n")
        output_box.insert(tk.END, "\n")
    else:
        output_box.insert(tk.END, "📋 No exclusion patterns found in CSV.\n")
        output_box.insert(tk.END, f"   Please ensure '{EXCLUDE_PATH}' exists with 'Item' and 'Work code' columns.\n\n")

    # Check empty required fields
    for col in required_columns:
        if col in df.columns:
            missing_rows = df[df[col].isna() | (df[col].astype(str).str.strip() == "")]
            if not missing_rows.empty:
                output_box.insert(tk.END, f"⚠ Missing values in column '{col}' at rows:\n")
                output_box.insert(tk.END, f"{list(missing_rows['S.n'])}\n\n")

    # Convert Cost to numeric, coerce errors to NaN
    df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce")

    output_box.insert(tk.END, "Checking Coordination Charges...\n\n")

    # Get unique bill numbers (excluding NaN and empty)
    bill_numbers = df["Contract Bill No"].dropna().unique()
    bill_numbers = [b for b in bill_numbers if str(b).strip()]

    for bill in bill_numbers:
        bill_df = df[df["Contract Bill No"] == bill].copy()
        
        # Find coordination charge rows (looking in Item column)
        coord_rows = bill_df[bill_df["Item"].astype(str).str.lower().str.contains("coordination charge", na=False)]
        
        if coord_rows.empty:
            output_box.insert(tk.END, f"⚠ No coordination charge found for Bill {bill}\n\n")
            continue

        # Sum all coordination charges for this bill
        actual_coord = coord_rows["Cost"].sum()

        # Calculate base amount (exclude items based on CSV patterns - checking against Item column)
        base_df = bill_df[~bill_df.apply(
            lambda row: should_exclude_row(
                row['Item'],  # Now checking Item column instead of Work
                row['Work code'], 
                exclude_item_patterns, 
                exclude_workcode_patterns
            ), 
            axis=1
        )]

        base_sum = base_df["Cost"].sum()
        expected = base_sum * 0.15
        diff = abs(expected - actual_coord)

        output_box.insert(tk.END, f"Bill {bill}\n")
        output_box.insert(tk.END, f"Total Bill Amount (all items) = {bill_df['Cost'].sum():.2f}\n")
        output_box.insert(tk.END, f"Base Amount (excluding items from CSV) = {base_sum:.2f}\n")
        output_box.insert(tk.END, f"Expected 15% = {expected:.2f}\n")
        output_box.insert(tk.END, f"Actual Coordination = {actual_coord:.2f}\n")
        output_box.insert(tk.END, f"Difference = {diff:.2f}\n")

        if diff <= TOLERANCE:
            output_box.insert(tk.END, "✅ Coordination charge correct.\n\n")
        else:
            output_box.insert(tk.END, "❌ Coordination charge mismatch!\n\n")
            
            # Show details of excluded items for debugging
            excluded_df = bill_df[bill_df.apply(
                lambda row: should_exclude_row(
                    row['Item'],  # Now checking Item column
                    row['Work code'], 
                    exclude_item_patterns, 
                    exclude_workcode_patterns
                ), 
                axis=1
            )]
            if not excluded_df.empty:
                output_box.insert(tk.END, "   Items excluded from base calculation (from CSV):\n")
                for _, row in excluded_df.iterrows():
                    output_box.insert(tk.END, f"     - {row['Item']} (Code: {row['Work code']}, Work: {row['Work']}): {row['Cost']:.2f}\n")
            else:
                output_box.insert(tk.END, "   No items were excluded - check if patterns match your data\n")
            output_box.insert(tk.END, "\n")


def refresh_output():
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, "🔄 Output cleared. Ready to run check again.\n")


# ---------------- GUI ----------------

root = tk.Tk()
root.title("Bill Validation Tool")
root.geometry("900x700")

title = tk.Label(root, text="Bill Validation Tool", font=("Arial", 16, "bold"))
title.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

run_button = tk.Button(button_frame, text="Run Check", font=("Arial", 12), width=15, command=run_check)
run_button.grid(row=0, column=0, padx=10)

refresh_button = tk.Button(button_frame, text="Refresh", font=("Arial", 12), width=15, command=refresh_output)
refresh_button.grid(row=0, column=1, padx=10)

output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=110, height=35)
output_box.pack(padx=10, pady=10, fill="both", expand=True)

root.mainloop()