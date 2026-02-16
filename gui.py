"""
Bill Validation GUI Application
Handles the user interface and display – enhanced for readability.
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
        self.root.geometry("950x850")
        
        self.bill_file_path = tk.StringVar(value="Bill.csv")
        self.exclude_file_path = tk.StringVar(value="exclude_patterns.csv")
        self.allowed_file_path = tk.StringVar(value="")  # now mandatory
        self.coordination_percent = tk.StringVar(value="15")
        
        self.setup_ui()
        
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
                                                    width=110, height=28)
        self.output_box.pack(padx=10, pady=10, fill="both", expand=True)
    
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
    
    def update_progress(self, current, total, bill_number):
        self.progress_label.config(
            text=f"Processing bill {current} of {total}: Bill {bill_number}"
        )
        self.root.update()
    
    def format_output(self, validation_result, percent_used):
        """Format validation results in a clear, human‑friendly way."""
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
        
        # Validation rules summary
        self.output_box.insert(tk.END, "📋 VALIDATION CHECKS\n")
        self.output_box.insert(tk.END, "-"*40 + "\n")
        rules = [
            "• columns_present     – all required columns exist",
            "• no_missing_values   – no empty cells in required columns (unless 'blank' allowed)",
            f"• coordination_correct – coordination charge = {percent_used}% of base amount (±{validation_result.get('tolerance',10)})",
            "• allowed_values      – each value belongs to its column's allowed set",
            "• numeric_values      – Cost, Rate per unit, Quantity contain only numbers"
        ]
        for rule in rules:
            self.output_box.insert(tk.END, f"  {rule}\n")
        self.output_box.insert(tk.END, "\n")
        
        total_bills = validation_result['total_bills']
        self.output_box.insert(tk.END, 
            f"🔍 ANALYZING {total_bills} BILL{'S' if total_bills!=1 else ''} "
            f"(coordination = {percent_used}%)\n\n")
        
        passed_bills = []
        failed_bills = []
        
        # Process each bill
        for bill, result in validation_result["results"].items():
            checks = result["checks"]
            bill_passed = all(checks.values())
            
            if bill_passed:
                passed_bills.append(bill)
            else:
                failed_bills.append(bill)
            
            # Bill header with clear pass/fail icon
            status = "✅ PASS" if bill_passed else "❌ FAIL"
            self.output_box.insert(tk.END, f"{status}  Bill {bill}\n")
            self.output_box.insert(tk.END, "  " + "-"*50 + "\n")
            
            # Table of check results with details
            check_order = ['columns_present', 'no_missing_values', 'allowed_values', 'numeric_values', 'coordination_correct']
            for check_name in check_order:
                passed = checks.get(check_name, False)
                icon = "✅" if passed else "❌"
                self.output_box.insert(tk.END, f"  {icon} {check_name}\n")
                
                # Add detailed explanations for failures
                if not passed:
                    if check_name == "no_missing_values":
                        missing = result["details"].get("missing_values", {})
                        for col, rows in missing.items():
                            rows_str = ', '.join(str(r) for r in rows)
                            self.output_box.insert(tk.END, 
                                f"      → Column '{col}' has empty cells at row(s): {rows_str}\n")
                    elif check_name == "allowed_values":
                        violations = result["details"].get("allowed_violations", {})
                        for col, vals in violations.items():
                            vals_str = ', '.join(f"'{v}'" for v in vals)
                            self.output_box.insert(tk.END, 
                                f"      → Column '{col}' contains invalid value(s): {vals_str}\n")
                    elif check_name == "numeric_values":
                        violations = result["details"].get("numeric_violations", {})
                        for col, rows in violations.items():
                            rows_str = ', '.join(str(r) for r in rows)
                            self.output_box.insert(tk.END, 
                                f"      → Column '{col}' has non‑numeric entries at row(s): {rows_str}\n")
                    elif check_name == "coordination_correct":
                        coord = result["details"].get("coordination", {})
                        if not coord.get("has_coordination", False):
                            self.output_box.insert(tk.END, 
                                f"      → No coordination charge row found for this bill\n")
                        else:
                            self.output_box.insert(tk.END, 
                                f"      → Expected: {coord['expected']:.2f}, "
                                f"Actual: {coord['actual_coord']:.2f}, "
                                f"Difference: {coord['diff']:.2f}\n")
                            if coord.get("excluded_items"):
                                self.output_box.insert(tk.END, f"      → Excluded from base amount:\n")
                                for item in coord["excluded_items"]:
                                    self.output_box.insert(tk.END, 
                                        f"          - {item['Item']} (Code: {item['Work code']}): {item['Cost']:.2f}\n")
            self.output_box.insert(tk.END, "\n")
        
        # Final summary – very clear
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
        
        try:
            validator = BillValidator(
                file_path=bill_path,
                exclude_path=exclude_path,
                allowed_values_path=allowed_path,
                coordination_percentage=percent
            )
            result = validator.load_and_validate(progress_callback=self.update_progress)
            self.format_output(result, percent)
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed:\n{e}")
    
    def refresh_output(self):
        self.output_box.delete(1.0, tk.END)
        self.output_box.insert(tk.END, "🔄 Output cleared. Ready to run check again.\n")
        self.progress_label.config(text="")


def main():
    root = tk.Tk()
    app = BillValidationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()