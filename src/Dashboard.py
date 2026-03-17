import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

st.set_page_config(layout="wide", page_title="TFL Dashboard")


st.markdown("""
<style>
    /* Main title styling */
    h1 {
        color: #1f77b4;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5em;
    }
    
    /* Subheader styling */
    h2 {
        color: #2c3e50;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5em;
        font-size: 1.8em;
    }
    
    /* Tab styling */
    [data-baseweb="tab"] {
        background-color: #f8f9fa;
        font-size: 1.1em;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #f0f2f6;
        padding: 1.5em;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)



from data_loader import (
    get_network_benchmark,
    get_most_volatile_line,
    get_best_satisfaction_line,
    get_worst_disruption_line,
    get_volatility_ranking,
    get_line_metrics,
    get_most_stable_line,
    get_top_insight_lines,
    get_yearly_rankings,
    get_line_volatility_stats,
    get_anomalies,
    get_yoy_analysis,
    get_root_cause_data,
    get_data_quality_report
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
root_cause_df=get_root_cause_data()
volatility_df = volatility_df.rename(columns={"stddev_samp": "Volatility Score"})
data_quality_df=get_data_quality_report()

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
    st.title("London Underground")
    st.caption("Performance Dashboard")
    st.divider()
    st.markdown("""
    ###  About This Dashboard
    
    Select a tab above to explore different perspectives on TfL performance data.
    
    **Tabs Overview:**
    - **Overview**: Network-level summary
    - **Line Explorer**: Compare multiple lines
    - **Network Analysis**: Individual vs average
    - **Yearly Rankings**: Historical rankings
    - **YoY Analysis**: Year-over-year changes
    - **Anomalies**: Unusual events
    - **Volatility**: Stability ranking
    - **Root Cause**: Disruption sources
    - **Data Quality**: Data completeness
    - **Summary**: Key conclusions
    """)
    st.divider()
    st.markdown("""
    ### 📈 Data Period
    2004/05 to 2016/17
    
    ### 🚊 Lines Analyzed
    11 Underground lines
    """)



st.title("London Underground Performance Dashboard")
st.write(
    "A historical analysis of reliability, disruption, and customer experience across Underground lines."
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7,tab8,tab9,tab10 = st.tabs([
    "Overview", 
    "Line Explorer", 
    "Network Analysis",
    "Yearly Rankings",
    "YoY Analysis",
    "Anomalies",
    "Volatility",
    "Root Cause Analysis",
    "Data Quality Report",
    "A Summary Page"
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
    st.caption("""What this shows: A summary of network-level performance, including the most volatile and most stable lines.
    
    How to interpret it: Higher volatility scores indicate greater year-to-year fluctuation in disruption levels.""")
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
    
    
    col1, col2 = st.columns(2)
    
    with col1:
        tab2_selected_lines = st.multiselect(
            "Select line(s) to compare",
            options=all_lines,
            default=["Bakerloo", "Central", "Jubilee"],
            key="tab2_lines"
        )
    
    with col2:
        tab2_selected_metric_label = st.selectbox(
            "Select metric",
            options=list(metric_map.keys()),
            index=0,
            key="tab2_metric"
        )
    
    st.divider()
    
    # REST OF CODE (unchanged, but use tab2_selected_lines and tab2_selected_metric_label)
    tab2_selected_metric = metric_map[tab2_selected_metric_label]
    
    filtered_df = metrics_df.copy()
    if tab2_selected_lines:
        filtered_df = filtered_df[filtered_df["line"].isin(tab2_selected_lines)]
    
    filtered_df = filtered_df.dropna(subset=[tab2_selected_metric])
    
    fig_metric = px.line(
        filtered_df,
        x="year",
        y=tab2_selected_metric,
        color="line",
        markers=True,
        hover_data=["year_label"],
        title=f"{tab2_selected_metric_label} Over Time"
    )
    
    fig_metric.update_layout(
        xaxis_title="Year",
        yaxis_title=tab2_selected_metric_label,
        legend_title="Line"
    )
    
    st.plotly_chart(fig_metric, use_container_width=True)
    
    st.caption("""What this shows: Trends over time for the selected performance metric across chosen Underground lines.""")
    st.caption("""How to interpret it: Use this view to compare how individual lines changed over the available years. """)
    
    

with tab3:
    st.subheader("Line vs Network Average")
    
    # ADD CONTROLS HERE
    col1, col2 = st.columns(2)
    
    with col1:
        tab3_selected_line = st.selectbox(
            "Select line to compare with network",
            options=all_lines,
            index=0,
            key="tab3_line"
        )
    
    with col2:
        tab3_selected_metric_label = st.selectbox(
            "Select metric",
            options=list(metric_map.keys()),
            index=0,
            key="tab3_metric"
        )
    
    st.divider()
    
    # REST OF CODE
    line_col, network_col = network_metric_map[tab3_selected_metric_label]
    
    compare_df = benchmark_df[benchmark_df["line"] == tab3_selected_line].copy()
    compare_df = compare_df.dropna(subset=[line_col, network_col])
    
    plot_df = compare_df[["year", "year_label", line_col, network_col]].copy()
    plot_df = plot_df.rename(columns={
        line_col: tab3_selected_line,
        network_col: "Network Average"
    })
    
    plot_df = plot_df.melt(
        id_vars=["year", "year_label"],
        value_vars=[tab3_selected_line, "Network Average"],
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
        title=f"{tab3_selected_metric_label}: {tab3_selected_line} vs Network Average"
    )
    
    fig_compare.update_layout(
        xaxis_title="Year",
        yaxis_title=tab3_selected_metric_label,
        legend_title="Series"
    )
    
    st.plotly_chart(fig_compare, use_container_width=True)
    st.caption(
        f"This chart compares {tab3_selected_line} against the network average for {tab3_selected_metric_label.lower()}."
    )
    
    st.caption(""" 
               What this shows: A comparison between one selected line and the network average for the chosen metric.
How to interpret it: Values above or below the network average indicate how the selected line performs relative to the wider system.
               """)
with tab4:
    st.subheader("Yearly Performance Rankings")
    
    # ADD CONTROLS HERE
    col1, col2 = st.columns(2)
    
    with col1:
        tab4_available_years = sorted(yearly_rankings["year"].dropna().unique().tolist())
        tab4_selected_year = st.selectbox(
            "Select year for rankings",
            options=tab4_available_years,
            index=0,
            key="tab4_year"
        )
    
    with col2:
        tab4_ranking_metric_map = {
            "Best Lost Customer Hours Rank": "rank_lch_best",
            "Best Schedule Operated Rank": "rank_schedule_best",
            "Best Customer Satisfaction Rank": "rank_css_best"
        }
        tab4_selected_ranking_label = st.selectbox(
            "Select ranking metric",
            options=list(tab4_ranking_metric_map.keys()),
            index=0,
            key="tab4_ranking"
        )
    
    st.divider()
    
    # REST OF CODE
    tab4_selected_ranking_metric = tab4_ranking_metric_map[tab4_selected_ranking_label]
    
    filtered_rankings = yearly_rankings[yearly_rankings["year"] == tab4_selected_year].copy()
    filtered_rankings = filtered_rankings.dropna(subset=[tab4_selected_ranking_metric])
    filtered_rankings = filtered_rankings.sort_values(tab4_selected_ranking_metric, ascending=True)
    
    fig_rank = px.bar(
        filtered_rankings,
        x="line",
        y=tab4_selected_ranking_metric,
        color="line",
        title=f"{tab4_selected_ranking_label} for {tab4_selected_year}"
    )
    
    fig_rank.update_layout(
        xaxis_title="Line",
        yaxis_title=tab4_selected_ranking_label,
        showlegend=False
    )
    
    st.plotly_chart(fig_rank, use_container_width=True)
    
    top_line = filtered_rankings.iloc[0]["line"]
    top_rank = filtered_rankings.iloc[0][tab4_selected_ranking_metric]
    
    st.caption(
        f"For {tab4_selected_year}, **{top_line}** achieved the strongest result in **{tab4_selected_ranking_label.lower()}** with rank **{int(top_rank)}**."
    )
    st.markdown(""" 
                What this shows: Performance rankings for a selected year based on the chosen metric.
How to interpret it: Lower rank values indicate stronger performance in the selected category.""")
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
    st.markdown(""" 
                    What this shows: Year-over-year changes in lost customer hours, highlighting improvement or decline.

How to interpret it: Negative change indicates improvement, while positive change indicates deterioration.""")



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

with tab8:
    st.subheader("Root Cause Analysis")
    
    # ADD CONTROL HERE
    tab8_root_cause_mode = st.selectbox(
        "View breakdown by",
        options=["Percentage Contribution", "Raw Lost Customer Hours"],
        index=0,
        key="tab8_root"
    )
    
    st.divider()
    
    # REST OF CODE
    if tab8_root_cause_mode == "Percentage Contribution":
        y_col = "percent_contribution"
        chart_title = "Disruption Cause Contribution Over Time"
        y_label = "Percentage Contribution (%)"
    else:
        y_col = "lost_customer_hours"
        chart_title = "Disruption Causes Over Time"
        y_label = "Lost Customer Hours"

    fig_root = px.line(
        root_cause_df,
        x="year",
        y=y_col,
        color="category",
        markers=True,
        hover_data=["year_label"],
        title=chart_title
    )

    fig_root.update_layout(
        xaxis_title="Year",
        yaxis_title=y_label,
        legend_title="Category"
    )

    st.plotly_chart(fig_root, use_container_width=True)

    if tab8_root_cause_mode == "Percentage Contribution":
        st.caption(
            "This view shows how the relative contribution of each disruption category changed over time."
        )
    else:
        st.caption(
            "This view shows the absolute lost customer hours attributed to each disruption category over time."
        )

    latest_year = root_cause_df["year"].max()
    latest_df = root_cause_df[root_cause_df["year"] == latest_year].copy()

    if tab8_root_cause_mode == "Percentage Contribution":
        top_category = latest_df.sort_values("percent_contribution", ascending=False).iloc[0]
        st.info(
            f"In {top_category['year_label']}, {top_category['category']} contributed the largest share of disruption at {top_category['percent_contribution']}%."
        )
    else:
        top_category = latest_df.sort_values("lost_customer_hours", ascending=False).iloc[0]
        st.info(
            f"In {top_category['year_label']}, {top_category['category']} accounted for the highest disruption impact with {round(top_category['lost_customer_hours'], 2)} lost customer hours."
        )
with tab9:
    st.subheader("Data Quality Overview")

    st.markdown("""
    **What this shows:** Availability of key metrics across Underground lines and years.

    **How to interpret it:** Higher missing-year counts indicate weaker coverage for that metric and should be considered when interpreting results.
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        total_missing_ejt = int(data_quality_df["missing_ejt_years"].sum())
        st.metric("Total Missing EJT Years", total_missing_ejt)

    with col2:
        total_missing_schedule = int(data_quality_df["missing_schedule_years"].sum())
        st.metric("Total Missing Schedule Years", total_missing_schedule)

    with col3:
        total_missing_esc = int(data_quality_df["missing_esc_years"].sum())
        st.metric("Total Missing Escalator Years", total_missing_esc)

    st.divider()

    st.dataframe(data_quality_df, use_container_width=True, hide_index=True)

    st.info(
        "This table helps explain where missing or incomplete data may affect interpretation of trends, rankings, and comparisons."
    )

with tab10:
    st.subheader("Executive Summary")

    st.markdown("""
    This page provides a high-level summary of the main findings from the London Underground performance analysis dashboard.
    It is designed for users who want a quick overview without reviewing each chart individually.
    """)

    st.divider()

    st.markdown("Key Findings")
    st.markdown(f"""
    - **{most_volatile_line}** is the most volatile line, with a volatility score of **{volatility_score}**.
    - **{most_stable_line}** is the most stable line, with a volatility score of **{stable_score}**.
    - **{worst_lch_line}** records the highest average lost customer hours (**{worst_lch_score}**).
    - **{best_css_line}** records the highest average customer satisfaction (**{best_css_score}**).
    """)

    if not anomalies_df.empty:
        strongest_anomaly = anomalies_df.sort_values("z_score", ascending=False).iloc[0]
        st.markdown(
            f"- The strongest anomaly was observed for **{strongest_anomaly['line']}** with a z-score of **{strongest_anomaly['z_score']:.2f}**."
        )

    latest_year = root_cause_df["year"].max()
    latest_root_df = root_cause_df[root_cause_df["year"] == latest_year].copy()

  

    st.divider()

    st.markdown("### Overall Interpretation")
    st.write(
        "The analysis shows that Underground performance varies substantially across lines and years. "
        "Some lines remain relatively stable over time, while others exhibit significant fluctuations, "
        "unusual events, and weaker reliability indicators. The dashboard also shows that disruption is "
        "not only unevenly distributed across lines, but also shaped by underlying operational causes."
    )

    st.divider()

    st.markdown("### Important Limitations")
    st.markdown("""
    - Rankings based on absolute lost customer hours may favour smaller lines such as Waterloo & City.
    - Some performance metrics are missing for certain years, which may affect comparison and trend interpretation.
    - The analysis is based on yearly data, so shorter-term variation is not captured.
    """)

    st.divider()

    st.info(
        "This summary is intended to provide a quick overview. Detailed evidence and visual exploration are available in the other tabs."
    )
    


footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: black;
color: white;
text-align: center;
font-size:25px;
}
</style>
<div class="footer">
<p>This Analysis was done by Mohammad Faisal <a style='display: block; text-align: center></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)