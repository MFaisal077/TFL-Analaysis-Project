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

@st.cache_data
def get_yoy_analysis():
    """
    Get year-over-year analysis from v_anomaly_flags view.
    Shows which lines improved/declined.
    """
    conn = get_connection()
    query = """
        SELECT 
            line,
            year,
            lost_customer_hours,
            yoy_change,
            z_score,
            anomaly_flag
        FROM v_anomaly_flags
        WHERE yoy_change IS NOT NULL
        ORDER BY year DESC, yoy_change ASC;
    """
    try:
        df = pd.read_sql(query, conn)
        conn.close()
        # Convert year to numeric if string
        if isinstance(df['year'].iloc[0], str):
            df['year'] = df['year'].str[:4].astype(int)
        return df
    except Exception as e:
        print(f"Error fetching YoY data: {e}")
        conn.close()
        return pd.DataFrame()


@st.cache_data
def get_anomalies():
    """
    Get flagged anomalies from v_anomaly_flags view.
    Identifies unusual year-over-year changes (z-score > 2.5 or < -2.5).
    """
    conn = get_connection()
    query = """
        SELECT 
            line,
            year,
            lost_customer_hours,
            yoy_change,
            z_score,
            std_yoy,
            mean_yoy,
            anomaly_flag
        FROM v_anomaly_flags
        WHERE anomaly_flag = 'Anomaly'
        ORDER BY z_score DESC;
    """
    try:
        df = pd.read_sql(query, conn)
        conn.close()
        if not df.empty and isinstance(df['year'].iloc[0], str):
            df['year'] = df['year'].str[:4].astype(int)
        return df
    except Exception as e:
        print(f"Error fetching anomalies: {e}")
        conn.close()
        return pd.DataFrame()


@st.cache_data
def get_line_volatility_stats():
    """
    Get volatility statistics for each line from v_line_volatility.
    Higher values = less stable/predictable performance.
    """
    conn = get_connection()
    query = """
        SELECT 
            line,
            stddev_samp as volatility,
            avg_trend,
            worst_drop,
            biggest_spike,
            valid_years
        FROM v_line_volatility
        ORDER BY stddev_samp DESC;
    """
    try:
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error fetching volatility stats: {e}")
        conn.close()
        return pd.DataFrame()