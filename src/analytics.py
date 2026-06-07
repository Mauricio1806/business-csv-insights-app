import pandas as pd
from utils import get_logger

logger = get_logger("analytics")

def find_column_by_keywords(df: pd.DataFrame, keywords: list[str]) -> str:
    """
    Finds the best matching column in the DataFrame that contains any of the keywords in its name.
    """
    # 1. Try exact match (case-insensitive)
    for col in df.columns:
        col_lower = str(col).lower()
        if col_lower in keywords:
            return col
            
    # 2. Try cleaned exact match (removing spaces and underscores)
    for col in df.columns:
        col_clean = str(col).lower().replace("_", "").replace(" ", "")
        for kw in keywords:
            kw_clean = kw.lower().replace("_", "").replace(" ", "")
            if col_clean == kw_clean:
                return col
                
    # 3. Partial match, excluding obvious false positives based on keywords
    is_sales_search = any(kw in ["sales_amount", "sales", "revenue", "amount"] for kw in keywords)
    is_order_search = any(kw in ["order_id", "order"] for kw in keywords)
    
    for col in df.columns:
        col_lower = str(col).lower()
        
        # Exclude false positives for sales search
        if is_sales_search:
            if "channel" in col_lower or "rep" in col_lower or "date" in col_lower:
                continue
                
        # Exclude false positives for order search
        if is_order_search:
            if "date" in col_lower or "amount" in col_lower or "rep" in col_lower:
                continue
                
        if any(kw in col_lower for kw in keywords):
            return col
            
    # 4. Final fallback (any partial match)
    for col in df.columns:
        col_lower = str(col).lower()
        if any(kw in col_lower for kw in keywords):
            return col
            
    return None

def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Computes high-level business metrics.
    """
    sales_col = find_column_by_keywords(df, ["sales_amount", "sales", "amount", "revenue"])
    order_col = find_column_by_keywords(df, ["order_id", "id", "order"])
    price_col = find_column_by_keywords(df, ["unit_price", "price"])
    qty_col = find_column_by_keywords(df, ["quantity", "qty"])
    
    # 1. Total Sales
    total_sales = 0.0
    if sales_col:
        total_sales = float(df[sales_col].sum())
    elif qty_col and price_col:
        total_sales = float((df[qty_col] * df[price_col]).sum())
        
    # 2. Total Orders
    total_orders = len(df)
    if order_col:
        total_orders = int(df[order_col].nunique())
        
    # 3. Average Order Value (AOV)
    avg_order_value = 0.0
    if total_orders > 0:
        if sales_col:
            # Group by order to get order value if order_id is present
            if order_col:
                order_totals = df.groupby(order_col)[sales_col].sum()
                avg_order_value = float(order_totals.mean())
            else:
                avg_order_value = float(df[sales_col].mean())
        elif qty_col and price_col:
            df['temp_sales'] = df[qty_col] * df[price_col]
            if order_col:
                order_totals = df.groupby(order_col)['temp_sales'].sum()
                avg_order_value = float(order_totals.mean())
            else:
                avg_order_value = float(df['temp_sales'].mean())
                
    return {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "avg_order_value": avg_order_value
    }

def get_categorical_breakdowns(df: pd.DataFrame) -> dict:
    """
    Computes aggregations for regions, product categories, channels, and statuses.
    """
    sales_col = find_column_by_keywords(df, ["sales_amount", "sales", "amount", "revenue"])
    region_col = find_column_by_keywords(df, ["region", "location", "territory"])
    cat_col = find_column_by_keywords(df, ["category", "product_category", "prod_cat"])
    chan_col = find_column_by_keywords(df, ["sales_channel", "channel", "source"])
    pay_col = find_column_by_keywords(df, ["payment_status", "payment", "pay"])
    del_col = find_column_by_keywords(df, ["delivery_status", "delivery", "status"])
    
    breakdowns = {}
    
    # helper for groupby sum
    def get_sales_sum(col_name):
        if col_name and sales_col:
            # Drop null values in categorical column
            clean_df = df.dropna(subset=[col_name])
            return clean_df.groupby(col_name)[sales_col].sum().reset_index().sort_values(by=sales_col, ascending=False)
        return pd.DataFrame()

    # helper for counts
    def get_value_counts(col_name):
        if col_name:
            return df[col_name].value_counts().reset_index().rename(columns={"count": "count", "index": col_name})
        return pd.DataFrame()

    breakdowns["sales_by_region"] = get_sales_sum(region_col)
    breakdowns["sales_by_category"] = get_sales_sum(cat_col)
    breakdowns["sales_by_channel"] = get_sales_sum(chan_col)
    
    breakdowns["payment_status_dist"] = get_value_counts(pay_col)
    breakdowns["delivery_status_dist"] = get_value_counts(del_col)
    
    # Save standard column names for easy plotly binding
    for key in ["sales_by_region", "sales_by_category", "sales_by_channel"]:
        if not breakdowns[key].empty:
            breakdowns[key].columns = ["dimension", "sales"]
            
    for key in ["payment_status_dist", "delivery_status_dist"]:
        if not breakdowns[key].empty:
            # In pandas 2.0+ value_counts().reset_index() returns columns: [index_col, 'count']
            # Let's standardize the column names
            breakdowns[key].columns = ["status", "count"]

    return breakdowns

def get_monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes monthly sales trend if a date column is available.
    """
    date_col = find_column_by_keywords(df, ["order_date", "date", "time", "created"])
    sales_col = find_column_by_keywords(df, ["sales_amount", "sales", "amount", "revenue"])
    
    if not date_col or not sales_col:
        return pd.DataFrame()
        
    try:
        # Create a copy and ensure dates are parsed
        trend_df = df.dropna(subset=[date_col, sales_col]).copy()
        
        # Check if date_col is already datetime. If not, try parsing
        if not pd.api.types.is_datetime64_any_dtype(trend_df[date_col]):
            trend_df[date_col] = pd.to_datetime(trend_df[date_col], errors='coerce', format='mixed')
            
        trend_df = trend_df.dropna(subset=[date_col])
        
        if trend_df.empty:
            return pd.DataFrame()
            
        # Group by Year-Month
        trend_df["month_period"] = trend_df[date_col].dt.to_period("M")
        monthly_sales = trend_df.groupby("month_period")[sales_col].sum().reset_index()
        
        # Convert period back to string for Plotly
        monthly_sales["month_str"] = monthly_sales["month_period"].astype(str)
        monthly_sales = monthly_sales.sort_values(by="month_period")
        
        return monthly_sales[["month_str", sales_col]].rename(columns={sales_col: "sales"})
    except Exception as e:
        logger.warning(f"Could not compute monthly sales trend: {e}")
        return pd.DataFrame()
