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
        self.root.geometry("950x900")

        # Default file names (expected to be in the same folder as the script)
        self.bill_file_path = tk.StringVar(value="Bill.csv")
        self.exclude_file_path = tk.StringVar(value="Exclude.csv")
        self.allowed_file_path = tk.StringVar(value="Valuecheck.csv")
        self.workcode_file_path = tk.StringVar(value="Workcode.csv")
        self.coordination_percent = tk.StringVar(value="15")

        self.setup_ui()
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

        # Configure tags
        self.output_box.tag_configure("red", foreground="red")
        self.output_box.tag_configure("orange", foreground="darkorange")
        self.output_box.tag_configure("warning", foreground="darkorange")

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

        if not validation_result["global_columns_ok"]:
            self.output_box.insert(tk.END,
                "❌ MISSING COLUMNS\n" +
                "="*60 + "\n" +
                f"The following required columns are missing from the bill file:\n" +
                f"   {', '.join(validation_result['missing_columns'])}\n\n")
            return

        self.output_box.insert(tk.END,
            "✅ COLUMN CHECK PASSED\n" +
            "="*60 + "\n" +
            "All required columns are present in the bill file.\n\n")

        # Exclusion conditions
        exclude_conds = validation_result.get("exclude_conditions", [])
        if exclude_conds:
            self.output_box.insert(tk.END, "📋 EXCLUSION CONDITIONS\n")
            self.output_box.insert(tk.END, "-"*40 + "\n")
            for cond in exclude_conds:
                cond_str = " AND ".join(f"{col} = '{val}'" for col, val in cond.items())
                self.output_box.insert(tk.END, f"   • {cond_str}\n")
            self.output_box.insert(tk.END, "\n")

        # Allowed values
        allowed_dict = validation_result["allowed_dict"]
        if allowed_dict:
            self.output_box.insert(tk.END, "📋 ALLOWED VALUES PER COLUMN\n")
            self.output_box.insert(tk.END, "-"*40 + "\n")
            for col, values in sorted(allowed_dict.items()):
                if 'any' in values and len(values) == 1:
                    desc = "any value allowed"
                elif 'blank' in values and len(values) == 1:
                    desc = "empty cells allowed"
                else:
                    display_vals = [v for v in values if v not in ('any','blank')]
                    desc = f"must be one of: {', '.join(sorted(display_vals))}"
                    if 'blank' in values:
                        desc += " (empty cells also allowed)"
                    if 'any' in values:
                        desc += " (any non‑empty value allowed)"
                self.output_box.insert(tk.END, f"   {col}: {desc}\n")
            self.output_box.insert(tk.END, "\n")

        # Work code reference file issues
        # Work code reference file issues
        work_issues = validation_result.get('work_code_issues')
        if work_issues:
            self.output_box.insert(tk.END, "⚠️  WORK CODE REFERENCE FILE ISSUES\n", "red")
            self.output_box.insert(tk.END, "-"*60 + "\n", "red")
            details_red = ""
            if work_issues.get('missing_code_rows'):
                rows = ', '.join(str(r) for r in work_issues['missing_code_rows'])
                details_red += f"   • Missing work code at row(s): {rows}\n"
            if work_issues.get('missing_name_rows'):
                rows = ', '.join(str(r) for r in work_issues['missing_name_rows'])
                details_red += f"   • Missing work name at row(s): {rows}\n"
            if work_issues.get('name_with_multiple_codes'):
                details_red += "   • Work name appears with multiple different work codes:\n"
                for name, data in work_issues['name_with_multiple_codes'].items():
                    codes_str = ', '.join(data['codes'])
                    rows_str = ', '.join(str(r) for r in data['rows'])
                    details_red += f"       '{name}' with codes {codes_str} at rows: {rows_str}\n"
            self.output_box.insert(tk.END, details_red, "red")
            self.output_box.insert(tk.END, "\n")


        # Validation rules summary
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

        # Human‑readable base names
        base_check_names = {
            'columns_present': 'Required columns exist',
            'no_missing_values': 'No empty cells in required columns',
            'allowed_values': 'Values from allowed list',
            'numeric_values': 'Numeric columns contain only numbers',
            'work_pairs_valid': 'Work code/name pairs are valid',
        }

        for bill, result in validation_result["results"].items():
            checks = result["checks"]
            details = result["details"]
            coord_info = details.get("coordination", {})

            # Determine bill pass/fail (coordination check always passes if no coordination row)
            all_checks_pass = all(checks.values())  # coordination_correct is True when no coordination

            if all_checks_pass:
                passed_bills.append(bill)
            else:
                failed_bills.append(bill)

            status = "✅ PASS" if all_checks_pass else "❌ FAIL"
            self.output_box.insert(tk.END, f"{status}  Bill {bill}\n")
            self.output_box.insert(tk.END, "  " + "-"*50 + "\n")

            # ---- List all checks with appropriate symbols and text ----
            # Columns present
            icon = "✅" if checks.get('columns_present') else "❌"
            self.output_box.insert(tk.END, f"  {icon} {base_check_names['columns_present']}\n")

            # No missing values
            icon = "✅" if checks.get('no_missing_values') else "❌"
            self.output_box.insert(tk.END, f"  {icon} {base_check_names['no_missing_values']}\n")

            # Allowed values
            icon = "✅" if checks.get('allowed_values') else "❌"
            self.output_box.insert(tk.END, f"  {icon} {base_check_names['allowed_values']}\n")

            # Numeric values
            icon = "✅" if checks.get('numeric_values') else "❌"
            self.output_box.insert(tk.END, f"  {icon} {base_check_names['numeric_values']}\n")

            # Work pairs valid (or missing values only)
            if validation_result.get('work_pairs_checked', False):
                icon = "✅" if checks.get('work_pairs_valid') else "❌"
                self.output_box.insert(tk.END, f"  {icon} {base_check_names['work_pairs_valid']}\n")
            else:
                # No reference file: only check missing values, which is included in work_pairs_valid check
                icon = "✅" if checks.get('work_pairs_valid') else "❌"
                self.output_box.insert(tk.END, f"  {icon} Work code/name (missing values only)\n")

            # Coordination charge – special handling
            if coord_info.get('has_coordination', False):
                # There is a coordination row: show correct/incorrect
                passed = checks.get('coordination_correct', False)
                icon = "✅" if passed else "❌"
                text = "Coordination charge correct" if passed else "Coordination charge incorrect"
                self.output_box.insert(tk.END, f"  {icon} {text}\n")
            else:
                # No coordination row: show warning and pass
                self.output_box.insert(tk.END, "  ⚠️  No coordination charge (skipped)\n", "orange")

            # ---- Detailed coordination calculation (if exists) ----
            if coord_info.get('has_coordination', False):
                base = coord_info.get('base_amount', 0)
                expected = coord_info.get('expected', 0)
                actual = coord_info.get('actual_coord', 0)
                self.output_box.insert(tk.END, f"     Base amount (after exclusions): ₹{base:.2f}\n")
                self.output_box.insert(tk.END, f"     {percent_used}% of base = ₹{expected:.2f}\n")
                if checks.get('coordination_correct', True):
                    self.output_box.insert(tk.END, f"     Actual coordination: ₹{actual:.2f} (matches expected)\n")
                else:
                    diff = coord_info.get('diff', 0)
                    self.output_box.insert(tk.END, f"     Actual coordination: ₹{actual:.2f} (Difference: ₹{diff:.2f})\n", "red")
                if coord_info.get("excluded_items"):
                    self.output_box.insert(tk.END, f"     Excluded from base amount:\n")
                    for item in coord_info["excluded_items"]:
                        self.output_box.insert(tk.END, f"        - {item['Item']} (Code: {item['Work code']}): ₹{item['Cost']:.2f}\n")

            # ---- Detailed failure explanations (non‑coordination) ----
            failure_details = []

            # Missing values
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

            if failure_details:
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

        try:
            percent = float(percent_str)
            if percent <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "Please enter a valid positive number for the coordination percentage.")
            return

        if not bill_path:
            messagebox.showerror("Error", "Please select a Bill CSV file.")
            return
        if not os.path.exists(bill_path):
            messagebox.showerror("Error", f"Bill file not found:\n{bill_path}")
            return

        if exclude_path and not os.path.exists(exclude_path):
            if not messagebox.askyesno("File Not Found",
                f"Exclude patterns file not found:\n{exclude_path}\n\nContinue without exclusion patterns?"):
                return

        if not allowed_path:
            messagebox.showerror("Error", "Please select an Allowed Values CSV file (mandatory).")
            return
        if not os.path.exists(allowed_path):
            messagebox.showerror("Error", f"Allowed values file not found:\n{allowed_path}")
            return

        if workcode_path and not os.path.exists(workcode_path):
            if not messagebox.askyesno("File Not Found",
                f"Work code reference file not found:\n{workcode_path}\n\nContinue without work code validation?"):
                return
            else:
                workcode_path = None

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
| `Exclude.csv`     | **Exclusion conditions** – each row defines a set of column‑value pairs.                  | Any columns present in the bill; rows with **all** matching values are excluded from the coordination base amount. |
| `Valuecheck.csv`  | Defines which values are allowed in each column (mandatory).                              | One column per required field (e.g. Contract Bill No)|
| `Workcode.csv`    | Reference list of valid (Work code, Work) pairs (optional, but recommended).             | Work code, Work, Start, End                           |

---

## STEP 2: PREPARE YOUR DATA

1. **Open each template file** in a spreadsheet editor (Excel, LibreOffice, etc.) or a text editor.
2. **Keep the first row (headers) untouched**.
3. **Paste your data starting from row 2**.  
   - For `Bill.csv`, paste your bill rows.
   - For `Exclude.csv`, list **exclusion conditions**.  
     * Each row defines one condition. A bill row is excluded **only if it matches all the columns you fill in that row**.  
     * For example, a row with `Work code = S` excludes all rows with Work code 'S'.  
     * A row with `Work = Site` and `Item = Cement` excludes only rows where both Work is 'Site' **and** Item is 'Cement'.  
     * Empty cells are ignored (they do not form part of the condition).
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
- **Orange warning (⚠️)** indicates that a check was skipped (e.g., no coordination charge).
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