# Automated KPI Reporting
A lightweight analytics tool that transforms raw sales data into structured revenue insights in seconds.

Upload a CSV file, select a reporting period (Daily, Weekly, Monthly, Yearly), and instantly generate:

Revenue aggregation by selected time grain

Key financial metrics

Revenue trend visualization

Exportable revenue report (CSV)

# Features

CSV ingestion (up to 200MB)

Automatic data validation

Revenue aggregation by time period

Key KPI metrics:

Total Revenue

Average Revenue

Peak Revenue

Median Revenue

Growth Rate

Revenue trend visualization

Downloadable revenue report

# Required Columns

Your CSV must include:

InvoiceDate

Quantity

UnitPrice

Revenue is calculated as:

Revenue = Quantity × UnitPrice

The application automatically validates required columns before processing.

# Data Processing Pipeline

Load CSV file

Validate required columns and clean data

Compute revenue metrics

Aggregate revenue by selected time grain

Generate report and visualization

# Example Output

Total Revenue

Average Revenue per Period

Peak Revenue

Growth Percentage

Time-based Revenue Trend

Exportable aggregated CSV report

# Tech Stack

Python

Pandas

Streamlit

Matplotlib / Plotly

# Installation (Local)
pip install -r requirements.txt

streamlit run app.py
