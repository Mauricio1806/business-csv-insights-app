import os
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Import backend modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from utils import inject_custom_css, get_logger
from data_loader import load_csv, get_dataset_profile
from data_cleaner import clean_data
from analytics import compute_kpis, get_categorical_breakdowns, get_monthly_sales_trend

# Page configuration
st.set_page_config(
    page_title="Business CSV Insights & Data Cleaning App",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom corporate CSS style
inject_custom_css()

# Session State initialization
if 'raw_df' not in st.session_state:
    st.session_state['raw_df'] = None
if 'cleaned_df' not in st.session_state:
    st.session_state['cleaned_df'] = None
if 'clean_summary' not in st.session_state:
    st.session_state['clean_summary'] = None
if 'file_name' not in st.session_state:
    st.session_state['file_name'] = ""
if 'data_source' not in st.session_state:
    st.session_state['data_source'] = "None"

# Sidebar file upload and reset
st.sidebar.image("https://img.icons8.com/clouds/100/data-configuration.png", width=75)
st.sidebar.title("Data Source")

uploaded_file = st.sidebar.file_uploader("Upload Business CSV Export", type=["csv"])

# Define default sample path
sample_csv_path = os.path.join("sample_data", "sample_sales_operations.csv")

# Determine which data to load
if uploaded_file is not None:
    # Check if a new file was uploaded
    if st.session_state['file_name'] != uploaded_file.name:
        st.session_state['raw_df'] = load_csv(uploaded_file)
        st.session_state['cleaned_df'] = None
        st.session_state['clean_summary'] = None
        st.session_state['file_name'] = uploaded_file.name
        st.session_state['data_source'] = "Uploaded File"
else:
    # Fallback to sample data
    if st.session_state['raw_df'] is None or st.session_state['data_source'] == "Uploaded File":
        if os.path.exists(sample_csv_path):
            st.session_state['raw_df'] = load_csv(sample_csv_path)
            st.session_state['cleaned_df'] = None
            st.session_state['clean_summary'] = None
            st.session_state['file_name'] = "sample_sales_operations.csv"
            st.session_state['data_source'] = "Sample Dataset"

# Load the working dataset
df_working = st.session_state['raw_df']
profile = get_dataset_profile(df_working)

# ----------------- MAIN TITLE & SUBTITLE -----------------
st.markdown('<div class="app-title">Business CSV Insights & Data Cleaning App</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Upload messy CSV files, detect data quality issues, clean the dataset and generate operational insights.</div>', unsafe_allow_html=True)

# Status notification banner
if st.session_state['data_source'] == "Uploaded File":
    st.success(f"📂 **Active Dataset**: `{st.session_state['file_name']}` (User Uploaded)")
else:
    st.info(f"💡 **Active Dataset**: `{st.session_state['file_name']}` (Loaded automatically as no custom file was uploaded. Upload your own CSV in the sidebar.)")

# ----------------- SIDEBAR CLEANING OPTIONS -----------------
st.sidebar.markdown("---")
st.sidebar.title("Data Cleaning Rules")

clean_opts = {
    "remove_duplicates": st.sidebar.checkbox("Remove Duplicate Rows", value=True),
    "standardize_columns": st.sidebar.checkbox("Standardize Column Headers", value=True),
    "trim_text": st.sidebar.checkbox("Trim Text Fields", value=True),
    "standardize_payment": st.sidebar.checkbox("Standardize Payment Status Text", value=True),
    "parse_dates": st.sidebar.checkbox("Standardize Dates (Mixed Formats)", value=True),
    "fill_numeric_median": st.sidebar.checkbox("Fill Empty Numeric with Median", value=True),
    "fill_text_unknown": st.sidebar.checkbox("Fill Empty Text with 'Unknown'", value=True)
}

if st.sidebar.button("🧼 Execute Cleaning Pipeline", use_container_width=True):
    with st.spinner("Processing data transformation..."):
        cleaned_data, summary = clean_data(df_working, clean_opts)
        st.session_state['cleaned_df'] = cleaned_data
        st.session_state['clean_summary'] = summary
        st.sidebar.success("Dataset successfully cleaned!")

# ----------------- TABS CREATION -----------------
tab_overview, tab_quality, tab_cleaning, tab_insights, tab_explorer = st.tabs([
    "🏠 Overview",
    "⚠️ Data Quality Scan",
    "🧼 Cleaning Panel",
    "📊 Business Insights",
    "🔍 Data Explorer"
])

# ----------------- TAB 1: OVERVIEW -----------------
with tab_overview:
    col_text, col_meta = st.columns([2, 1])
    
    with col_text:
        st.markdown("""
        ### About the Application
        This operational utility helps business teams automate the process of cleaning, checking, and reporting on raw CSV data exports. Large database systems (CRMs, ERPs, inventory portals, payment gateways) often output files with syntax differences, duplicate entries, missing metrics, or disjointed dates.
        
        #### Core Capabilities:
        * **Automated Data Quality Audit**: Instantly spots row anomalies, empty cells, and type mismatches.
        * **Standardized Cleansing Workflow**: Click-and-run filters to transform inconsistencies into database-friendly formats.
        * **Business-Ready Visualizations**: Translates tables into interactive KPI cards and sales metrics breakdown.
        * **Multi-Format Export**: Download reporting files in clean CSV and multi-tab styled Excel spreadsheets.
        """)
        
    with col_meta:
        st.markdown("### Active Dataset Profile")
        if profile:
            st.markdown(f"""
            * **File Name**: `{st.session_state['file_name']}`
            * **Total Records (Rows)**: `{profile['num_rows']:,}`
            * **Parameters (Columns)**: `{profile['num_cols']}`
            * **Null Data Cells**: `{profile['missing_cells']:,} ({profile['missing_pct']:.2f}% of data)`
            * **Duplicate Rows**: `{profile['duplicate_rows']}`
            * **Numeric Fields**: `{profile['numeric_cols_count']}`
            * **Categorical Fields**: `{profile['categorical_cols_count']}`
            """)

    st.markdown('<div class="ui-divider"></div>', unsafe_allow_html=True)
    
    # Showcase cards
    card_col1, card_col2, card_col3 = st.columns(3)
    with card_col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">1. Upload File</div>
            <div class="metric-value">Drag & Drop</div>
            <div class="metric-subtext">Upload raw reports directly in the sidebar panel.</div>
        </div>
        """, unsafe_allow_html=True)
    with card_col2:
        st.markdown("""
        <div class="metric-card accent">
            <div class="metric-label">2. Run Cleaning</div>
            <div class="metric-value">Select & Apply</div>
            <div class="metric-subtext">Customize rules in the sidebar to patch dates, casings, and duplicates.</div>
        </div>
        """, unsafe_allow_html=True)
    with card_col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">3. Export Report</div>
            <div class="metric-value">CSV / Excel</div>
            <div class="metric-subtext">Download cleanly formatted reporting sheets instantly.</div>
        </div>
        """, unsafe_allow_html=True)

# ----------------- TAB 2: DATA QUALITY SCAN -----------------
with tab_quality:
    st.markdown("### Automated Data Quality Analysis")
    st.write("Scan metrics identify syntax and completeness gaps across all dataset columns.")
    
    # Quality Overview Cards
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    with q_col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #0f766e;">
            <div class="metric-label">Completeness Rating</div>
            <div class="metric-value">{100 - profile.get('missing_pct', 0.0):.1f}%</div>
            <div class="metric-subtext">Non-null cells vs total space</div>
        </div>
        """, unsafe_allow_html=True)
        
    with q_col2:
        dup_color = "#ef4444" if profile.get('duplicate_rows', 0) > 0 else "#0f766e"
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: {dup_color};">
            <div class="metric-label">Duplicate Rows</div>
            <div class="metric-value">{profile.get('duplicate_rows', 0)}</div>
            <div class="metric-subtext">Identical records detected</div>
        </div>
        """, unsafe_allow_html=True)
        
    with q_col3:
        null_color = "#f59e0b" if profile.get('missing_cells', 0) > 0 else "#0f766e"
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: {null_color};">
            <div class="metric-label">Missing Values</div>
            <div class="metric-value">{profile.get('missing_cells', 0):,}</div>
            <div class="metric-subtext">Blank or null data entries</div>
        </div>
        """, unsafe_allow_html=True)
        
    with q_col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #3b82f6;">
            <div class="metric-label">Total Cells</div>
            <div class="metric-value">{profile.get('num_rows', 0) * profile.get('num_cols', 0):,}</div>
            <div class="metric-subtext">Rows multiplied by Columns</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="ui-divider"></div>', unsafe_allow_html=True)

    # Detailed Column Breakdown
    col_break_left, col_break_right = st.columns([1, 1])
    
    with col_break_left:
        st.markdown("#### Column Profiling & Null Counts")
        # Build null check table
        null_data = []
        for col in df_working.columns:
            null_count = int(df_working[col].isnull().sum())
            null_pct = (null_count / len(df_working) * 100) if len(df_working) > 0 else 0.0
            null_data.append({
                "Column Name": col,
                "Data Type": str(df_working[col].dtype),
                "Missing Cells": null_count,
                "Missing %": f"{null_pct:.1f}%"
            })
        st.dataframe(pd.DataFrame(null_data), use_container_width=True, hide_index=True)
        
    with col_break_right:
        st.markdown("#### Null Counts Visual Distribution")
        # Null check visualization
        null_counts_df = df_working.isnull().sum().reset_index()
        null_counts_df.columns = ["Column", "Null Count"]
        null_counts_df = null_counts_df[null_counts_df["Null Count"] > 0]
        
        if not null_counts_df.empty:
            fig_nulls = px.bar(
                null_counts_df,
                x="Null Count",
                y="Column",
                orientation="h",
                color="Null Count",
                color_continuous_scale="Reds",
                labels={"Null Count": "Null Count", "Column": "Column Header"},
                height=350
            )
            fig_nulls.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=50, r=20, t=10, b=10),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_nulls, use_container_width=True)
        else:
            st.success("✅ **Clean Run**: No missing value cells detected in this file.")

# ----------------- TAB 3: CLEANING PANEL -----------------
with tab_cleaning:
    st.markdown("### Operational Cleaning Workbench")
    st.write("Trigger data transformations via the sidebar panel. Below is the structural execution validation report.")
    
    if st.session_state['cleaned_df'] is None:
        st.info("💡 **Awaiting Pipeline Execution**: Configure settings in the sidebar and click 'Execute Cleaning Pipeline' to run.")
    else:
        summary = st.session_state['clean_summary']
        cleaned_df = st.session_state['cleaned_df']
        
        # Before vs After Grid
        s_col1, s_col2, s_col3 = st.columns(3)
        
        with s_col1:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #0f766e;">
                <div class="metric-label">Records (Rows)</div>
                <div class="metric-value">{summary['rows_before']} ➔ {summary['rows_after']}</div>
                <div class="metric-subtext">Duplicate row removal validation</div>
            </div>
            """, unsafe_allow_html=True)
            
        with s_col2:
            null_after_color = "#ef4444" if summary['nulls_after'] > 0 else "#0f766e"
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {null_after_color};">
                <div class="metric-label">Blank Cells</div>
                <div class="metric-value">{summary['nulls_before']} ➔ {summary['nulls_after']}</div>
                <div class="metric-subtext">Imputation validation report</div>
            </div>
            """, unsafe_allow_html=True)
            
        with s_col3:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #0f766e;">
                <div class="metric-label">Duplicate Rows</div>
                <div class="metric-value">{summary['duplicates_before']} ➔ {summary['duplicates_after']}</div>
                <div class="metric-subtext">Structural duplicates count</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Transformations Applied")
        for act in summary['actions_taken']:
            st.markdown(f"- ✅ {act}")
            
        st.markdown('<div class="ui-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### Export Cleaned Deliverable Files")
        
        # Prepare exports
        # CSV Buffer
        csv_buffer = cleaned_df.to_csv(index=False, encoding='utf-8')
        
        # Excel Buffer
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            cleaned_df.to_excel(writer, index=False, sheet_name="Cleaned Data")
        excel_bytes = excel_buffer.getvalue()
        
        ex_col1, ex_col2 = st.columns(2)
        with ex_col1:
            st.download_button(
                label="📥 Download Clean CSV Dataset",
                data=csv_buffer,
                file_name=f"cleaned_{st.session_state['file_name']}",
                mime="text/csv",
                use_container_width=True
            )
        with ex_col2:
            st.download_button(
                label="📥 Download Styled Excel sheet",
                data=excel_bytes,
                file_name=f"cleaned_{st.session_state['file_name'].replace('.csv', '.xlsx')}",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# ----------------- TAB 4: BUSINESS INSIGHTS -----------------
with tab_insights:
    st.markdown("### Operational Business Insights")
    st.write("Aggregations and visualizations compiled from the active dataset. Note: Charts perform best on cleaned columns.")
    
    # We choose cleaned_df if available, otherwise fallback to raw_df
    df_analytic = st.session_state['cleaned_df'] if st.session_state['cleaned_df'] is not None else df_working
    
    # Check if df_analytic is cleaned. If not, give warning that data is messy
    if st.session_state['cleaned_df'] is None:
        st.warning("⚠️ **Viewing Raw (Messy) Data Insights**: Transformations have not been applied. Run the cleaning panel to resolve nulls and date discrepancies first.")
        
    kpis = compute_kpis(df_analytic)
    
    # Display analytics KPIs
    bi_col1, bi_col2, bi_col3 = st.columns(3)
    with bi_col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #0f766e;">
            <div class="metric-label">Total Revenue (Sales)</div>
            <div class="metric-value">${kpis['total_sales']:,.2f}</div>
            <div class="metric-subtext">Sum of sales_amount</div>
        </div>
        """, unsafe_allow_html=True)
    with bi_col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #b45309;">
            <div class="metric-label">Average Order Value</div>
            <div class="metric-value">${kpis['avg_order_value']:,.2f}</div>
            <div class="metric-subtext">Mean transaction value</div>
        </div>
        """, unsafe_allow_html=True)
    with bi_col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #2563eb;">
            <div class="metric-label">Total Transactions (Orders)</div>
            <div class="metric-value">{kpis['total_orders']:,}</div>
            <div class="metric-subtext">Unique order counts</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="ui-divider"></div>', unsafe_allow_html=True)

    breakdowns = get_categorical_breakdowns(df_analytic)
    
    # Row 1 charts
    ch_col1, ch_col2 = st.columns(2)
    
    with ch_col1:
        # Sales by Region
        df_reg = breakdowns.get("sales_by_region", pd.DataFrame())
        if not df_reg.empty:
            fig_reg = px.bar(
                df_reg,
                x="sales",
                y="dimension",
                orientation="h",
                color="sales",
                color_continuous_scale="Viridis",
                title="Revenue Contribution by Market Region",
                labels={"sales": "Sales ($)", "dimension": "Region"},
                height=350
            )
            fig_reg.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                margin=dict(l=100, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_reg, use_container_width=True)
        else:
            st.info("No region column identified in dataset.")
            
    with ch_col2:
        # Sales by Category
        df_cat = breakdowns.get("sales_by_category", pd.DataFrame())
        if not df_cat.empty:
            fig_cat = px.bar(
                df_cat,
                x="sales",
                y="dimension",
                orientation="h",
                color="sales",
                color_continuous_scale="Tealgrn",
                title="Revenue Contribution by Product Category",
                labels={"sales": "Sales ($)", "dimension": "Product Category"},
                height=350
            )
            fig_cat.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                margin=dict(l=100, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No product category column identified in dataset.")

    # Row 2 charts
    ch_col3, ch_col4 = st.columns(2)
    
    with ch_col3:
        # Sales Channel Distribution
        df_chan = breakdowns.get("sales_by_channel", pd.DataFrame())
        if not df_chan.empty:
            fig_chan = px.pie(
                df_chan,
                values="sales",
                names="dimension",
                title="Revenue Share by Sales Channel",
                color_discrete_sequence=px.colors.qualitative.Prism,
                height=350
            )
            fig_chan.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=30, r=30, t=40, b=40)
            )
            st.plotly_chart(fig_chan, use_container_width=True)
        else:
            st.info("No sales channel column identified.")
            
    with ch_col4:
        # Monthly Sales Trend
        df_trend = get_monthly_sales_trend(df_analytic)
        if not df_trend.empty:
            fig_trend = px.line(
                df_trend,
                x="month_str",
                y="sales",
                markers=True,
                title="Monthly Revenue Trend Analysis",
                labels={"sales": "Sales Revenue ($)", "month_str": "Reporting Month"},
                height=350
            )
            fig_trend.update_layout(
                plot_bgcolor="rgba(240,244,248,0.5)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=50, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No date/time or sales metric found to build monthly sales trend.")

    # Row 3: Status breakdowns
    ch_col5, ch_col6 = st.columns(2)
    with ch_col5:
        # Payment Status
        df_pay = breakdowns.get("payment_status_dist", pd.DataFrame())
        if not df_pay.empty:
            fig_pay = px.bar(
                df_pay,
                x="status",
                y="count",
                color="status",
                title="Transaction Casing - Payment Status Distribution",
                labels={"status": "Status Casing", "count": "Order Count"},
                height=350
            )
            fig_pay.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(l=50, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_pay, use_container_width=True)
        else:
            st.info("No payment status column found.")
            
    with ch_col6:
        # Delivery Status
        df_del = breakdowns.get("delivery_status_dist", pd.DataFrame())
        if not df_del.empty:
            fig_del = px.bar(
                df_del,
                x="status",
                y="count",
                color="status",
                color_discrete_sequence=px.colors.qualitative.Safe,
                title="Fulfillment Casing - Delivery Status Distribution",
                labels={"status": "Status", "count": "Order Count"},
                height=350
            )
            fig_del.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(l=50, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_del, use_container_width=True)
        else:
            st.info("No delivery status column found.")

# ----------------- TAB 5: DATA EXPLORER -----------------
with tab_explorer:
    st.markdown("### Interactive Dataset Explorer")
    st.write("Browse and audit both the raw original file and the post-pipeline clean data.")
    
    exp_col1, exp_col2 = st.columns(2)
    
    with exp_col1:
        st.markdown("#### Original (Raw) Data Preview")
        st.write("First 15 records as uploaded by user/system:")
        st.dataframe(df_working.head(15), use_container_width=True)
        
    with exp_col2:
        st.markdown("#### Post-Pipeline (Cleaned) Data Preview")
        if st.session_state['cleaned_df'] is None:
            st.warning("⚠️ **Awaiting Cleaning**: Process the dataset in the Cleaning Panel to view post-pipeline output.")
        else:
            st.write("First 15 records after pipeline execution:")
            st.dataframe(st.session_state['cleaned_df'].head(15), use_container_width=True)
