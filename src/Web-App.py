import streamlit as st
import pandas as pd
import psycopg2
import warnings


st.set_page_config(layout="wide", page_title="TFL Dashboard")
warnings.filterwarnings('ignore')

@st.cache_data
def connect_lchbyline():
    conn = psycopg2.connect(
        host="localhost", database="TFL_Analysis",
        user="postgres", password="Faisal@123"
    )
    query = """
        SELECT
            "year",
            line,
            lost_customer_hours,
            LAG(lost_customer_hours) OVER (PARTITION BY line ORDER BY "year") as prev_year,
            COALESCE(lost_customer_hours - LAG(lost_customer_hours) 
                     OVER (PARTITION BY line ORDER BY "year"), 0) as year_over_year_change
        FROM lchbyline
        ORDER BY line, "year";
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data
def connect_lchbycategory():
    conn = psycopg2.connect(
        host="localhost", database="TFL_Analysis",
        user="postgres", password="Faisal@123"
    )
    query = """
        SELECT year, category, (lost_customer_hours / 1000000.0) as lost_hours_millions
        FROM lchbycategory
        ORDER BY year;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data
def connect_ejt():
    conn = psycopg2.connect(
        host="localhost", database="TFL_Analysis",
        user="postgres", password="Faisal@123"
    )
    query = "SELECT line, year, ejt FROM excess_journey_time ORDER BY year;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data
def connect_css_esc_avl():
     conn = psycopg2.connect(
        host="localhost", database="TFL_Analysis",
        user="postgres", password="Faisal@123"
    )
     query="""
     SELECT 
    esc_avl.line,
    CASE 
        WHEN esc_avl.esc_avail > 95 THEN 'High'
        WHEN esc_avl.esc_avail BETWEEN 90 AND 95 THEN 'Medium'
        ELSE 'Low'
    END as esc_tier,
    ROUND(AVG(css.customer_satisfaction), 1) as avg_satisfaction_percent,
    COUNT(*) as num_years
FROM css 
INNER JOIN esc_avl ON css.line = esc_avl.line AND css."year" = esc_avl."year"
GROUP BY esc_avl.line, esc_tier
ORDER BY esc_avl.line, esc_tier DESC;"""
     df=pd.read_sql(query,conn)
     conn.close()
     return df
    


data_line = connect_lchbyline()
data_cat = connect_lchbycategory()
data_ejt = connect_ejt()
data_css=connect_css_esc_avl()


with st.sidebar:
    st.header("Project Controls")
    st.write("This dashboard visualizes the long-term performance trends of the London Underground.")
    st.divider()

    st.subheader("Filter Lines")
    all_lines = sorted(data_line['line'].unique())
    selected_lines = st.multiselect(
        "Select lines to display",
        options=all_lines,
        default=["Bakerloo", "Central", "Jubilee"]
    )

    st.divider()
    st.info("Data Source: TFL Open Data (2004-2017)")
    st.caption("Created by Mohammad Faisal")


st.title("London Underground Performance")

st.markdown("""
### Project Objective
This tool bridges the gap between raw **Transport for London (TfL)** data and actionable insight.
""")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Year-Over-Year Change in LCH")
    try:
        df = data_line.copy()
        if selected_lines:
            df = df[df['line'].isin(selected_lines)]
        st.line_chart(df, x="year", y="year_over_year_change", color="line")
    except Exception as e:
        st.error(f"Database Error: {e}")

with col2:
    st.subheader("Performance by Cause (Millions)")
    try:
        df = data_cat.copy()
        if selected_lines:  
            pass
        st.line_chart(df, x="year", y="lost_hours_millions", color="category")
    except Exception as e:
        st.error(f"Database Error: {e}")

with col3:
    st.subheader("Excess Journey Time")
    try:
        df = data_ejt.copy()
        if selected_lines:
            df = df[df['line'].isin(selected_lines)]
        st.line_chart(df, x="year", y="ejt", color="line")
    except Exception as e:
        st.error(f"Database Error: {e}")
        
st.divider()
st.subheader("Customer Satisfaction vs Escalator Availability")
try:
    df = data_css.copy()
    if selected_lines:
        df = df[df['line'].isin(selected_lines)]
    st.bar_chart(df, x="line", y="avg_satisfaction_percent", color="esc_tier", use_container_width=True)
except Exception as e:
    st.error(f"Database Error: {e}")
    