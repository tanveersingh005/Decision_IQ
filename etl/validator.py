import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ETLValidator")

class ETLValidator:
    """
    Data Quality Validation Engine for DecisionIQ ETL.
    Contains assertions for schema adherence, primary keys, null values, ranges, and referential integrity.
    """
    
    @staticmethod
    def validate_pk(df, table_name, pk_col):
        """
        Validates that the primary key is unique and non-null.
        """
        if pk_col not in df.columns:
            logger.error(f"Validation FAILED: Primary key '{pk_col}' not found in table '{table_name}'.")
            return False
            
        null_count = df[pk_col].isnull().sum()
        if null_count > 0:
            logger.error(f"Validation FAILED: Table '{table_name}' has {null_count} null primary keys.")
            return False
            
        dup_count = df[pk_col].duplicated().sum()
        if dup_count > 0:
            logger.warning(f"Validation WARNING: Table '{table_name}' has {dup_count} duplicate primary keys.")
            return False
            
        logger.info(f"Validation PASSED: Primary key '{pk_col}' in '{table_name}' is unique and non-null.")
        return True
        
    @staticmethod
    def validate_not_null(df, table_name, columns):
        """
        Validates that specified columns contain zero null values.
        """
        passed = True
        for col in columns:
            if col not in df.columns:
                logger.error(f"Validation FAILED: Column '{col}' not found in table '{table_name}'.")
                passed = False
                continue
                
            null_count = df[col].isnull().sum()
            if null_count > 0:
                logger.error(f"Validation FAILED: Column '{col}' in table '{table_name}' has {null_count} null values.")
                passed = False
                
        if passed:
            logger.info(f"Validation PASSED: Non-null constraints satisfied in '{table_name}' for columns {columns}.")
        return passed
        
    @staticmethod
    def validate_ranges(df, table_name, range_rules):
        """
        Validates numeric range rules.
        range_rules is a dict: {column_name: (min_val, max_val)}
        Use None if there is no boundary.
        """
        passed = True
        for col, boundaries in range_rules.items():
            if col not in df.columns:
                logger.error(f"Validation FAILED: Column '{col}' not found in table '{table_name}'.")
                passed = False
                continue
                
            min_val, max_val = boundaries
            
            # Check min boundary
            if min_val is not None:
                violations = (df[col] < min_val).sum()
                if violations > 0:
                    logger.error(f"Validation FAILED: Column '{col}' in '{table_name}' has {violations} values below {min_val}.")
                    passed = False
                    
            # Check max boundary
            if max_val is not None:
                violations = (df[col] > max_val).sum()
                if violations > 0:
                    logger.error(f"Validation FAILED: Column '{col}' in '{table_name}' has {violations} values above {max_val}.")
                    passed = False
                    
        if passed:
            logger.info(f"Validation PASSED: Numeric ranges satisfied in '{table_name}' for rules {list(range_rules.keys())}.")
        return passed
        
    @staticmethod
    def validate_fk(df_child, child_table, fk_col, df_parent, parent_table, pk_col):
        """
        Validates referential integrity: every value in child_table.fk_col must exist in parent_table.pk_col.
        Handles nulls in fk_col by ignoring them (non-identifying relationships).
        """
        if fk_col not in df_child.columns:
            logger.error(f"Validation FAILED: Foreign key '{fk_col}' not found in child table '{child_table}'.")
            return False
        if pk_col not in df_parent.columns:
            logger.error(f"Validation FAILED: Parent key '{pk_col}' not found in parent table '{parent_table}'.")
            return False
            
        child_vals = df_child[fk_col].dropna().unique()
        parent_vals = set(df_parent[pk_col].unique())
        
        invalid_vals = [val for val in child_vals if val not in parent_vals]
        if len(invalid_vals) > 0:
            logger.error(f"Validation FAILED: Foreign key violation between '{child_table}.{fk_col}' and '{parent_table}.{pk_col}'. "
                         f"Invalid references: {invalid_vals[:5]}... Total: {len(invalid_vals)}")
            return False
            
        logger.info(f"Validation PASSED: Referential integrity verified between '{child_table}.{fk_col}' and '{parent_table}.{pk_col}'.")
        return True
