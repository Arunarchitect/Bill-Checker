"""
Bill Validation Module
Handles loading of data, exclusion patterns, allowed values, and per-bill checks.
"""

import pandas as pd
import numpy as np
from collections import defaultdict

class BillValidator:
    def __init__(self, file_path, exclude_path=None, allowed_values_path=None, coordination_percentage=15.0, tolerance=10.0):
        """
        Initialize the validator with file paths and settings.
        
        :param file_path: Path to the main bill CSV file.
        :param exclude_path: Path to CSV with exclusion patterns (optional).
        :param allowed_values_path: Path to CSV with allowed values (mandatory).
        :param coordination_percentage: Percentage used for coordination charge calculation.
        :param tolerance: Allowed difference between expected and actual coordination charge.
        """
        self.file_path = file_path
        self.exclude_path = exclude_path
        self.allowed_values_path = allowed_values_path
        self.coordination_percentage = coordination_percentage
        self.tolerance = tolerance
        
        # Will be populated after loading
        self.df = None
        self.exclude_item_patterns = []
        self.exclude_workcode_patterns = []
        self.allowed_dict = {}          # column -> set of allowed values
        self.required_columns = []      # will be set from allowed_dict keys
        
    def load_exclude_patterns(self):
        """Load exclusion patterns from CSV (if provided)."""
        if not self.exclude_path or not pd.io.common.file_exists(self.exclude_path):
            return
        
        try:
            excl_df = pd.read_csv(self.exclude_path)
            # Expect columns: 'type' and 'pattern' (type can be 'Item' or 'Work code')
            if 'type' in excl_df.columns and 'pattern' in excl_df.columns:
                for _, row in excl_df.iterrows():
                    if row['type'].strip().lower() == 'item':
                        self.exclude_item_patterns.append(row['pattern'].strip())
                    elif row['type'].strip().lower() == 'work code':
                        self.exclude_workcode_patterns.append(row['pattern'].strip())
            else:
                # Fallback: assume one column with item patterns (for backward compatibility)
                self.exclude_item_patterns = excl_df.iloc[:, 0].dropna().astype(str).tolist()
        except Exception as e:
            print(f"Warning: Could not load exclude patterns: {e}")
    
    def load_allowed_values(self):
        """
        Load allowed values from CSV (mandatory).
        Expected format:
            - First row is the header, containing all column names that must be present.
            - Each subsequent row provides values for those columns.
            - For a given column, the set of allowed values is the collection of all
              non‑empty, non‑blank strings appearing in that column.
            - The special token 'any' means any non‑empty value is allowed.
            - The special token 'blank' indicates that empty values are permitted.
        """
        if not self.allowed_values_path or not pd.io.common.file_exists(self.allowed_values_path):
            raise FileNotFoundError(f"Allowed values file not found: {self.allowed_values_path}")
        
        try:
            # Read all columns as strings to preserve original representation (e.g., '6' not '6.0')
            allowed_df = pd.read_csv(self.allowed_values_path, dtype=str)
            
            # The columns of this DataFrame are the required columns.
            self.required_columns = list(allowed_df.columns)
            
            # Build allowed_dict: for each column, collect all non‑empty, non‑blank values.
            self.allowed_dict = {}
            for col in self.required_columns:
                # Get all values from this column, drop NaN/empty, convert to string, strip.
                values = allowed_df[col].dropna().astype(str).str.strip()
                # Keep only non‑empty strings.
                values = values[values != '']
                # Create a set of unique values.
                unique_vals = set(values)
                self.allowed_dict[col] = unique_vals
            
        except Exception as e:
            raise ValueError(f"Error loading allowed values: {e}")
    
    def _check_columns_present(self, df_columns):
        """Check that all required columns (from allowed_dict) are present."""
        missing = [col for col in self.required_columns if col not in df_columns]
        return len(missing) == 0, missing
    
    def _check_numeric_values(self, bill_df):
        """
        Check that numeric columns contain only numbers.
        Empty cells are skipped (they are handled by missing‑values check).
        """
        numeric_cols = ['Cost', 'Rate per unit', 'Quantity']
        violations = defaultdict(list)
        for col in numeric_cols:
            if col not in bill_df.columns:
                continue
            for idx, val in bill_df[col].items():
                # Skip empty cells (they are either allowed by 'blank' or will be caught by missing check)
                if pd.isna(val) or str(val).strip() == '':
                    continue
                try:
                    float(val)
                except (ValueError, TypeError):
                    violations[col].append(idx + 2)  # +2 because 0-index + header row
        return len(violations) == 0, dict(violations)
    
    def _check_no_missing_values(self, bill_df):
        """
        Check for empty cells in required columns.
        If a column's allowed set contains the special token 'blank', missing values are allowed.
        """
        missing = defaultdict(list)
        for col in self.required_columns:
            if col not in bill_df.columns:
                continue
            # If allowed set contains 'blank', missing values are allowed
            allowed_set = self.allowed_dict.get(col, set())
            if 'blank' in allowed_set:
                continue
            # Find rows where value is NaN or empty string after stripping
            empty_mask = bill_df[col].isna() | (bill_df[col].astype(str).str.strip() == '')
            empty_indices = bill_df.index[empty_mask].tolist()
            if empty_indices:
                # Convert to 1‑based row numbers (header row is 1, data rows start at 2)
                missing[col] = [idx + 2 for idx in empty_indices]
        return len(missing) == 0, dict(missing)
    
    def _check_allowed_values(self, bill_df):
        """
        Check that values in columns with allowed sets are within those sets.
        - If the allowed set contains 'any', any non‑empty value is permitted.
        - Empty cells are skipped (they are handled by missing‑values check).
        - If the allowed set contains 'blank', that only affects missing‑values; here it is treated as a normal value.
        """
        violations = defaultdict(list)
        for col, allowed_set in self.allowed_dict.items():
            if col not in bill_df.columns:
                continue
            # If the allowed set contains 'any', treat as no restrictions for non‑empty values
            if 'any' in allowed_set:
                continue
            # If allowed set is empty, treat as no restrictions (though this shouldn't happen with valid files)
            if not allowed_set:
                continue
            for idx, val in bill_df[col].items():
                # Skip empty cells (they are either allowed by 'blank' in missing check)
                if pd.isna(val) or str(val).strip() == '':
                    continue
                str_val = str(val).strip()
                if str_val not in allowed_set:
                    violations[col].append(str_val)
        # Remove duplicates in the list of invalid values per column
        violations = {col: sorted(set(vals)) for col, vals in violations.items()}
        return len(violations) == 0, violations
    
    def _check_coordination(self, bill_df):
        """
        Check coordination charge correctness.
        Returns (passed, details_dict).
        """
        # Identify coordination charge row(s)
        coord_mask = (
            bill_df['Work'].astype(str).str.contains('coordination', case=False, na=False) |
            bill_df['Work code'].astype(str).str.startswith('C')
        )
        coord_rows = bill_df[coord_mask]
        
        details = {
            'has_coordination': not coord_rows.empty,
            'expected': 0.0,
            'actual_coord': 0.0,
            'diff': 0.0,
            'excluded_items': []
        }
        
        if coord_rows.empty:
            return False, details
        
        actual_coord = coord_rows['Cost'].sum()
        details['actual_coord'] = actual_coord
        
        # Build base amount by excluding patterns
        # Create base_mask with the same index as bill_df to avoid pandas warning
        base_mask = pd.Series([True] * len(bill_df), index=bill_df.index)
        
        # Exclude by item patterns
        for pattern in self.exclude_item_patterns:
            base_mask &= ~bill_df['Item'].astype(str).str.contains(pattern, case=False, na=False)
        
        # Exclude by work code patterns
        for pattern in self.exclude_workcode_patterns:
            base_mask &= ~bill_df['Work code'].astype(str).str.contains(pattern, case=False, na=False)
        
        # Also explicitly exclude any coordination rows
        base_mask &= ~coord_mask
        
        base_df = bill_df[base_mask]
        base_sum = base_df['Cost'].sum()
        
        # Record excluded items for reporting (optional)
        excluded = bill_df[~base_mask & ~coord_mask]
        for _, row in excluded.iterrows():
            details['excluded_items'].append({
                'Item': row['Item'],
                'Work code': row['Work code'],
                'Cost': row['Cost']
            })
        
        expected = base_sum * (self.coordination_percentage / 100.0)
        details['expected'] = expected
        
        diff = abs(expected - actual_coord)
        details['diff'] = diff
        
        passed = diff <= self.tolerance
        return passed, details
    
    def load_and_validate(self, progress_callback=None):
        """
        Main validation workflow.
        Returns a dictionary with overall results.
        """
        # 1. Load exclude patterns and allowed values
        self.load_exclude_patterns()
        self.load_allowed_values()
        
        # 2. Load main bill CSV
        try:
            self.df = pd.read_csv(self.file_path)
        except Exception as e:
            raise ValueError(f"Could not read bill file: {e}")
        
        # 3. Global column presence check
        cols_present, missing_cols = self._check_columns_present(self.df.columns)
        if not cols_present:
            return {
                'global_columns_ok': False,
                'missing_columns': missing_cols,
                'exclude_item_patterns': self.exclude_item_patterns,
                'exclude_workcode_patterns': self.exclude_workcode_patterns,
                'allowed_dict': self.allowed_dict,
                'total_bills': 0,
                'results': {}
            }
        
        # 4. Group by Contract Bill No
        bill_numbers = self.df['Contract Bill No'].dropna().unique()
        total_bills = len(bill_numbers)
        results = {}
        
        for idx, bill in enumerate(bill_numbers, start=1):
            if progress_callback:
                progress_callback(idx, total_bills, bill)
            
            bill_df = self.df[self.df['Contract Bill No'] == bill].copy()
            
            # Ensure Cost is numeric for calculations
            bill_df['Cost'] = pd.to_numeric(bill_df['Cost'], errors='coerce')
            
            checks = {}
            details = {}
            
            # Columns present (already global, but we can record per bill as True)
            checks['columns_present'] = True   # because global check passed
            
            # No missing values
            nmv_ok, nmv_details = self._check_no_missing_values(bill_df)
            checks['no_missing_values'] = nmv_ok
            details['missing_values'] = nmv_details
            
            # Coordination correct
            coord_ok, coord_details = self._check_coordination(bill_df)
            checks['coordination_correct'] = coord_ok
            details['coordination'] = coord_details
            
            # Allowed values
            av_ok, av_details = self._check_allowed_values(bill_df)
            checks['allowed_values'] = av_ok
            details['allowed_violations'] = av_details
            
            # Numeric values
            num_ok, num_details = self._check_numeric_values(bill_df)
            checks['numeric_values'] = num_ok
            details['numeric_violations'] = num_details
            
            results[bill] = {
                'checks': checks,
                'details': details
            }
        
        return {
            'global_columns_ok': True,
            'missing_columns': [],
            'exclude_item_patterns': self.exclude_item_patterns,
            'exclude_workcode_patterns': self.exclude_workcode_patterns,
            'allowed_dict': self.allowed_dict,
            'total_bills': total_bills,
            'results': results,
            'tolerance': self.tolerance
        }