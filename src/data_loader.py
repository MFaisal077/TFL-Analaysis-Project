import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

@st.cache_data
def get_most_stable_line():
    conn = get_connection()
    query = """
        SELECT line, stddev_samp
        FROM v_line_volatility
        WHERE stddev_samp IS NOT NULL
        ORDER BY stddev_samp ASC
        LIMIT 1;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.iloc[0]["line"], round(df.iloc[0]["stddev_samp"], 2)


@st.cache_data
def get_yearly_rankings():
    conn = get_connection()
    query = """
        SELECT
            line,
            "year",
            lost_customer_hours,
            schedule_operated,
            customer_satisfaction,
            esc_avail,
            ejt,
            yoy_change,
            rank_lch_best,
            rank_schedule_best,
            rank_css_best
        FROM v_yearly_rankings
        ORDER BY "year", line;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def get_top_insight_lines():
    conn = get_connection()
    query = """
        SELECT
            line,
            avg_lch,
            avg_customer_satisfaction
        FROM v_line_summary
        WHERE avg_lch IS NOT NULL
        ORDER BY avg_lch DESC
        LIMIT 1;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return (
        df.iloc[0]["line"],
        round(df.iloc[0]["avg_lch"], 2),
        df.iloc[0]["avg_customer_satisfaction"]
    )

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="TFL_Analysis",
        user="postgres",
        password="Faisal@123"
    )

@st.cache_data
def get_network_benchmark():
    conn = get_connection()
    query = """
        SELECT
            line,
            "year",
            lost_customer_hours,
            schedule_operated,
            customer_satisfaction,
            esc_avail,
            ejt,
            network_avg_lch,
            network_avg_schedule,
            network_avg_css,
            network_avg_esc,
            network_avg_ejt
        FROM v_network_benchmark
        ORDER BY "year", line;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    df["year_label"] = df["year"]
    df["year"] = df["year"].str[:4].astype(int)
    return df


@st.cache_data
def get_most_volatile_line():
    conn = get_connection()
    query = """
        SELECT line, stddev_samp
        FROM v_line_volatility
        ORDER BY stddev_samp DESC
        LIMIT 1;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.iloc[0]["line"], round(df.iloc[0]["stddev_samp"], 2)


@st.cache_data
def get_best_satisfaction_line():
    conn = get_connection()
    query = """
        SELECT line, avg_customer_satisfaction
        FROM v_line_summary
        WHERE avg_customer_satisfaction IS NOT NULL
        ORDER BY avg_customer_satisfaction DESC
        LIMIT 1;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.iloc[0]["line"], round(df.iloc[0]["avg_customer_satisfaction"], 2)


@st.cache_data
def get_worst_disruption_line():
    conn = get_connection()
    query = """
        SELECT line, avg_lch
        FROM v_line_summary
        WHERE avg_lch IS NOT NULL
        ORDER BY avg_lch DESC
        LIMIT 1;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.iloc[0]["line"], round(df.iloc[0]["avg_lch"], 2)


@st.cache_data
def get_volatility_ranking():
    conn = get_connection()
    query = """
        SELECT line, stddev_samp
        FROM v_line_volatility
        ORDER BY stddev_samp DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def get_line_metrics():
    conn = get_connection()
    query = """
        SELECT
            line,
            "year",
            lost_customer_hours,
            ejt,
            customer_satisfaction,
            schedule_operated,
            esc_avail
        FROM v_perfomance_base
        ORDER BY "year", line;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    df["year_label"] = df["year"]
    df["year"] = df["year"].str[:4].astype(int)
    return df
