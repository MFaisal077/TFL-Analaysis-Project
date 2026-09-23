"""
FINAL Industry-Standard CSS – London Underground Performance Dashboard
TfL official branding + Glassmorphism UI
"""

import streamlit as st


def load_custom_css():
    """Injects high-specificity Glassmorphism CSS without overriding Streamlit icons."""

    st.markdown(
        """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        :root {
            --tfl-blue: #0019a8;
            --tfl-red: #e21836;
            --dark-text: #1e2a44;
            --glass-bg: rgba(255, 255, 255, 0.65);
            --glass-border: rgba(255, 255, 255, 0.8);
            --glass-shadow: 0 8px 32px 0 rgba(0, 25, 168, 0.08);
        }

        /* Overall App Background Soft Gradient */
        .stApp {
            background: linear-gradient(135deg, #f0f4f9 0%, #e5ecf6 100%) !important;
        }

        /* 1. Safe Scoped Typography (Targets text elements only, leaves UI icons alone) */
        .stMarkdown, 
        .stMarkdown p, 
        .stMarkdown label, 
        .stMarkdown span,
        div[data-testid="stCaptionContainer"],
        div[data-testid="stHeader"] {
            font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
            color: var(--dark-text) !important;
        }

        /* 2. Page Title Header */
        h1, .stMarkdown h1 { 
            font-family: 'Inter', sans-serif !important;
            color: var(--tfl-blue) !important; 
            font-size: 2.6rem !important; 
            font-weight: 700 !important; 
            text-align: center !important; 
            letter-spacing: -0.8px !important;
            margin-bottom: 0.5rem !important;
        }

        /* 3. Section Headers */
        h2, .stMarkdown h2 { 
            font-family: 'Inter', sans-serif !important;
            color: var(--tfl-blue) !important; 
            font-size: 1.6rem !important; 
            font-weight: 600 !important; 
            border-bottom: 3px solid var(--tfl-red) !important; 
            padding-bottom: 0.5rem !important; 
            margin: 1.5rem 0 1rem 0 !important; 
        }

        /* 4. Glassmorphic Metric Cards */
        div[data-testid="stMetric"], 
        div[data-testid="metric-container"] {
            background: var(--glass-bg) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border-radius: 16px !important;
            border: 1px solid var(--glass-border) !important;
            border-left: 6px solid var(--tfl-blue) !important;
            box-shadow: var(--glass-shadow) !important;
            padding: 1.25rem 1.5rem !important;
        }

        /* Metric Titles & Numbers */
        div[data-testid="stMetricLabel"] label,
        div[data-testid="stMetricLabel"] p {
            font-family: 'Inter', sans-serif !important;
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            color: #4a5568 !important;
        }

        div[data-testid="stMetricValue"] div {
            font-family: 'Inter', sans-serif !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: var(--tfl-blue) !important;
        }

        /* 5. Glassmorphic Tab Navigation */
        button[data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.4) !important; 
            backdrop-filter: blur(8px) !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.95rem !important; 
            font-weight: 600 !important; 
            padding: 0.75rem 1.25rem !important; 
            border-radius: 10px 10px 0 0 !important;
            border: 1px solid rgba(255, 255, 255, 0.6) !important;
            border-bottom: none !important;
            margin-right: 4px !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(180deg, var(--tfl-blue), #001a70) !important;
            border-bottom: 4px solid var(--tfl-red) !important;
            box-shadow: 0 4px 15px rgba(0, 25, 168, 0.2) !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] p,
        button[data-baseweb="tab"][aria-selected="true"] span {
            color: #ffffff !important;
        }

        /* 6. Glassmorphic Chart Containers */
        .stPlotlyChart { 
            background: var(--glass-bg) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border-radius: 16px !important; 
            border: 1px solid var(--glass-border) !important;
            box-shadow: var(--glass-shadow) !important;
            padding: 12px !important;
        }

        /* 7. Glassmorphic Footer */
        .dashboard-footer {
            width: 100%;
            background: rgba(0, 25, 168, 0.85) !important;
            backdrop-filter: blur(10px) !important;
            text-align: center !important; 
            padding: 1rem 0 !important;
            margin-top: 3rem !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15) !important;
        }

        .dashboard-footer p {
            font-family: 'Inter', sans-serif !important;
            color: #ffffff !important;
            font-weight: 500 !important;
            margin: 0 !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_footer():
    """Renders the branded bottom bar."""
    st.markdown(
        """
        <div class="dashboard-footer">
            <p>London Underground Performance Analytics • Powered by TfL Open Data</p>
        </div>
        """,
        unsafe_allow_html=True,
    )