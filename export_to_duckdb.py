import psycopg2
import duckdb

# 1. Connect to local PostgreSQL and DuckDB
pg_conn = psycopg2.connect(
    host="localhost",
    database="TFL_Analysis",
    user="postgres",
    password="Faisal@123"  # Your PostgreSQL password
)
duck_conn = duckdb.connect("tfl_analysis.db")

# List of all views used in your Streamlit functions
views = [
    "v_line_volatility",
    "v_yearly_rankings",
    "v_line_summary",
    "v_network_benchmark",
    "v_perfomance_base",
    "v_anomaly_flags",
    "v_lch_category_contribution",
    "v_data_quality_report"
]

# 2. Copy data from each PostgreSQL view into DuckDB tables
for view in views:
    print(f"Exporting {view}...")
    cursor = pg_conn.cursor()
    cursor.execute(f"SELECT * FROM {view};")
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()

    # Convert to Pandas DataFrame for clean insertion into DuckDB
    import pandas as pd
    df = pd.DataFrame(data, columns=columns)

    # Write table to DuckDB
    duck_conn.execute(f"CREATE TABLE {view} AS SELECT * FROM df")

duck_conn.close()
pg_conn.close()
print("Done! 'tfl_analysis.db' file created successfully.")