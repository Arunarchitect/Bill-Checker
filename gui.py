"""
Bill Validation GUI Application
Handles the user interface and display
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
        self.root.geometry("900x800")
        
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
        """Format validation results with rules list and per-bill status table"""
        self.output_box.delete(1.0, tk.END)
        
        # Global column check
        if not validation_result["global_columns_ok"]:
            self.output_box.insert(tk.END, 
                f"❌ Missing Columns: {validation_result['missing_columns']}\n\n")
            return  # can't proceed if columns missing
        
        self.output_box.insert(tk.END, "✅ All required columns present.\n\n")
        
        # Exclusion patterns
        exclude_item = validation_result["exclude_item_patterns"]
        exclude_work = validation_result["exclude_workcode_patterns"]
        if exclude_item or exclude_work:
            self.output_box.insert(tk.END, "📋 Loaded exclusion patterns:\n")
            if exclude_item:
                self.output_box.insert(tk.END, f"   Item patterns: {exclude_item}\n")
            if exclude_work:
                self.output_box.insert(tk.END, f"   Work code patterns: {exclude_work}\n")
            self.output_box.insert(tk.END, "\n")
        
        # Allowed values
        allowed_dict = validation_result["allowed_dict"]
        if allowed_dict:
            self.output_box.insert(tk.END, "📋 Loaded allowed values for columns:\n")
            for col, values in sorted(allowed_dict.items()):
                self.output_box.insert(tk.END, f"   {col}: {sorted(values)}\n")
            self.output_box.insert(tk.END, "\n")
        else:
            self.output_box.insert(tk.END, "⚠ No allowed values loaded – check will fail if any column has restrictions.\n\n")
        
        # Define check rules
        check_rules = {
            "columns_present": "All required columns are present in the file",
            "no_missing_values": "No missing (empty) values in required columns for this bill",
            "coordination_correct": f"Coordination charge is correct within tolerance (±{validation_result.get('tolerance',10)}) using {percent_used}% of base amount",
            "allowed_values": "All values in specified columns belong to the allowed set (mandatory check)",
            "numeric_values": "Numeric columns (Cost, Rate per unit, Quantity) contain only numbers"
        }
        
        # Display rules
        self.output_box.insert(tk.END, "📋 VALIDATION RULES\n")
        self.output_box.insert(tk.END, "="*60 + "\n")
        for check, desc in check_rules.items():
            self.output_box.insert(tk.END, f"• {check}: {desc}\n")
        self.output_box.insert(tk.END, "\n")
        
        total_bills = validation_result['total_bills']
        self.output_box.insert(tk.END, f"Checking {total_bills} bills with {percent_used}% coordination...\n\n")
        
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
            
            # Bill header
            status = "✅" if bill_passed else "❌"
            self.output_box.insert(tk.END, f"{status} Bill {bill}\n")
            self.output_box.insert(tk.END, "-"*40 + "\n")
            
            # Table of check results
            for check_name, passed in checks.items():
                icon = "✅" if passed else "❌"
                self.output_box.insert(tk.END, f"  {icon} {check_name}\n")
                
                # If failed, add failure details indented
                if not passed:
                    if check_name == "no_missing_values":
                        missing = result["details"]["missing_values"]
                        for col, rows in missing.items():
                            self.output_box.insert(tk.END, f"      Missing in '{col}' at rows: {rows}\n")
                    elif check_name == "coordination_correct":
                        coord = result["details"]["coordination"]
                        if not coord.get("has_coordination", False):
                            self.output_box.insert(tk.END, f"      No coordination charge found\n")
                        else:
                            self.output_box.insert(tk.END, 
                                f"      Expected: {coord['expected']:.2f}, Actual: {coord['actual_coord']:.2f}, Diff: {coord['diff']:.2f}\n")
                            if coord.get("excluded_items"):
                                self.output_box.insert(tk.END, f"      Excluded items:\n")
                                for item in coord["excluded_items"]:
                                    self.output_box.insert(tk.END, 
                                        f"        - {item['Item']} (Code: {item['Work code']}): {item['Cost']:.2f}\n")
                    elif check_name == "allowed_values":
                        violations = result["details"]["allowed_violations"]
                        for col, vals in violations.items():
                            self.output_box.insert(tk.END, f"      Invalid values in '{col}': {vals}\n")
                    elif check_name == "numeric_values":
                        violations = result["details"]["numeric_violations"]
                        for col, vals in violations.items():
                            self.output_box.insert(tk.END, f"      Non-numeric values in '{col}': {vals}\n")
                    # columns_present is global, already handled at top
            self.output_box.insert(tk.END, "\n")
        
        # Final summary
        self.output_box.insert(tk.END, "="*60 + "\n")
        self.output_box.insert(tk.END, "FINAL SUMMARY\n")
        self.output_box.insert(tk.END, "="*60 + "\n")
        self.output_box.insert(tk.END, f"Total bills processed: {total_bills}\n")
        self.output_box.insert(tk.END, f"✅ Bills passed all checks: {len(passed_bills)}")
        if passed_bills:
            self.output_box.insert(tk.END, f" - {', '.join(str(b) for b in passed_bills)}\n")
        else:
            self.output_box.insert(tk.END, "\n")
        self.output_box.insert(tk.END, f"❌ Bills failed one or more checks: {len(failed_bills)}")
        if failed_bills:
            self.output_box.insert(tk.END, f" - {', '.join(str(b) for b in failed_bills)}\n")
        else:
            self.output_box.insert(tk.END, "\n")
        
        # Summary line in the requested format
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