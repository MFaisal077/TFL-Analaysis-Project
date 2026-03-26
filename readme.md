# London Underground Performance Dashboard

A full-stack data analytics application for exploring historical Transport for London (TfL) Underground performance data (2004/05 – 2016/17).

---

## Project Overview

This project solves the problem of **complex and hard-to-use TfL datasets** by transforming them into a structured, interactive dashboard.

The system:

* Cleans raw TfL CSV data
* Stores it in a PostgreSQL database
* Uses SQL for analysis
* Visualises insights through a Streamlit dashboard

The final result is an **interactive analytics tool** for exploring:

* Service reliability
* Customer satisfaction
* Disruption trends
* Performance comparisons across Underground lines

---

## System Architecture

```
Raw CSV Data → Python (Pandas) → PostgreSQL → SQL Queries → Streamlit → Plotly Dashboard
```

---

## Technologies Used

* Python
* Pandas
* PostgreSQL
* psycopg2
* Streamlit
* Plotly

---

## Project Structure

```
TFL-Analaysis-Project/
│
├── src/
│   ├── Dashboard.py          # Main Streamlit app
│   ├── data_loader.py       # SQL queries + DB connection
│   ├── data_cleaning.py     # ETL script (optional)
│   ├── styles.py            # Custom styling
│
├── tfl_analysis_dump.sql    # REQUIRED database dump
├── requirements.txt         # Python dependencies
├── README.md
```

---

## ⚙️ Setup Instructions (IMPORTANT)

Follow these steps exactly to run the project.

---

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Install PostgreSQL

Download PostgreSQL if not installed:

https://www.postgresql.org/download/

---

### 3. Create the Database

Open PostgreSQL and run:

```sql
CREATE DATABASE tfl_analysis;
```

---

### 4. Import the Database Dump

From the project folder:

```bash
psql -U postgres -d tfl_analysis < tfl_analysis_dump.sql
```

This will automatically create:

* All tables
* All data
* All analytical views

(The dashboard depends on these views.) 

---

### 5. Configure Database Password (ONLY STEP YOU MUST EDIT)

Open:

```
src/data_loader.py
```

Find this line:

```python
password="Faisal@123"
```

Replace it with your own PostgreSQL password:

```python
password="your_password_here"
```

This is required or the app will not connect to the database. 

---

### 6. Run the Application

```bash
streamlit run src/Dashboard.py
```

If that doesn’t work, use:

```bash
python -m streamlit run src/Dashboard.py
```

---

## How to Verify It Works

If setup is correct:

* The app opens in your browser
* The **Overview tab loads metrics**
* Charts display without errors
* No database errors appear

---

## Dashboard Features

### Overview

* Key performance indicators
* Most volatile / stable lines
* Network summary

### Line Explorer

* Compare multiple lines
* Track metrics over time

### Network Analysis

* Compare a line vs network average

### Yearly Rankings

* Rank lines by performance per year

### Year-over-Year Analysis

* Identify improvements and declines

### Anomaly Detection

* Detect unusual events using Z-scores

### Volatility Analysis

* Measure consistency of performance

### Root Cause Analysis

* Understand disruption causes

### Data Quality Report

* Identify missing or incomplete data

---

## Analytical Methods Used

* SQL aggregation
* Standard deviation (volatility)
* Z-score anomaly detection
* Year-over-year change analysis
* Ranking functions (window functions)

---

## Important Notes

* The database dump already contains **all processed data**
* You do **NOT need to run `data_cleaning.py`**
* That script is included only to demonstrate the ETL process 

---

## Limitations

* Data is yearly (not real-time)
* Some metrics contain missing values
* No predictive modelling (scope limitation)

---

## Future Improvements

* Real-time TfL API integration
* Machine learning predictions
* More granular (monthly/daily) data
* External data integration (weather, events)

---

## Author

Mohammad Faisal
BSc Computer Science – Final Year Project
City, University of London

Supervisor: Warren Fernando

---

## 📎 Data Source

Transport for London Open Data
https://tfl.gov.uk/info-for/open-data-users/open-data-policy

---

## Reproducibility Statement

This project is fully reproducible by:

1. Installing dependencies
2. Restoring the provided SQL dump
3. Updating the database password in one file
4. Running the Streamlit app

No additional configuration is required.
