import streamlit as st
import pandas as pd
import psycopg2
import warnings

# 1. SETUP & CONFIGURATION
st.set_page_config(layout="wide", page_title="TFL Dashboard")
warnings.filterwarnings('ignore') # Hides the SQLAlchemy warning

# 2. DATA FUNCTIONS (Kept separate as you requested)
def connect_lchbyline():
    conn = psycopg2.connect(
        host="localhost",
        database="TFL_Analysis",
        user="postgres",
        password="Faisal@123"
    )
    query = "SELECT line, lost_customer_hours, year FROM lchbyline ORDER BY year;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def connect_lchbycategory():
    conn = psycopg2.connect(
        host="localhost",
        database="TFL_Analysis",
        user="postgres",
        password="Faisal@123"
    )
    # Your fixed query with the division for Millions
    query = """
    SELECT 
        year, 
        category, 
        (lost_customer_hours / 1000000.0) as lost_hours_millions 
    FROM lchbycategory 
    ORDER BY year;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# 3. SIDEBAR (The "Control Panel")
with st.sidebar:
    st.header("Project Controls")
    st.write("This dashboard visualizes the long-term performance trends of the London Underground.")
    
    st.divider()
    
    # You can add filters here later (e.g., Year Slider)
    st.info("Data Source: TFL Open Data (2004-2017)")
    st.caption("Created by Mohammad Faisal")

# 4. MAIN PAGE LAYOUT
# Simple, Clean Title
st.title("🚇 London Underground Performance")

# Description Block
st.markdown("""
### Project Objective
This tool bridges the gap between raw **Transport for London (TfL)** data and actionable insight. 

While apps like Google Maps focus on *real-time* travel, this dashboard is designed for **historical strategic analysis**. It ingests over 13 years of scattered performance data to help researchers, journalists, and urban planners answer critical questions:
 **Long-Term Trends:** How has reliability evolved since 2004?
 **Root Cause Analysis:** Are delays caused by aging infrastructure or staffing issues?
 **Comparative Performance:** Which lines are improving, and which are deteriorating?

**Key Metric:**
The analysis focuses on **Lost Customer Hours (LCH)**—the industry-standard proxy for measuring the total human impact of network delays.
""")


st.divider() 


col1, col2 = st.columns(2)

with col1:
    st.subheader("Performance by Line")
    try:
        data_line = connect_lchbyline()
        st.line_chart(data_line, x="year", y="lost_customer_hours", color="line")
    except Exception as e:
        st.error(f"Database Error: {e}")

with col2:
    st.subheader("Performance by Cause (Millions)")
    try:
        data_cat = connect_lchbycategory()
        st.line_chart(data_cat, x="year", y="lost_hours_millions", color="category")
    except Exception as e:
        st.error(f"Database Error: {e}")