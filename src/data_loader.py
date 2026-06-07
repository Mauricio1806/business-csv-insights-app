import os
import pandas as pd
from utils import get_logger

logger = get_logger("data_loader")

def load_csv(file_source) -> pd.DataFrame:
    """
    Loads a CSV file into a Pandas DataFrame.
    file_source can be a file path (str) or a file-like buffer from Streamlit upload.
    """
    try:
        # Load CSV
        df = pd.read_csv(file_source)
        logger.info(f"Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns.")
        return df
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        raise e

def get_dataset_profile(df: pd.DataFrame) -> dict:
    """
    Analyzes a DataFrame and returns metadata statistics.
    """
    if df is None or df.empty:
        return {}
        
    num_rows = len(df)
    num_cols = len(df.columns)
    total_cells = num_rows * num_cols
    
    missing_cells = int(df.isnull().sum().sum())
    missing_pct = (missing_cells / total_cells * 100) if total_cells > 0 else 0.0
    
    duplicate_rows = int(df.duplicated().sum())
    
    # Analyze column types
    numeric_cols = list(df.select_dtypes(include=['number']).columns)
    datetime_cols = list(df.select_dtypes(include=['datetime', 'datetimetz']).columns)
    
    # Categorical/text columns (excluding numeric/datetime)
    categorical_cols = [col for col in df.columns if col not in numeric_cols and col not in datetime_cols]
    
    return {
        "num_rows": num_rows,
        "num_cols": num_cols,
        "missing_cells": missing_cells,
        "missing_pct": missing_pct,
        "duplicate_rows": duplicate_rows,
        "numeric_cols_count": len(numeric_cols),
        "categorical_cols_count": len(categorical_cols),
        "columns_list": list(df.columns),
        "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
    }
