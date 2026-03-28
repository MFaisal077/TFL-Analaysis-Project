# London Underground Performance Dashboard

A full-stack data analytics web application analyzing 13 years of TfL Underground performance data (2004/05 – 2016/17) with interactive visualizations and statistical insights.

---

## Quick Summary
- **What:** Interactive 10-tab Streamlit dashboard  
- **Setup time:** 10–15 minutes  
- **Main file:** `src/Dashboard.py`  
- **Required file:** `tfl_analysis_dump.sql`

---

## Setup Instructions (For Markers)

### Step 1: Create the Database
```bash
psql -U postgres -c "CREATE DATABASE TFL_Analysis;"

```


### Step 2: Restore the Database Dump
```bash 
psql -U postgres -d TFL_Analysis -f tfl_analysis_dump.sql
(Or use pgAdmin → Restore)
```

### Step 3: Run the Dashboard
```bash
pip install -r requirements.txt
streamlit run src/Dashboard.py

```

Before running, open src/data_loader.py and replace:

password="your_postgres_password"

with your local PostgreSQL password.

Optional: Re-run ETL from Raw CSVs

```bash
python src/data_cleaning.py
(Only needed if you want to recreate the tables from scratch — not required because the dump already contains all data.)

Project Structure
```bash TFL-ANALYSIS-PROJECT/
├── src/
│   ├── Dashboard.py              # Main application (run this)
│   ├── data_loader.py
│   ├── data_cleaning.py          # Optional ETL script
│   └── styles.py
├── requirements.txt
├── tfl_analysis_dump.sql         # Complete database dump (REQUIRED)
├── README.md
│
├── data_raw/                     # Raw CSV files                   

Dashboard Features

Overview – Network summary and KPIs
Line Explorer – Compare multiple lines over time
Network Analysis – Line vs network average
Yearly Rankings – Performance rankings per year
YoY Analysis – Year-over-year changes
Anomalies – Z-score outlier detection
Volatility – Performance stability
Root Cause Analysis – Disruption categories
Data Quality Report – Missing data transparency
TfL Insights – Real-world event correlation


Author
Mohammad Faisal
BSc Computer Science – Final Year Project
City, University of London
Supervisor: Warren Fernando
Date: 26 March 2026
Data Source
Transport for London Open Data: https://tfl.gov.uk/info-for/open-data-users/open-data-policy

Reproducibility:
Fully self-contained. Restore the dump and run src/Dashboard.py. No external services required.