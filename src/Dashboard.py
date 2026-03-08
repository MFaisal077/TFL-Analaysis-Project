import streamlit as st
import pandas as pd
import psycopg2

st.set_page_config(layout="wide", page_title="TFL Dashboard")

@st.cache_data
def get_most_volatile_line():
    conn = psycopg2.connect(
        host="localhost",
        database="TFL_Analysis",
        user="postgres",
        password="Faisal@123"
    )

    query = """
        SELECT line, stddev_samp
        FROM v_line_volatility
        ORDER BY stddev_samp DESC
        LIMIT 1;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    line = df.iloc[0]["line"]
    score = round(df.iloc[0]["stddev_samp"], 2)

    return line, score


# PAGE HEADER
st.title("London Underground Performance Dashboard")
st.write(
    "A historical analysis of reliability, disruption, and customer experience across Underground lines"
)

# GET DATA
most_volatile_line, volatility_score = get_most_volatile_line()

# KPI ROW
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Most Volatile Line",
        value=most_volatile_line
    )
    st.caption(f"Volatility score: {volatility_score}")

with col2:
    st.metric("Best Satisfaction Line", "TBD")

with col3:
    st.metric("Worst Disruption Line", "TBD")


# SIDEBAR
with st.sidebar:
    st.title("Dashboard Controls")