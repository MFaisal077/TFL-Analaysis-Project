import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

st.set_page_config(layout="wide", page_title="TFL Dashboard")
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

# ---------------- CONNECTION ----------------
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="TFL_Analysis",
        user="postgres",
        password="Faisal@123"
    )


# ---------------- DATA LOADERS ----------------
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


benchmark_df = get_network_benchmark()
most_volatile_line, volatility_score = get_most_volatile_line()
best_css_line, best_css_score = get_best_satisfaction_line()
worst_lch_line, worst_lch_score = get_worst_disruption_line()
volatility_df = get_volatility_ranking()
metrics_df = get_line_metrics()
most_stable_line, stable_score = get_most_stable_line()
insight_line, insight_lch, insight_css = get_top_insight_lines()

volatility_df = volatility_df.rename(columns={"stddev_samp": "Volatility Score"})

metric_map = {
    "Lost Customer Hours": "lost_customer_hours",
    "Excess Journey Time": "ejt",
    "Customer Satisfaction": "customer_satisfaction",
    "Schedule Operated": "schedule_operated",
    "Escalator Availability": "esc_avail"
}

network_metric_map = {
    "Lost Customer Hours": ("lost_customer_hours", "network_avg_lch"),
    "Excess Journey Time": ("ejt", "network_avg_ejt"),
    "Customer Satisfaction": ("customer_satisfaction", "network_avg_css"),
    "Schedule Operated": ("schedule_operated", "network_avg_schedule"),
    "Escalator Availability": ("esc_avail", "network_avg_esc")
}

metric_descriptions = {
    "Lost Customer Hours": "Measures disruption impact experienced by passengers. Higher values indicate worse service reliability.",
    "Excess Journey Time": "Shows the additional journey time experienced compared with scheduled service.",
    "Customer Satisfaction": "Represents the average passenger satisfaction score for each line.",
    "Schedule Operated": "Percentage of planned service that was actually operated.",
    "Escalator Availability": "Percentage of escalators available for use across each line."
}

all_lines = sorted(metrics_df["line"].dropna().unique().tolist())


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("Dashboard Controls")

    selected_lines = st.multiselect(
        "Select line(s)",
        options=all_lines,
        default=["Bakerloo", "Central", "Jubilee"]
    )

    selected_metric_label = st.selectbox(
        "Select metric",
        options=list(metric_map.keys()),
        index=0
    )

    selected_line_for_comparison = st.selectbox(
        "Select one line for network comparison",
        options=all_lines,
        index=0
    )

selected_metric = metric_map[selected_metric_label]


# ---------------- PAGE HEADER ----------------
st.title("London Underground Performance Dashboard")
st.write(
    "A historical analysis of reliability, disruption, and customer experience across Underground lines."
)

tab1, tab2, tab3 = st.tabs(["Overview", "Line Explorer", "Network Analysis"])


# ---------------- TAB 1: OVERVIEW ----------------
with tab1:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Most Volatile Line", most_volatile_line)
        st.caption(f"Volatility score: {volatility_score}")

    with col2:
        st.metric("Best Customer Satisfaction Line", best_css_line)
        st.caption(f"Average satisfaction: {best_css_score}")

    with col3:
        st.metric("Worst Disruption Line", worst_lch_line)
        st.caption(f"Average LCH: {worst_lch_score}")

    st.divider()

    st.subheader("Operational Stability Ranking")
    fig_vol = px.bar(
        volatility_df,
        x="line",
        y="Volatility Score",
        title="Operational Stability by Line"
    )
    fig_vol.update_layout(
        xaxis_title="Line",
        yaxis_title="Volatility Score"
    )
    st.plotly_chart(fig_vol, use_container_width=True)

    st.caption(
        "Higher volatility scores indicate greater year-to-year fluctuations in lost customer hours."
    )
    st.divider()
    st.subheader("Key Insights")

    st.markdown(
    f"""
    - **{most_volatile_line}** is the most volatile line, with a volatility score of **{volatility_score}**.
    - **{most_stable_line}** is the most stable line, with a volatility score of **{stable_score}**.
    - **{worst_lch_line}** shows the highest average lost customer hours (**{worst_lch_score}**), indicating the greatest average disruption.
    """
    )


# ---------------- TAB 2: LINE EXPLORER ----------------
with tab2:
    st.subheader("Line Explorer")

    filtered_df = metrics_df.copy()
    if selected_lines:
        filtered_df = filtered_df[filtered_df["line"].isin(selected_lines)]

    filtered_df = filtered_df.dropna(subset=[selected_metric])

    fig_metric = px.line(
        filtered_df,
        x="year",
        y=selected_metric,
        color="line",
        markers=True,
        hover_data=["year_label"],
        title=f"{selected_metric_label} Over Time"
    )

    fig_metric.update_layout(
        xaxis_title="Year",
        yaxis_title=selected_metric_label,
        legend_title="Line"
    )

    st.plotly_chart(fig_metric, use_container_width=True)
    st.caption(metric_descriptions[selected_metric_label])


# ---------------- TAB 3: NETWORK ANALYSIS ----------------
with tab3:
    st.subheader("Line vs Network Average")

    line_col, network_col = network_metric_map[selected_metric_label]

    compare_df = benchmark_df[benchmark_df["line"] == selected_line_for_comparison].copy()
    compare_df = compare_df.dropna(subset=[line_col, network_col])

    plot_df = compare_df[["year", "year_label", line_col, network_col]].copy()
    plot_df = plot_df.rename(columns={
        line_col: selected_line_for_comparison,
        network_col: "Network Average"
    })

    plot_df = plot_df.melt(
        id_vars=["year", "year_label"],
        value_vars=[selected_line_for_comparison, "Network Average"],
        var_name="Series",
        value_name="Value"
    )

    fig_compare = px.line(
        plot_df,
        x="year",
        y="Value",
        color="Series",
        markers=True,
        hover_data=["year_label"],
        title=f"{selected_metric_label}: {selected_line_for_comparison} vs Network Average"
    )

    fig_compare.update_layout(
        xaxis_title="Year",
        yaxis_title=selected_metric_label,
        legend_title="Series"
    )

    st.plotly_chart(fig_compare, use_container_width=True)
    st.caption(
        f"This chart compares {selected_line_for_comparison} against the network average for {selected_metric_label.lower()}."
    )