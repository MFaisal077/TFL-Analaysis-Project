import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import data_loader

st.set_page_config(layout="wide", page_title="TFL Dashboard")

from data_loader import (
    get_network_benchmark,
    get_most_volatile_line,
    get_best_satisfaction_line,
    get_worst_disruption_line,
    get_volatility_ranking,
    get_line_metrics,
    get_yearly_rankings,
    get_most_stable_line,
    get_top_insight_lines,
    get_yearly_rankings
)

benchmark_df = get_network_benchmark()
most_volatile_line, volatility_score = get_most_volatile_line()
best_css_line, best_css_score = get_best_satisfaction_line()
worst_lch_line, worst_lch_score = get_worst_disruption_line()
volatility_df = get_volatility_ranking()
metrics_df = get_line_metrics()
most_stable_line, stable_score = get_most_stable_line()
insight_line, insight_lch, insight_css = get_top_insight_lines()
yearly_rankings=get_yearly_rankings()

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
    
    available_years = sorted(yearly_rankings["year"].dropna().unique().tolist())

    selected_year = st.selectbox(
    "Select year for rankings",
    options=available_years,
    index=0
    )

    ranking_metric_map = {
    "Best Lost Customer Hours Rank": "rank_lch_best",
    "Best Schedule Operated Rank": "rank_schedule_best",
    "Best Customer Satisfaction Rank": "rank_css_best"
    }

    selected_ranking_label = st.selectbox(
    "Select ranking metric",
    options=list(ranking_metric_map.keys()),
    index=0
    )

selected_ranking_metric = ranking_metric_map[selected_ranking_label]

selected_metric = metric_map[selected_metric_label]



st.title("London Underground Performance Dashboard")
st.write(
    "A historical analysis of reliability, disruption, and customer experience across Underground lines."
)

tab1, tab2, tab3,tab4 = st.tabs(["Overview", "Line Explorer", "Network Analysis","Yearly Rankings"])


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
with tab4:
    st.subheader("Yearly Performance Rankings")

    filtered_rankings = yearly_rankings[yearly_rankings["year"] == selected_year].copy()
    filtered_rankings = filtered_rankings.dropna(subset=[selected_ranking_metric])
    filtered_rankings = filtered_rankings.sort_values(selected_ranking_metric, ascending=True)

    fig_rank = px.bar(
        filtered_rankings,
        x="line",
        y=selected_ranking_metric,
        color="line",
        title=f"{selected_ranking_label} for {selected_year}"
    )

    fig_rank.update_layout(
        xaxis_title="Line",
        yaxis_title=selected_ranking_label,
        showlegend=False
    )

    st.plotly_chart(fig_rank, use_container_width=True)

    top_line = filtered_rankings.iloc[0]["line"]
    top_rank = filtered_rankings.iloc[0][selected_ranking_metric]

    st.caption(
        f"For {selected_year}, **{top_line}** achieved the strongest result in **{selected_ranking_label.lower()}** with rank **{int(top_rank)}**."
    )
    