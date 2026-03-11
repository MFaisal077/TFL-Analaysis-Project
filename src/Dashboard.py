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
    get_yearly_rankings,
    get_line_volatility_stats,
    get_anomalies,
    get_yoy_analysis
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
yoy_df = get_yoy_analysis()
anomalies_df = get_anomalies()
volatility_stats_df = get_line_volatility_stats()

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

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview", 
    "Line Explorer", 
    "Network Analysis",
    "Yearly Rankings",
    "YoY Analysis",
    "Anomalies",
    "Volatility"
])


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
with tab5:
    st.subheader("Year-over-Year Performance Analysis")
    
    st.markdown("""
    **What this shows:**
    - Lines that improved year-to-year (negative change = good)
    - Lines that declined year-to-year (positive change = bad)
    - Identifies which lines are on right/wrong trajectory
    """)
    
    if not yoy_df.empty:
        latest_year = yoy_df['year'].max()
        yoy_latest = yoy_df[yoy_df['year'] == latest_year].copy()
        
        if not yoy_latest.empty:
            # Improving lines (negative = fewer disruptions)
            improving = yoy_latest[yoy_latest['yoy_change'] < 0].sort_values('yoy_change')
            
            # Declining lines (positive = more disruptions)
            declining = yoy_latest[yoy_latest['yoy_change'] > 0].sort_values('yoy_change', ascending=False)
            
            st.markdown(f"### Performance Change: {int(latest_year - 1)} → {int(latest_year)}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Best Improvements**")
                if not improving.empty:
                    for idx, (_, row) in enumerate(improving.head(5).iterrows(), 1):
                        improvement = abs(row['yoy_change'])
                        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "✓"
                        st.success(f"{medal} {row['line']}: -{improvement:,.0f} hours")
                else:
                    st.info("No improvements")
            
            with col2:
                st.markdown("**Most Decline**")
                if not declining.empty:
                    for idx, (_, row) in enumerate(declining.head(5).iterrows(), 1):
                        st.error(f"{row['line']}: +{row['yoy_change']:,.0f} hours")
                else:
                    st.info("No declines")
            
            st.divider()
            
            # Visualization: All lines
            st.markdown("### All Lines: Year-over-Year Change")
            viz_df = yoy_latest.sort_values('yoy_change', ascending=False)
            
            fig_yoy = px.bar(
                viz_df,
                x='yoy_change',
                y='line',
                color='yoy_change',
                color_continuous_scale=['green', 'red'],
                title='Lost Customer Hours Change (Year-over-Year)',
                labels={'yoy_change': 'YoY Change (hours)', 'line': 'Line'},
                hover_data={'yoy_change': ':.0f'}
            )
            
            fig_yoy.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.5)
            fig_yoy.update_layout(
                showlegend=False,
                height=500
            )
            
            st.plotly_chart(fig_yoy, use_container_width=True)
        else:
            st.warning("No data available for selected year")
    else:
        st.error("Unable to load YoY data")


# ============= TAB 6: ANOMALIES =============
with tab6:
    st.subheader("Anomaly Detection: Unusual Performance Events")
    
    st.markdown("""
    This identifies year-over-year changes that are **statistically unusual**.
    
    **What causes anomalies:**
    - Major disruptions or incidents
    - Unexpected improvements
    - Significant operational changes
    
    **How it works:**
    - Z-score > 2.5 or < -2.5 indicates statistical outlier
    - More than 2.5 standard deviations from the mean
    """)
    
    if not anomalies_df.empty and len(anomalies_df) > 0:
        st.markdown(f"### Found {len(anomalies_df)} Anomalies")
        
        st.divider()
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            worst_idx = anomalies_df['z_score'].idxmax()
            worst_line = anomalies_df.loc[worst_idx]
            st.metric(
                "Worst Anomaly",
                worst_line['line'],
                f"Z-score: {worst_line['z_score']:.2f}"
            )
        
        with col2:
            best_idx = anomalies_df['z_score'].idxmin()
            best_line = anomalies_df.loc[best_idx]
            st.metric(
                "Best Anomaly",
                best_line['line'],
                f"Z-score: {best_line['z_score']:.2f}"
            )
        
        with col3:
            st.metric(
                "Total Anomalies",
                len(anomalies_df),
                "unusual events"
            )
        
        st.divider()
        
        # Table of anomalies
        st.markdown("### Detailed Anomalies")
        display_cols = ['line', 'year', 'lost_customer_hours', 'yoy_change', 'z_score']
        st.dataframe(
            anomalies_df[display_cols].sort_values('z_score', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        
        # Visualization
        st.markdown("### Anomalies Visualization")
        fig_anomalies = px.scatter(
            anomalies_df,
            x='z_score',
            y='line',
            size=anomalies_df['yoy_change'].abs(),
            color='z_score',
            hover_data=['year', 'yoy_change', 'lost_customer_hours'],
            title='Anomalous Performance Changes (Z-Score)',
            labels={'z_score': 'Z-Score', 'line': 'Line'},
            color_continuous_scale=['red', 'blue']
        )
        
        fig_anomalies.add_vline(x=2.5, line_dash="dash", line_color="red", opacity=0.3)
        fig_anomalies.add_vline(x=-2.5, line_dash="dash", line_color="blue", opacity=0.3)
        fig_anomalies.update_layout(height=500)
        
        st.plotly_chart(fig_anomalies, use_container_width=True)
        
        st.markdown("""
        **Interpretation:**
        - Red dashed line: Z-score = 2.5 (significant positive anomaly)
        - Blue dashed line: Z-score = -2.5 (significant negative anomaly)
        - Points beyond these lines are statistically unusual
        """)
    else:
        st.info("No anomalies detected in the data (all changes are within 2.5 standard deviations)")


# ============= TAB 7: VOLATILITY =============
with tab7:
    st.subheader("Line Volatility: Performance Stability Analysis")
    
    st.markdown("""
    **Volatility measures:** How consistent is a line's performance year-to-year?
    
    - **High volatility:** Unpredictable service (more disruptions some years, fewer others)
    - **Low volatility:** Consistent service (similar disruptions year after year)
    
    **What causes volatility:**
    - Ongoing maintenance or upgrades
    - Staffing fluctuations
    - Infrastructure issues
    - Demand variations
    """)
    
    if not volatility_stats_df.empty:
        # Top unstable lines
        st.markdown("### Most Volatile Lines (Least Stable)")
        top_volatile = volatility_stats_df.head(5)
        
        for idx, (_, row) in enumerate(top_volatile.iterrows(), 1):
            st.warning(f"**{idx}. {row['line']}** - Volatility Score: {row['volatility']:.2f}")
        
        st.divider()
        
        # Top stable lines
        st.markdown("### Most Stable Lines (Most Consistent)")
        top_stable = volatility_stats_df.tail(5).sort_values('volatility')
        
        for idx, (_, row) in enumerate(top_stable.iterrows(), 1):
            st.success(f"**{idx}. {row['line']}** - Volatility Score: {row['volatility']:.2f}")
        
        st.divider()
        
        # Chart
        st.markdown("### All Lines: Volatility Ranking")
        
        fig_vol = px.bar(
            volatility_stats_df.sort_values('volatility', ascending=False),
            x='volatility',
            y='line',
            color='volatility',
            color_continuous_scale='Reds',
            title='Performance Volatility by Line (Higher = Less Stable)',
            labels={'volatility': 'Volatility Score (Std Dev)', 'line': 'Line'},
            hover_data={'volatility': ':.2f', 'valid_years': True}
        )
        
        fig_vol.update_layout(
            showlegend=False,
            height=600
        )
        
        st.plotly_chart(fig_vol, use_container_width=True)
        
        st.markdown("""
        **Why this matters for operations:**
        - Volatile lines may have underlying issues
        - Stable lines indicate good operational control
        - Improving (reducing) volatility is a positive sign
        - Lines with high volatility warrant investigation
        """)
    else:
        st.error("Unable to load volatility data")