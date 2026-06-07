import logging
import sys
import streamlit as st

def get_logger(name: str) -> logging.Logger:
    """
    Sets up a clean, professional logger that writes to stdout.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def inject_custom_css():
    """
    Injects custom corporate CSS styling to give the app a polished internal tool feel.
    """
    st.markdown("""
    <style>
        /* Modern corporate color tones */
        :root {
            --primary: #0f766e; /* Dark Teal */
            --primary-light: #ccfbf1;
            --accent: #b45309; /* Warm Amber */
            --bg-card: #ffffff;
            --bg-page: #f8fafc;
        }
        
        /* Heading Styles */
        .app-title {
            color: #0f172a;
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            font-size: 2.3rem;
            margin-bottom: 0.1rem;
        }
        .app-subtitle {
            color: #64748b;
            font-family: 'Inter', sans-serif;
            font-size: 1.05rem;
            margin-bottom: 1.5rem;
        }
        
        /* Metric KPI Card styling */
        .metric-card {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 18px;
            box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
            border-left: 5px solid #0f766e;
            margin-bottom: 12px;
        }
        
        .metric-card.accent {
            border-left-color: #b45309;
        }
        
        .metric-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 2px;
        }
        .metric-subtext {
            font-size: 0.72rem;
            color: #94a3b8;
        }
        
        /* Divider line */
        .ui-divider {
            height: 1px;
            background-color: #e2e8f0;
            margin: 1.2rem 0;
        }
        
        /* Table / Dataframes styling */
        .dataframe {
            border-radius: 6px;
        }
    </style>
    """, unsafe_allow_html=True)
