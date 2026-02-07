import streamlit as st

def configure_page():
  """Configure Streamlit page settings."""
  st.set_page_config(
    page_title="JobTrail - Job Application Tracker",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
  )

def load_custom_css():
  """Load custom CSS styles."""
  st.markdown("""
    <style>
    .main {
      padding: 0rem 1rem;
    }
    .stMetric {
      background-color: #808080;
      padding: 15px;
      border-radius: 10px;
    }
    .job-card {
      padding: 20px;
      border-radius: 10px;
      border: 1px solid #e0e0e0;
      margin: 10px 0;
      background-color: white;
    }
    .status-badge {
      padding: 5px 10px;
      border-radius: 5px;
      font-size: 12px;
      font-weight: bold;
    }
    .status-saved { background-color: #e3f2fd; color: #1976d2; }
    .status-applied { background-color: #fff3e0; color: #f57c00; }
    .status-interview { background-color: #f3e5f5; color: #7b1fa2; }
    .status-offer { background-color: #e8f5e9; color: #388e3c; }
    .status-rejected { background-color: #ffebee; color: #d32f2f; }
    </style>
  """, unsafe_allow_html=True)

