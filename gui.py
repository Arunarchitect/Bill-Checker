"""
Bill Validation GUI Application
Handles the user interface and display – combines check icons and human‑friendly details.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import os
from validator import BillValidator

class BillValidationGUI:
    """Main GUI class for the Bill Validation Tool"""

    def __init__(self, root):
        self.root = root
        self.root.title("Bill Validation Tool")
        self.root.geometry("950x900")   # <-- fixed geometry
        ...

        # Default file names (expected to be in the same folder as the script)
        self.bill_file_path = tk.StringVar(value="Bill.csv")
        self.exclude_file_path = tk.StringVar(value="Exclude.csv")
        self.allowed_file_path = tk.StringVar(value="Valuecheck.csv")  # now mandatory
        self.workcode_file_path = tk.StringVar(value="Workcode.csv")   # optional reference
        self.coordination_percent = tk.StringVar(value="15")

        self.setup_ui()
        # Show instructions on startup
        self.refresh_output()

    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="Bill Validation Tool",
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # File selection frames
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=5, fill="x", padx=20)

        # Bill CSV
        bill_label = tk.Label(file_frame, text="Bill CSV File:", font=("Arial", 10))
        bill_label.grid(row=0, column=0, sticky="w", pady=5)
        bill_entry = tk.Entry(file_frame, textvariable=self.bill_file_path,
                              font=("Arial", 10), width=60)
        bill_entry.grid(row=0, column=1, padx=5, pady=5)
        bill_browse = tk.Button(file_frame, text="Browse...",
                                command=self.browse_bill_file)
        bill_browse.grid(row=0, column=2, padx=5, pady=5)

        # Exclude patterns
        exclude_label = tk.Label(file_frame, text="Exclude Patterns File:", font=("Arial", 10))
        exclude_label.grid(row=1, column=0, sticky="w", pady=5)
        exclude_entry = tk.Entry(file_frame, textvariable=self.exclude_file_path,
                                 font=("Arial", 10), width=60)
        exclude_entry.grid(row=1, column=1, padx=5, pady=5)
        exclude_browse = tk.Button(file_frame, text="Browse...",
                                   command=self.browse_exclude_file)
        exclude_browse.grid(row=1, column=2, padx=5, pady=5)

        # Allowed values (mandatory)
        allowed_label = tk.Label(file_frame, text="Allowed Values File:", font=("Arial", 10))
        allowed_label.grid(row=2, column=0, sticky="w", pady=5)
        allowed_entry = tk.Entry(file_frame, textvariable=self.allowed_file_path,
                                 font=("Arial", 10), width=60)
        allowed_entry.grid(row=2, column=1, padx=5, pady=5)
        allowed_browse = tk.Button(file_frame, text="Browse...",
                                   command=self.browse_allowed_file)
        allowed_browse.grid(row=2, column=2, padx=5, pady=5)

        # Work code reference file (optional)
        workcode_label = tk.Label(file_frame, text="Work Code Reference File:", font=("Arial", 10))
        workcode_label.grid(row=3, column=0, sticky="w", pady=5)
        workcode_entry = tk.Entry(file_frame, textvariable=self.workcode_file_path,
                                   font=("Arial", 10), width=60)
        workcode_entry.grid(row=3, column=1, padx=5, pady=5)
        workcode_browse = tk.Button(file_frame, text="Browse...",
                                    command=self.browse_workcode_file)
        workcode_browse.grid(row=3, column=2, padx=5, pady=5)

        # Percentage
        percent_frame = tk.Frame(self.root)
        percent_frame.pack(pady=5, fill="x", padx=20)
        percent_label = tk.Label(percent_frame, text="Coordination Percentage (%):", font=("Arial", 10))
        percent_label.grid(row=0, column=0, sticky="w", pady=5)
        percent_entry = tk.Entry(percent_frame, textvariable=self.coordination_percent,
                                 font=("Arial", 10), width=10)
        percent_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        hint_label = tk.Label(percent_frame, text="(e.g., 15 for 15%)", font=("Arial", 9), fg="gray")
        hint_label.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        self.run_button = tk.Button(button_frame, text="Run Check",
                                    font=("Arial", 12), width=15,
                                    command=self.run_check)
        self.run_button.grid(row=0, column=0, padx=10)
        self.refresh_button = tk.Button(button_frame, text="Refresh",
                                       font=("Arial", 12), width=15,
                                       command=self.refresh_output)
        self.refresh_button.grid(row=0, column=1, padx=10)

        # Progress
        self.progress_label = tk.Label(self.root, text="", font=("Arial", 10))
        self.progress_label.pack(pady=5)

        # Output
        self.output_box = scrolledtext.ScrolledText(self.root, wrap=tk.WORD,
                                                    width=110, height=30)
        self.output_box.pack(padx=10, pady=10, fill="both", expand=True)

        # Configure tag for red text
        self.output_box.tag_configure("red", foreground="red")

    def browse_bill_file(self):
        filename = filedialog.askopenfilename(
            title="Select Bill CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.bill_file_path.set(filename)

    def browse_exclude_file(self):
        filename = filedialog.askopenfilename(
            title="Select Exclude Patterns CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.exclude_file_path.set(filename)

    def browse_allowed_file(self):
        filename = filedialog.askopenfilename(
            title="Select Allowed Values CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.allowed_file_path.set(filename)

    def browse_workcode_file(self):
        filename = filedialog.askopenfilename(
            title="Select Work Code Reference CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.workcode_file_path.set(filename)

    def update_progress(self, current, total, bill_number):
        self.progress_label.config(
            text=f"Processing bill {current} of {total}: Bill {bill_number}"
        )
        self.root.update()

    def format_output(self, validation_result, percent_used):
        """Format validation results with check icons and detailed failure explanations."""
        self.output_box.delete(1.0, tk.END)

        # Global column check
        if not validation_result["global_columns_ok"]:
            self.output_box.insert(tk.END,
                "❌ MISSING COLUMNS\n" +
                "="*60 + "\n" +
                f"The following required columns are missing from the bill file:\n" +
                f"   {', '.join(validation_result['missing_columns'])}\n\n")
            return  # can't proceed if columns missing

        self.output_box.insert(tk.END,
            "✅ COLUMN CHECK PASSED\n" +
            "="*60 + "\n" +
            "All required columns are present in the bill file.\n\n")

        # Exclusion patterns
        exclude_item = validation_result["exclude_item_patterns"]
        exclude_work = validation_result["exclude_workcode_patterns"]
        if exclude_item or exclude_work:
            self.output_box.insert(tk.END, "📋 EXCLUSION PATTERNS\n")
            self.output_box.insert(tk.END, "-"*40 + "\n")
            if exclude_item:
                self.output_box.insert(tk.END, f"   Items excluded from base amount: {', '.join(exclude_item)}\n")
            if exclude_work:
                self.output_box.insert(tk.END, f"   Work codes excluded: {', '.join(exclude_work)}\n")
            self.output_box.insert(tk.END, "\n")

        # Allowed values
        allowed_dict = validation_result["allowed_dict"]
        if allowed_dict:
            self.output_box.insert(tk.END, "📋 ALLOWED VALUES PER COLUMN\n")
            self.output_box.insert(tk.END, "-"*40 + "\n")
            for col, values in sorted(allowed_dict.items()):
                # Format nicely: show 'any' or 'blank' prominently
                if 'any' in values and len(values) == 1:
                    desc = "any value allowed"
                elif 'blank' in values and len(values) == 1:
                    desc = "empty cells allowed"
                else:
                    # Remove 'any' and 'blank' from display if they exist alongside other values
                    display_vals = [v for v in values if v not in ('any','blank')]
                    desc = f"must be one of: {', '.join(sorted(display_vals))}"
                    if 'blank' in values:
                        desc += " (empty cells also allowed)"
                    if 'any' in values:
                        desc += " (any non‑empty value allowed)"
                self.output_box.insert(tk.END, f"   {col}: {desc}\n")
            self.output_box.insert(tk.END, "\n")

        # --- Work code reference file issues (if any) ---
        work_issues = validation_result.get('work_code_issues')
        if work_issues:
            # Insert header in red
            self.output_box.insert(tk.END, "⚠️  WORK CODE REFERENCE FILE ISSUES\n", "red")
            self.output_box.insert(tk.END, "-"*60 + "\n", "red")
            details_red = ""

            if work_issues.get('missing_code_rows'):
                rows = ', '.join(str(r) for r in work_issues['missing_code_rows'])
                details_red += f"   • Missing work code at row(s): {rows}\n"

            if work_issues.get('missing_name_rows'):
                rows = ', '.join(str(r) for r in work_issues['missing_name_rows'])
                details_red += f"   • Missing work name at row(s): {rows}\n"

            if work_issues.get('duplicate_codes'):
                details_red += "   • Duplicate work codes:\n"
                for code, rows in work_issues['duplicate_codes'].items():
                    rows_str = ', '.join(str(r) for r in rows)
                    details_red += f"       {code} at rows: {rows_str}\n"

            if work_issues.get('duplicate_names'):
                details_red += "   • Duplicate work names:\n"
                for name, rows in work_issues['duplicate_names'].items():
                    rows_str = ', '.join(str(r) for r in rows)
                    details_red += f"       {name} at rows: {rows_str}\n"

            if work_issues.get('duplicate_pairs'):
                details_red += "   • Duplicate (Work code, Work) pairs:\n"
                for pair_str, rows in work_issues['duplicate_pairs'].items():
                    rows_str = ', '.join(str(r) for r in rows)
                    details_red += f"       {pair_str} at rows: {rows_str}\n"

            self.output_box.insert(tk.END, details_red, "red")
            self.output_box.insert(tk.END, "\n")

        # Validation rules summary – plain language
        self.output_box.insert(tk.END, "📋 VALIDATION RULES\n")
        self.output_box.insert(tk.END, "-"*40 + "\n")
        rules = [
            "• All required columns must exist.",
            "• No empty cells in required columns (unless explicitly allowed).",
            f"• Coordination charge must be exactly {percent_used}% of the base amount (within ±{validation_result.get('tolerance',10)}).",
            "• Values in certain columns must be from a predefined list.",
            "• Cost, Rate per unit, and Quantity must contain only numbers."
        ]
        if validation_result.get('work_pairs_checked', False):
            rules.append("• Every (Work code, Work name) pair must match the reference file, and neither field may be empty.")
        else:
            rules.append("• Work code and Work name must not be empty (pair validation skipped because no reference file provided).")
        for rule in rules:
            self.output_box.insert(tk.END, f"  {rule}\n")
        self.output_box.insert(tk.END, "\n")

        total_bills = validation_result['total_bills']
        self.output_box.insert(tk.END,
            f"🔍 ANALYZING {total_bills} BILL{'S' if total_bills!=1 else ''} "
            f"(coordination = {percent_used}%)\n\n")

        passed_bills = []
        failed_bills = []

        # Human‑readable check names
        check_names = {
            'columns_present': 'Required columns exist',
            'no_missing_values': 'No empty cells in required columns',
            'allowed_values': 'Values from allowed list',
            'numeric_values': 'Numeric columns contain only numbers',
            'work_pairs_valid': 'Work code/name pairs are valid',
            'coordination_correct': 'Coordination charge correct'
        }

        # Process each bill
        for bill, result in validation_result["results"].items():
            checks = result["checks"]
            bill_passed = all(checks.values())
            details = result["details"]

            if bill_passed:
                passed_bills.append(bill)
            else:
                failed_bills.append(bill)

            # Bill header with clear pass/fail icon
            status = "✅ PASS" if bill_passed else "❌ FAIL"
            self.output_box.insert(tk.END, f"{status}  Bill {bill}\n")
            self.output_box.insert(tk.END, "  " + "-"*50 + "\n")

            # Table of checks with icons
            check_order = ['columns_present', 'no_missing_values', 'allowed_values',
                           'numeric_values', 'work_pairs_valid', 'coordination_correct']
            for check_name in check_order:
                # Skip work_pairs_valid if not checked (but we always check missing values)
                if check_name == 'work_pairs_valid' and not validation_result.get('work_pairs_checked', False):
                    # Still need to show missing value status if any
                    passed = checks.get(check_name, False)
                    icon = "✅" if passed else "❌"
                    display_name = "Work code/name (missing values only)"
                    self.output_box.insert(tk.END, f"  {icon} {display_name}\n")
                else:
                    passed = checks.get(check_name, False)
                    icon = "✅" if passed else "❌"
                    display_name = check_names.get(check_name, check_name)
                    self.output_box.insert(tk.END, f"  {icon} {display_name}\n")

            # Detailed explanations for failures – all in red
            failure_details = []

            # Missing values (from required columns)
            missing = details.get("missing_values", {})
            if missing:
                for col, rows in missing.items():
                    rows_str = ', '.join(str(r) for r in rows)
                    failure_details.append(f"  • Column '{col}' has empty cells at row(s): {rows_str}")

            # Allowed values violations
            allowed_violations = details.get("allowed_violations", {})
            if allowed_violations:
                for col, vals in allowed_violations.items():
                    vals_str = ', '.join(f"'{v}'" for v in vals)
                    failure_details.append(f"  • Column '{col}' contains invalid values: {vals_str}")

            # Numeric violations
            numeric_violations = details.get("numeric_violations", {})
            if numeric_violations:
                for col, rows in numeric_violations.items():
                    rows_str = ', '.join(str(r) for r in rows)
                    failure_details.append(f"  • Column '{col}' has non‑numeric entries at row(s): {rows_str}")

            # Work code/name issues
            work_violations = details.get("work_pair_violations", {})
            if work_violations:
                if 'missing_columns' in work_violations:
                    cols = ', '.join(work_violations['missing_columns'])
                    failure_details.append(f"  • Missing required columns: {cols}")
                else:
                    missing_code = work_violations.get('missing_code', [])
                    missing_name = work_violations.get('missing_name', [])
                    invalid_pairs = work_violations.get('invalid_pairs', {})

                    if missing_code:
                        rows_str = ', '.join(str(r) for r in missing_code)
                        failure_details.append(f"  • Missing work code at row(s): {rows_str}")
                    if missing_name:
                        rows_str = ', '.join(str(r) for r in missing_name)
                        failure_details.append(f"  • Missing work name at row(s): {rows_str}")
                    for pair_key, rows in invalid_pairs.items():
                        code, name = pair_key.split('|', 1)
                        rows_str = ', '.join(str(r) for r in rows)
                        failure_details.append(f"  • Invalid pair (code: '{code}', work: '{name}') at row(s): {rows_str}")

            # Coordination issues
            coord = details.get("coordination", {})
            if not checks.get('coordination_correct', True):
                if not coord.get("has_coordination", False):
                    failure_details.append(f"  • No coordination charge row found.")
                else:
                    failure_details.append(f"  • Expected: ₹{coord['expected']:.2f}, Actual: ₹{coord['actual_coord']:.2f}, Difference: ₹{coord['diff']:.2f}")
                    if coord.get("excluded_items"):
                        failure_details.append(f"  • Excluded from base amount:")
                        for item in coord["excluded_items"]:
                            failure_details.append(f"      - {item['Item']} (Code: {item['Work code']}): ₹{item['Cost']:.2f}")

            if failure_details:
                # Insert all failure details as one block with red tag
                self.output_box.insert(tk.END, "\n" + "\n".join(failure_details) + "\n", "red")

            self.output_box.insert(tk.END, "\n")

        # Final summary
        self.output_box.insert(tk.END, "="*60 + "\n")
        self.output_box.insert(tk.END, "📊 FINAL SUMMARY\n")
        self.output_box.insert(tk.END, "="*60 + "\n")
        self.output_box.insert(tk.END, f"Total bills processed: {total_bills}\n")
        if passed_bills:
            self.output_box.insert(tk.END,
                f"✅ PASSED: {len(passed_bills)} bill{'s' if len(passed_bills)!=1 else ''} "
                f"- {', '.join(str(b) for b in passed_bills)}\n")
        else:
            self.output_box.insert(tk.END, "✅ PASSED: 0 bills\n")
        if failed_bills:
            self.output_box.insert(tk.END,
                f"❌ FAILED: {len(failed_bills)} bill{'s' if len(failed_bills)!=1 else ''} "
                f"- {', '.join(str(b) for b in failed_bills)}\n")
        else:
            self.output_box.insert(tk.END, "❌ FAILED: 0 bills\n")

        self.output_box.insert(tk.END, f"\n{len(passed_bills)} out of {total_bills} bills passed.\n")

        self.progress_label.config(text="")

    def run_check(self):
        bill_path = self.bill_file_path.get().strip()
        exclude_path = self.exclude_file_path.get().strip()
        allowed_path = self.allowed_file_path.get().strip()
        workcode_path = self.workcode_file_path.get().strip()
        percent_str = self.coordination_percent.get().strip()

        # Validate percentage
        try:
            percent = float(percent_str)
            if percent <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "Please enter a valid positive number for the coordination percentage.")
            return

        # Validate bill file
        if not bill_path:
            messagebox.showerror("Error", "Please select a Bill CSV file.")
            return
        if not os.path.exists(bill_path):
            messagebox.showerror("Error", f"Bill file not found:\n{bill_path}")
            return

        # Validate exclude patterns file (optional but warn if missing)
        if exclude_path and not os.path.exists(exclude_path):
            if not messagebox.askyesno("File Not Found",
                f"Exclude patterns file not found:\n{exclude_path}\n\nContinue without exclusion patterns?"):
                return

        # Validate allowed values file (mandatory)
        if not allowed_path:
            messagebox.showerror("Error", "Please select an Allowed Values CSV file (mandatory).")
            return
        if not os.path.exists(allowed_path):
            messagebox.showerror("Error", f"Allowed values file not found:\n{allowed_path}")
            return

        # Validate work code reference file if provided
        if workcode_path and not os.path.exists(workcode_path):
            if not messagebox.askyesno("File Not Found",
                f"Work code reference file not found:\n{workcode_path}\n\nContinue without work code validation?"):
                return
            else:
                workcode_path = None   # treat as not provided

        try:
            validator = BillValidator(
                file_path=bill_path,
                exclude_path=exclude_path,
                allowed_values_path=allowed_path,
                coordination_percentage=percent,
                work_code_path=workcode_path if workcode_path else None
            )
            result = validator.load_and_validate(progress_callback=self.update_progress)
            self.format_output(result, percent)
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed:\n{e}")

    def refresh_output(self):
        """Clear the output and show detailed instructions."""
        self.output_box.delete(1.0, tk.END)
        instructions = """\
📋 **WELCOME TO THE BILL VALIDATION TOOL**

This tool checks your bill CSV file against a set of validation rules.  
Follow the steps below to prepare your data and run the check.

---

## STEP 1: UNDERSTAND THE TEMPLATE FILES

Four CSV files are used (default names are shown in the entry fields above).  
**You must keep the column headings exactly as they appear in these templates.**  
You can modify the data rows (copy/paste your own data) but **do not change the header row**.

| File              | Purpose                                                                                   | Required Columns (examples)                          |
|-------------------|-------------------------------------------------------------------------------------------|------------------------------------------------------|
| `Bill.csv`        | The actual bill data you want to validate.                                                | Contract Bill No, Item, Work code, Work, Cost, ...   |
| `Exclude.csv`     | Patterns to exclude from the coordination base amount.                                    | type, pattern   (e.g. type=Item, pattern=Supervisor) |
| `Valuecheck.csv`  | Defines which values are allowed in each column (mandatory).                              | One column per required field (e.g. Contract Bill No)|
| `Workcode.csv`    | Reference list of valid (Work code, Work) pairs (optional, but recommended).             | Work code, Work, Start, End                           |

---

## STEP 2: PREPARE YOUR DATA

1. **Open each template file** in a spreadsheet editor (Excel, LibreOffice, etc.) or a text editor.
2. **Keep the first row (headers) untouched**.
3. **Paste your data starting from row 2**.  
   - For `Bill.csv`, paste your bill rows.
   - For `Exclude.csv`, add rows with `type` (either "Item" or "Work code") and the pattern to exclude.
   - For `Valuecheck.csv`, list **all allowed values** for each column.  
     * Use `any` if any non‑empty value is allowed.  
     * Use `blank` if empty cells are allowed.  
     * Otherwise, list every permissible value (one per row).
   - For `Workcode.csv`, list all valid work‑code / work‑name pairs (optional).
4. **Save the files** as CSV (comma‑separated values). Keep them in the same folder as this program, or use the Browse buttons to select them.

---

## STEP 3: SET THE COORDINATION PERCENTAGE

Enter the percentage used for coordination charge (e.g., 15 for 15%).  
The tool will check that the coordination charge row equals exactly this percentage of the base amount (after applying exclusions).

---

## STEP 4: RUN THE VALIDATION

Click the **Run Check** button. The tool will:

- Verify that all required columns exist.
- Check for empty cells (unless `blank` is allowed).
- Validate that values belong to the allowed lists.
- Ensure numeric columns contain only numbers.
- If a work‑code reference file is provided, verify every (Work code, Work) pair.
- Calculate the expected coordination charge and compare it with the actual value.

---

## STEP 5: INTERPRET THE RESULTS

- **Green checkmarks (✅)** indicate passed checks.
- **Red crosses (❌)** indicate failures.
- Detailed failure explanations are shown in **red text** below each bill.
- A final summary shows how many bills passed/failed.

If you need to run another check, click **Refresh** to clear the output and return to these instructions.

---

**Need help?** Make sure your CSV files use the correct column headers and that the data is properly formatted.  
If you see unexpected errors, check the console for more details.
"""
        self.output_box.insert(tk.END, instructions)
        self.progress_label.config(text="")


def main():
    root = tk.Tk()
    app = BillValidationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()