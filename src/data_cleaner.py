import pandas as pd
import numpy as np
from utils import get_logger

logger = get_logger("data_cleaner")

def clean_data(df: pd.DataFrame, options: dict) -> tuple[pd.DataFrame, dict]:
    """
    Cleans the input DataFrame according to selected options.
    Returns:
        cleaned_df: pd.DataFrame
        before_vs_after: dict (containing metric summaries)
    """
    # Create copy of dataframe to preserve original
    cleaned_df = df.copy()
    
    # Store initial metrics
    initial_rows = len(df)
    initial_nulls = int(df.isnull().sum().sum())
    initial_duplicates = int(df.duplicated().sum())
    
    # Track actions taken
    actions = []
    
    # 1. Standardize column names (convert to snake_case, strip whitespace)
    if options.get("standardize_columns"):
        original_cols = list(cleaned_df.columns)
        new_cols = []
        for col in original_cols:
            clean_col = str(col).strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")
            new_cols.append(clean_col)
        cleaned_df.columns = new_cols
        actions.append(f"Standardized columns: {dict(zip(original_cols, new_cols))}")
        logger.info("Standardized column headers.")
        
    # Check if headers are cleaned to refer to columns in snake_case or original
    # We will compute columns lists dynamically
    cols_to_check = cleaned_df.columns
    
    # Helper to find column regardless of snake_case or original name
    def find_col_by_pattern(pattern):
        for c in cleaned_df.columns:
            if pattern in str(c).lower():
                return c
        return None

    # 2. Remove duplicates
    if options.get("remove_duplicates"):
        cleaned_df = cleaned_df.drop_duplicates()
        rows_removed = initial_rows - len(cleaned_df)
        actions.append(f"Removed duplicates: {rows_removed} rows deleted.")
        logger.info(f"Removed {rows_removed} duplicate rows.")

    # 3. Trim text fields
    if options.get("trim_text"):
        text_cols = cleaned_df.select_dtypes(include=['object', 'string']).columns
        for col in text_cols:
            cleaned_df[col] = cleaned_df[col].apply(lambda x: str(x).strip() if pd.notnull(x) else x)
        actions.append("Trimmed whitespace from all text columns.")
        logger.info("Trimmed text columns.")

    # 4. Standardize payment status text
    if options.get("standardize_payment"):
        # Look for payment status column
        pay_col = find_col_by_pattern("payment_status") or find_col_by_pattern("payment")
        if pay_col and pay_col in cleaned_df.columns:
            cleaned_df[pay_col] = cleaned_df[pay_col].apply(
                lambda x: str(x).strip().capitalize() if pd.notnull(x) else x
            )
            actions.append(f"Standardized casing for column: '{pay_col}' (e.g. 'Paid', 'Pending').")
            logger.info(f"Standardized payment status casing in '{pay_col}'.")

    # 5. Parse date columns
    if options.get("parse_dates"):
        date_cols = [c for c in cleaned_df.columns if "date" in str(c).lower() or "time" in str(c).lower()]
        parsed_count = 0
        for col in date_cols:
            try:
                # Use mixed format parsing in Pandas 2.0+
                cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce', format='mixed')
                parsed_count += 1
            except Exception:
                try:
                    # Fallback
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                    parsed_count += 1
                except Exception as ex:
                    logger.warning(f"Could not parse dates for column '{col}': {ex}")
        if parsed_count > 0:
            actions.append(f"Parsed and standardized {parsed_count} date column(s).")
            logger.info(f"Parsed {parsed_count} date columns.")

    # 6. Fill missing numeric values and recalculate sales_amount
    qty_col = find_col_by_pattern("quantity") or find_col_by_pattern("qty")
    price_col = find_col_by_pattern("unit_price") or find_col_by_pattern("price")
    sales_col = find_col_by_pattern("sales_amount") or find_col_by_pattern("sales")
    
    if options.get("fill_numeric_median"):
        numeric_cols = cleaned_df.select_dtypes(include=['number']).columns
        filled_cols = []
        
        # 6a. Fill quantity and unit price with median first
        for col in [qty_col, price_col]:
            if col and col in numeric_cols and cleaned_df[col].isnull().any():
                median_val = cleaned_df[col].median()
                if pd.isna(median_val):
                    median_val = 0.0
                cleaned_df[col] = cleaned_df[col].fillna(median_val)
                filled_cols.append(col)
                
        # 6b. Recalculate missing sales amounts now that quantity and unit prices are fully populated
        if qty_col and price_col and sales_col:
            mask = cleaned_df[sales_col].isnull() & cleaned_df[qty_col].notnull() & cleaned_df[price_col].notnull()
            if mask.any():
                cleaned_df.loc[mask, sales_col] = cleaned_df.loc[mask, qty_col] * cleaned_df.loc[mask, price_col]
                actions.append(f"Recalculated missing sales amount fields in '{sales_col}' from quantities and unit prices.")
                logger.info(f"Recalculated missing sales amounts in '{sales_col}'.")
                
        # 6c. Fill remaining numeric columns (including sales_amount if still missing) with median
        for col in numeric_cols:
            if col not in filled_cols:
                if cleaned_df[col].isnull().any():
                    median_val = cleaned_df[col].median()
                    if pd.isna(median_val):
                        median_val = 0.0
                    cleaned_df[col] = cleaned_df[col].fillna(median_val)
                    filled_cols.append(col)
                    
        if filled_cols:
            actions.append(f"Filled missing numeric values in {filled_cols} with column median.")
            logger.info(f"Filled missing numeric values with medians in: {filled_cols}")
            
    else:
        # If fill_numeric_median is False, we still try to recalculate sales_amount for rows where quantity and unit_price are already present
        if qty_col and price_col and sales_col:
            mask = cleaned_df[sales_col].isnull() & cleaned_df[qty_col].notnull() & cleaned_df[price_col].notnull()
            if mask.any():
                cleaned_df.loc[mask, sales_col] = cleaned_df.loc[mask, qty_col] * cleaned_df.loc[mask, price_col]
                actions.append(f"Recalculated missing sales amount fields in '{sales_col}' from quantities and unit prices.")
                logger.info(f"Recalculated missing sales amounts in '{sales_col}'.")

    # 7. Fill missing text values with "Unknown"
    if options.get("fill_text_unknown"):
        # We fill missing categorical/text columns with "Unknown"
        # Avoid filling date columns that were parsed (since filling with "Unknown" converts column type back to string)
        exclude_cols = cleaned_df.select_dtypes(include=['datetime', 'datetimetz', 'number']).columns
        categorical_cols = [c for c in cleaned_df.columns if c not in exclude_cols]
        filled_cols = []
        for col in categorical_cols:
            if cleaned_df[col].isnull().any():
                cleaned_df[col] = cleaned_df[col].fillna("Unknown")
                filled_cols.append(col)
        if filled_cols:
            actions.append(f"Filled missing text values in {filled_cols} with 'Unknown'.")
            logger.info(f"Filled missing text values with 'Unknown' in: {filled_cols}")

    # Store final metrics
    final_rows = len(cleaned_df)
    final_nulls = int(cleaned_df.isnull().sum().sum())
    final_duplicates = int(cleaned_df.duplicated().sum())

    before_vs_after = {
        "rows_before": initial_rows,
        "rows_after": final_rows,
        "nulls_before": initial_nulls,
        "nulls_after": final_nulls,
        "duplicates_before": initial_duplicates,
        "duplicates_after": final_duplicates,
        "actions_taken": actions
    }
    
    return cleaned_df, before_vs_after
