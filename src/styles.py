"""
FINAL Industry-Standard CSS – London Underground Performance Dashboard
TfL official branding + premium corporate polish (2026)
"""
import streamlit as st

def load_custom_css():
    """Clean, production-ready CSS – no more arrowdown bug."""
    
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        :root {
            --tfl-blue: #0019a8;
            --tfl-red: #e21836;
            --dark-text: #1e2a44;
            --light-bg: #f8f9fa;
            --border: #e0e4ea;
        }
        
        /* Safe font application - NO universal * selector */
        h1, h2, h3, .stMarkdown, p, label, .streamlit-expanderHeader {
            font-family: 'Inter', system-ui, sans-serif !important;
        }
        
        /* Rest of your beautiful styles (unchanged but cleaner) */
        h1 { color: var(--tfl-blue) !important; font-size: 2.9em !important; font-weight: 700 !important; text-align: center !important; letter-spacing: -0.9px !important; }
        
        h2 { color: var(--tfl-blue) !important; font-size: 1.78em !important; font-weight: 600 !important; border-bottom: 4px solid var(--tfl-red) !important; padding-bottom: 0.65em !important; margin: 1.5em 0 0.9em 0 !important; }
        
        [data-baseweb="tab"] { background-color: white !important; font-size: 1.1em !important; font-weight: 600 !important; padding: 1.05em 1.5em !important; border-radius: 8px 8px 0 0 !important; }
        
        [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(180deg, var(--tfl-blue), #001a70) !important;
            color: white !important;
            border-bottom: 5px solid var(--tfl-red) !important;
        }
        
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
            padding: 1.85em 1.5em !important;
            border-radius: 14px !important;
            border-left: 7px solid var(--tfl-blue) !important;
            box-shadow: 0 6px 20px rgba(0, 25, 168, 0.12) !important;
        }
        
        .stPlotlyChart { border-radius: 14px !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.07) !important; }
        
        .footer {
            position: fixed; left: 0; bottom: 0; width: 100%;
            background: linear-gradient(90deg, var(--tfl-blue) 0%, #001a70 100%) !important;
            color: white !important; text-align: center !important; padding: 1.15em 0 !important;
            font-weight: 500 !important; box-shadow: 0 -4px 15px rgba(0, 25, 168, 0.3) !important;
        }
    </style>
    """, unsafe_allow_html=True)