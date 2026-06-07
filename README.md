# Business CSV Insights App

![Project Cover](assets/project-cover.png)

A lightweight internal data app built to clean messy CSV files, check data quality and turn operational spreadsheets into useful business insights.

The app was designed for recurring files exported from sales, operations, CRM, marketplace or logistics systems, where teams need to validate data, fix common issues and prepare clean reporting files quickly.

## App Snapshot

- Uploads CSV files directly in the browser
- Loads a sample sales operations dataset when no file is uploaded
- Detects missing values, duplicate rows and inconsistent text fields
- Applies cleaning rules without editing spreadsheets manually
- Generates sales and operational metrics
- Exports cleaned CSV and Excel files

## Preview

![Dashboard Preview](assets/dashboard-preview.png)

## Data Quality Results

Using the included sample dataset:

| Metric | Before Cleaning | After Cleaning |
|---|---:|---:|
| Rows | 32 | 30 |
| Missing Values | 13 | 0 |
| Duplicate Rows | 2 | 0 |
| Total Sales | $8,925 | $8,855 |

## What the App Handles

- Duplicate records
- Missing numeric values
- Missing text fields
- Inconsistent status values
- Irregular column names
- Date parsing issues
- CSV-to-reporting preparation

## Business Output

The cleaned dataset can be used for:

- Sales reporting
- Operational performance review
- Payment status monitoring
- Delivery status tracking
- Regional sales analysis
- Product category analysis
- Monthly trend analysis

## App Views

The interface includes:

- Data quality overview
- Cleaning controls
- Before vs after summary
- Sales KPI dashboard
- Operational charts
- Original and cleaned data preview
- Downloadable CSV and Excel outputs

## Built With

Python, Streamlit, Pandas, Plotly, OpenPyXL, CSV and Excel exports.

## Repository Contents

```
business-csv-insights-app/
├── app.py
├── assets/
├── sample_data/
├── src/
├── data/
├── README.md
└── requirements.txt
```

## Notes

The app runs locally as a Streamlit application and uses the included sample dataset for demonstration. Users can upload their own CSV files directly through the interface.
