"""
Bill Validation Core Module
Handles all the data processing and validation logic
"""

import pandas as pd
import os

class BillValidator:
    """Main validator class for bill processing"""
    
    def __init__(self, file_path="Bill.csv", exclude_path="exclude_patterns.csv", 
                 allowed_values_path=None, numeric_columns=None,
                 tolerance=10, coordination_percentage=15):
        """
        :param file_path: Path to the main bill CSV file
        :param exclude_path: Path to the exclusion patterns CSV
        :param allowed_values_path: Path to CSV defining allowed values per column (mandatory)
        :param numeric_columns: List of column names that must contain numeric data
        :param tolerance: Allowed difference between actual and expected coordination charge
        :param coordination_percentage: The percentage (e.g., 15 for 15%) to calculate expected coordination
        """
        self.file_path = file_path
        self.exclude_path = exclude_path
        self.allowed_values_path = allowed_values_path
        self.numeric_columns = numeric_columns if numeric_columns else ["Cost", "Rate per unit", "Quantity"]
        self.tolerance = tolerance
        self.coordination_percentage = coordination_percentage
        # required_columns will be set after loading allowed values
        self.required_columns = []
        self.allowed_columns = []
        
    def load_exclude_patterns(self):
        """Load exclusion patterns from CSV file"""
        exclude_item_patterns = []
        exclude_workcode_patterns = []
        
        if not os.path.exists(self.exclude_path):
            return exclude_item_patterns, exclude_workcode_patterns
        
        try:
            exclude_df = pd.read_csv(self.exclude_path)
            
            if 'Item' in exclude_df.columns:
                exclude_item_patterns = exclude_df['Item'].dropna().astype(str).tolist()
            
            if 'Work code' in exclude_df.columns:
                exclude_workcode_patterns = exclude_df['Work code'].dropna().astype(str).tolist()
                    
        except Exception as e:
            raise Exception(f"Error reading exclude_patterns.csv: {e}")
        
        return exclude_item_patterns, exclude_workcode_patterns
    
    def load_allowed_values(self):
        """
        Load allowed values per column from a CSV where the first row is the header,
        and subsequent rows list allowed values for each column (non‑empty cells).
        Also sets self.allowed_columns and self.required_columns (allowed columns + 'Cost').
        Returns a dictionary: column_name -> set of allowed values (as strings).
        """
        allowed = {}
        if not self.allowed_values_path or not os.path.exists(self.allowed_values_path):
            # Should not happen because allowed file is mandatory, but if missing, return empty
            return allowed

        try:
            df = pd.read_csv(self.allowed_values_path, keep_default_na=False, dtype=str)
            # keep_default_na=False prevents pandas from converting empty cells to NaN
            for col in df.columns:
                # Get non-empty, non-null values
                values = df[col].dropna()
                values = values[values.str.strip() != ""]
                if not values.empty:
                    allowed[col] = set(values.str.strip())
            
            self.allowed_columns = list(allowed.keys())
            # Required columns = allowed columns + 'Cost' (essential for calculations)
            self.required_columns = list(set(self.allowed_columns + ['Cost']))
        except Exception as e:
            raise Exception(f"Error reading allowed values CSV: {e}")

        return allowed
    
    def is_coordination_row(self, item_text):
        """Check if a row is a coordination charge"""
        return "coordination charge" in str(item_text).lower()
    
    def should_exclude_row(self, item_text, work_code, item_patterns, workcode_patterns):
        """Check if a row should be excluded from base calculation"""
        
        # Check Item column patterns
        for pattern in item_patterns:
            if pattern and pd.notna(pattern) and pattern.lower() in str(item_text).lower():
                return True
        
        # Check Work code column patterns
        for pattern in workcode_patterns:
            if not pattern or pd.isna(pattern):
                continue
                
            pattern_str = str(pattern)
            
            if pattern_str.lower().startswith("starts with "):
                prefix = pattern_str[12:].strip()
                if str(work_code).startswith(prefix):
                    return True
            elif pattern_str == str(work_code):
                return True
            elif pattern_str and pattern_str.lower() in str(work_code).lower():
                return True
        
        return False
    
    def validate_columns(self, df):
        """Check if all required columns are present"""
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        return missing_columns
    
    def find_missing_values(self, df):
        """Find rows with missing values in required columns"""
        missing_data = {}
        for col in self.required_columns:
            if col in df.columns:
                missing_rows = df[df[col].isna() | (df[col].astype(str).str.strip() == "")]
                if not missing_rows.empty:
                    missing_data[col] = list(missing_rows['S.n'])
        return missing_data
    
    def check_allowed_values(self, bill_df, allowed_dict):
        """
        Check that all values in specified columns are in the allowed set.
        Returns (passed, violations) where violations is a dict: column -> list of invalid values.
        """
        violations = {}
        for col, allowed_set in allowed_dict.items():
            if col not in bill_df.columns:
                # Column missing – will be caught by validate_columns, so we can skip here
                continue
            # Get non-null values
            values = bill_df[col].dropna().astype(str).str.strip()
            invalid = values[~values.isin(allowed_set)].unique()
            if len(invalid) > 0:
                violations[col] = list(invalid)
        return len(violations) == 0, violations
    
    def check_numeric_columns(self, bill_df):
        """
        Check that specified columns contain only numeric data.
        Returns (passed, violations) where violations is a dict: column -> list of non-numeric values.
        """
        violations = {}
        for col in self.numeric_columns:
            if col not in bill_df.columns:
                continue
            # Try converting to numeric, coerce errors to NaN
            converted = pd.to_numeric(bill_df[col], errors='coerce')
            # Find rows where original was not null but converted is NaN
            mask = bill_df[col].notna() & converted.isna()
            if mask.any():
                bad_values = bill_df.loc[mask, col].astype(str).unique()
                violations[col] = list(bad_values)
        return len(violations) == 0, violations
    
    def process_bill(self, bill_df, exclude_item_patterns, exclude_workcode_patterns,
                     allowed_dict, global_columns_ok):
        """Process a single bill and return validation results with multiple checks"""
        
        results = {
            "bill_number": None,  # will be set by caller
            "checks": {
                "columns_present": global_columns_ok,  # same for all bills
                "no_missing_values": True,
                "coordination_correct": False,
                "allowed_values": True,
                "numeric_values": True
            },
            "details": {
                "missing_values": {},
                "coordination": {},
                "allowed_violations": {},
                "numeric_violations": {}
            }
        }
        
        # Check missing values in this bill
        missing = {}
        for col in self.required_columns:
            if col in bill_df.columns:
                missing_rows = bill_df[bill_df[col].isna() | (bill_df[col].astype(str).str.strip() == "")]
                if not missing_rows.empty:
                    missing[col] = list(missing_rows['S.n'])
        if missing:
            results["checks"]["no_missing_values"] = False
            results["details"]["missing_values"] = missing
        
        # Coordination charge check
        coord_rows = bill_df[bill_df["Item"].astype(str).str.lower().str.contains("coordination charge", na=False)]
        if coord_rows.empty:
            results["checks"]["coordination_correct"] = False  # no coordination row, but we might treat as fail
            results["details"]["coordination"] = {"has_coordination": False}
        else:
            actual_coord = coord_rows["Cost"].sum()
            
            base_df = bill_df[~bill_df.apply(
                lambda row: self.should_exclude_row(
                    row['Item'],
                    row['Work code'],
                    exclude_item_patterns,
                    exclude_workcode_patterns
                ),
                axis=1
            )]
            base_sum = base_df["Cost"].sum()
            multiplier = self.coordination_percentage / 100.0
            expected = base_sum * multiplier
            diff = abs(expected - actual_coord)
            is_correct = diff <= self.tolerance
            
            excluded_df = bill_df[bill_df.apply(
                lambda row: self.should_exclude_row(
                    row['Item'],
                    row['Work code'],
                    exclude_item_patterns,
                    exclude_workcode_patterns
                ),
                axis=1
            )]
            
            results["checks"]["coordination_correct"] = is_correct
            results["details"]["coordination"] = {
                "has_coordination": True,
                "actual_coord": actual_coord,
                "base_sum": base_sum,
                "total_sum": bill_df["Cost"].sum(),
                "expected": expected,
                "diff": diff,
                "excluded_items": excluded_df.to_dict('records') if not excluded_df.empty else []
            }
        
        # Allowed values check
        allowed_ok, allowed_violations = self.check_allowed_values(bill_df, allowed_dict)
        results["checks"]["allowed_values"] = allowed_ok
        results["details"]["allowed_violations"] = allowed_violations
        
        # Numeric columns check
        numeric_ok, numeric_violations = self.check_numeric_columns(bill_df)
        results["checks"]["numeric_values"] = numeric_ok
        results["details"]["numeric_violations"] = numeric_violations
        
        return results
    
    def validate_all_bills(self, df, exclude_item_patterns, exclude_workcode_patterns,
                           allowed_dict, global_columns_ok, progress_callback=None):
        """Validate all bills in the dataframe"""
        results = {}
        
        # Get unique bill numbers
        bill_numbers = df["Contract Bill No"].dropna().unique()
        bill_numbers = [b for b in bill_numbers if str(b).strip()]
        
        total_bills = len(bill_numbers)
        
        for idx, bill in enumerate(bill_numbers):
            if progress_callback:
                progress_callback(idx + 1, total_bills, bill)
                
            bill_df = df[df["Contract Bill No"] == bill].copy()
            bill_result = self.process_bill(
                bill_df, exclude_item_patterns, exclude_workcode_patterns,
                allowed_dict, global_columns_ok
            )
            bill_result["bill_number"] = bill
            results[bill] = bill_result
        
        return results
    
    def load_and_validate(self, progress_callback=None):
        """Main method to load data and run validation"""
        
        if not os.path.exists(self.file_path):
            raise FileNotFoundError("Bill.csv not found!")
        
        try:
            df = pd.read_csv(self.file_path)
        except Exception as e:
            raise Exception(f"Failed to read CSV: {e}")
        
        # Load allowed values (this also sets self.required_columns)
        allowed_dict = self.load_allowed_values()
        if not allowed_dict:
            raise Exception("Allowed values file is empty or could not be loaded.")
        
        # Check columns globally using the newly set required_columns
        missing_columns = self.validate_columns(df)
        global_columns_ok = len(missing_columns) == 0
        
        # Convert Cost to numeric (for processing)
        df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce")
        
        # Load exclusion patterns
        exclude_item_patterns, exclude_workcode_patterns = self.load_exclude_patterns()
        
        # Validate all bills
        results = self.validate_all_bills(
            df, exclude_item_patterns, exclude_workcode_patterns,
            allowed_dict, global_columns_ok, progress_callback
        )
        
        return {
            "missing_columns": missing_columns,
            "global_columns_ok": global_columns_ok,
            "exclude_item_patterns": exclude_item_patterns,
            "exclude_workcode_patterns": exclude_workcode_patterns,
            "allowed_dict": allowed_dict,
            "results": results,
            "total_bills": len(results)
        }