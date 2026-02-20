"""
Bill Validation Module
Handles loading of data, exclusion patterns, allowed values, and per-bill checks.
"""

import pandas as pd
import numpy as np
from collections import defaultdict

class BillValidator:
    def __init__(self, file_path, exclude_path=None, allowed_values_path=None,
                 coordination_percentage=15.0, tolerance=10.0, work_code_path=None):
        """
        Initialize the validator with file paths and settings.

        :param file_path: Path to the main bill CSV file.
        :param exclude_path: Path to CSV with exclusion patterns (optional).
        :param allowed_values_path: Path to CSV with allowed values (mandatory).
        :param coordination_percentage: Percentage used for coordination charge calculation.
        :param tolerance: Allowed difference between expected and actual coordination charge.
        :param work_code_path: Path to CSV with valid work codes and work names (optional).
        """
        self.file_path = file_path
        self.exclude_path = exclude_path
        self.allowed_values_path = allowed_values_path
        self.coordination_percentage = coordination_percentage
        self.tolerance = tolerance
        self.work_code_path = work_code_path

        # Will be populated after loading
        self.df = None
        self.exclude_conditions = []          # list of dicts {column: value, ...}
        self.allowed_dict = {}                 # column -> set of allowed values
        self.required_columns = []              # will be set from allowed_dict keys
        self.valid_work_pairs = set()           # set of (code, name) tuples from reference file
        self.work_code_issues = None            # will hold dict of missing/duplicate info

    def load_exclude_patterns(self):
        """Load exclusion conditions from CSV (if provided).
           Each row in the CSV defines a set of column-value pairs.
           A bill row must match all specified columns to be excluded.
        """
        if not self.exclude_path or not pd.io.common.file_exists(self.exclude_path):
            return

        try:
            excl_df = pd.read_csv(self.exclude_path, dtype=str)  # read all as strings
            # Drop completely empty rows (all NaN)
            excl_df = excl_df.dropna(how='all')
            conditions = []
            for _, row in excl_df.iterrows():
                condition = {}
                for col in excl_df.columns:
                    val = row[col]
                    if pd.isna(val) or str(val).strip() == '':
                        continue
                    condition[col] = str(val).strip()
                if condition:  # only add if at least one condition
                    conditions.append(condition)
            self.exclude_conditions = conditions
        except Exception as e:
            print(f"Warning: Could not load exclude patterns: {e}")
            self.exclude_conditions = []

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

    def load_work_codes(self):
        """Load valid work code and work name pairs from reference CSV.
        Detect missing values and work names that appear with multiple different codes."""
        if not self.work_code_path or not pd.io.common.file_exists(self.work_code_path):
            return

        issues = {
            'missing_code_rows': [],          # list of row numbers (1‑based) with empty work code
            'missing_name_rows': [],          # list of row numbers with empty work name
            'name_with_multiple_codes': {}    # name -> {'codes': [code1, code2], 'rows': [row numbers]}
        }

        try:
            wc_df = pd.read_csv(self.work_code_path, dtype=str)
            # Find columns named 'Work code' and 'Work' (case‑insensitive)
            code_col = None
            name_col = None
            for col in wc_df.columns:
                lower = col.strip().lower()
                if lower == 'work code':
                    code_col = col
                elif lower == 'work':
                    name_col = col
            if code_col is None or name_col is None:
                raise ValueError("Work code file must contain columns named 'Work code' and 'Work'")

            # Maps to collect occurrences
            name_occurrences = defaultdict(list)   # name -> list of row numbers
            name_to_codes = defaultdict(set)       # name -> set of distinct codes

            valid_pairs = set()

            for idx, row in wc_df.iterrows():
                csv_row_num = idx + 2   # row number in the CSV (1‑based, header row = 1)

                code_raw = row[code_col]
                name_raw = row[name_col]

                # Check missing work code
                code_missing = pd.isna(code_raw) or str(code_raw).strip() == ''
                if code_missing:
                    issues['missing_code_rows'].append(csv_row_num)

                # Check missing work name
                name_missing = pd.isna(name_raw) or str(name_raw).strip() == ''
                if name_missing:
                    issues['missing_name_rows'].append(csv_row_num)

                # If either is missing, skip further processing for this row
                if code_missing or name_missing:
                    continue

                code = str(code_raw).strip()
                name = str(name_raw).strip()
                pair = (code, name)

                # Record occurrences
                name_occurrences[name].append(csv_row_num)
                name_to_codes[name].add(code)
                valid_pairs.add(pair)

            # Find names that appear with more than one distinct work code
            name_multiple_codes = {}
            for name, codes in name_to_codes.items():
                if len(codes) > 1:
                    rows = name_occurrences[name]   # all row numbers where this name appears
                    name_multiple_codes[name] = {
                        'codes': sorted(codes),
                        'rows': rows
                    }
            if name_multiple_codes:
                issues['name_with_multiple_codes'] = name_multiple_codes

            self.valid_work_pairs = valid_pairs
            # Only store issues if any were found
            if any(issues.values()):
                self.work_code_issues = issues
            else:
                self.work_code_issues = None

        except Exception as e:
            raise ValueError(f"Error loading work codes: {e}")



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
        Coordination rows are those where Work code is exactly 'C'.
        Exclusions are based on conditions loaded from exclude CSV.
        Returns (passed, details_dict).
        """
        # Identify coordination charge row(s) – exact match on Work code == 'C'
        coord_mask = bill_df['Work code'].astype(str).str.strip() == 'C'
        coord_rows = bill_df[coord_mask]

        details = {
            'has_coordination': not coord_rows.empty,
            'base_amount': 0.0,
            'expected': 0.0,
            'actual_coord': 0.0,
            'diff': 0.0,
            'excluded_items': []
        }

        if coord_rows.empty:
            # No coordination row – treat as pass
            return True, details

        actual_coord = coord_rows['Cost'].sum()
        details['actual_coord'] = actual_coord

        # Build exclusion mask based on all conditions
        exclude_mask = pd.Series([False] * len(bill_df), index=bill_df.index)

        for condition in self.exclude_conditions:
            # Only consider this condition if all its columns exist in the bill
            if not all(col in bill_df.columns for col in condition.keys()):
                continue

            # Start with all rows True, then AND each column condition using robust comparison
            cond_mask = pd.Series([True] * len(bill_df), index=bill_df.index)
            for col, val in condition.items():
                # Define a matching function that tries numeric comparison first
                def match_func(x):
                    if pd.isna(x):
                        return False
                    # Try numeric comparison
                    try:
                        # Convert both to float and compare within tolerance
                        return abs(float(x) - float(val)) < 1e-9
                    except ValueError:
                        # Fall back to string comparison
                        return str(x).strip() == val
                cond_mask &= bill_df[col].apply(match_func)
            exclude_mask |= cond_mask

        # Remove coordination rows themselves from base
        base_mask = ~exclude_mask & ~coord_mask
        base_df = bill_df[base_mask]
        base_sum = base_df['Cost'].sum()
        details['base_amount'] = base_sum

        # Record excluded items (for reporting)
        excluded = bill_df[exclude_mask & ~coord_mask]
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

    def _check_work_code_name_pairs(self, bill_df):
        """
        Check that:
          - 'Work code' and 'Work' columns exist.
          - No missing values in these columns.
          - Every (work code, work name) pair is valid according to reference file.
        Returns (passed, details_dict).
        """
        details = {
            'missing_code': [],
            'missing_name': [],
            'invalid_pairs': defaultdict(list)
        }

        # Check that required columns exist in the bill
        if 'Work code' not in bill_df.columns or 'Work' not in bill_df.columns:
            missing_cols = []
            if 'Work code' not in bill_df.columns:
                missing_cols.append('Work code')
            if 'Work' not in bill_df.columns:
                missing_cols.append('Work')
            return False, {'missing_columns': missing_cols}

        for idx, row in bill_df.iterrows():
            code = row.get('Work code', None)
            name = row.get('Work', None)

            # Check for missing work code
            if pd.isna(code) or str(code).strip() == '':
                details['missing_code'].append(idx + 2)
                continue

            # Check for missing work name
            if pd.isna(name) or str(name).strip() == '':
                details['missing_name'].append(idx + 2)
                continue

            # Both present, validate pair if we have a reference
            if self.valid_work_pairs:
                code_str = str(code).strip()
                name_str = str(name).strip()
                if (code_str, name_str) not in self.valid_work_pairs:
                    key = f"{code_str}|{name_str}"
                    details['invalid_pairs'][key].append(idx + 2)

        details['invalid_pairs'] = dict(details['invalid_pairs'])

        if self.valid_work_pairs:
            passed = (len(details['missing_code']) == 0 and
                      len(details['missing_name']) == 0 and
                      len(details['invalid_pairs']) == 0)
        else:
            passed = (len(details['missing_code']) == 0 and
                      len(details['missing_name']) == 0)

        return passed, details

    def load_and_validate(self, progress_callback=None):
        """
        Main validation workflow.
        Returns a dictionary with overall results.
        """
        # 1. Load exclude patterns and allowed values
        self.load_exclude_patterns()
        self.load_allowed_values()
        # 2. Load work codes if provided
        self.load_work_codes()

        # 3. Load main bill CSV
        try:
            self.df = pd.read_csv(self.file_path)
        except Exception as e:
            raise ValueError(f"Could not read bill file: {e}")

        # 4. Global column presence check
        cols_present, missing_cols = self._check_columns_present(self.df.columns)
        if not cols_present:
            return {
                'global_columns_ok': False,
                'missing_columns': missing_cols,
                'exclude_conditions': self.exclude_conditions,
                'allowed_dict': self.allowed_dict,
                'work_pairs_checked': bool(self.valid_work_pairs),
                'work_code_issues': self.work_code_issues,
                'total_bills': 0,
                'results': {}
            }

        # 5. Group by Contract Bill No
        bill_numbers = self.df['Contract Bill No'].dropna().unique()
        total_bills = len(bill_numbers)
        results = {}

        for idx, bill in enumerate(bill_numbers, start=1):
            if progress_callback:
                progress_callback(idx, total_bills, bill)

            bill_df = self.df[self.df['Contract Bill No'] == bill].copy()
            bill_df['Cost'] = pd.to_numeric(bill_df['Cost'], errors='coerce')

            checks = {}
            details = {}

            checks['columns_present'] = True

            nmv_ok, nmv_details = self._check_no_missing_values(bill_df)
            checks['no_missing_values'] = nmv_ok
            details['missing_values'] = nmv_details

            coord_ok, coord_details = self._check_coordination(bill_df)
            checks['coordination_correct'] = coord_ok
            details['coordination'] = coord_details

            av_ok, av_details = self._check_allowed_values(bill_df)
            checks['allowed_values'] = av_ok
            details['allowed_violations'] = av_details

            num_ok, num_details = self._check_numeric_values(bill_df)
            checks['numeric_values'] = num_ok
            details['numeric_violations'] = num_details

            wc_ok, wc_details = self._check_work_code_name_pairs(bill_df)
            checks['work_pairs_valid'] = wc_ok
            details['work_pairs_checked'] = bool(self.valid_work_pairs)
            details['work_pair_violations'] = wc_details

            results[bill] = {
                'checks': checks,
                'details': details
            }

        return {
            'global_columns_ok': True,
            'missing_columns': [],
            'exclude_conditions': self.exclude_conditions,
            'allowed_dict': self.allowed_dict,
            'work_pairs_checked': bool(self.valid_work_pairs),
            'work_code_issues': self.work_code_issues,
            'total_bills': total_bills,
            'results': results,
            'tolerance': self.tolerance
        }