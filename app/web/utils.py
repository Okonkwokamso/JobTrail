import pandas as pd
import streamlit as st
from app.models.job import Job


def status_badge(status: str) -> str:
  """Return HTML for status badge."""
  return f'<span class="status-badge status-{status}">{status.upper()}</span>'

def jobs_to_dataframe(jobs: list) -> pd.DataFrame:
  """Convert list of Job objects to pandas DataFrame."""
  if not jobs:
    return pd.DataFrame()
  
  data = []
  for job in jobs:
    data.append({
      'ID': job.id,
      'Title': job.title,
      'Company': job.company,
      'Location': job.location or 'Remote',
      'Type': job.job_type or 'N/A',
      'Salary': job.salary or 'Not specified',
      'Status': job.status,
      'Source': job.source,
      'Date Added': job.created_at.strftime('%Y-%m-%d'),
      'URL': job.url
    })
  
  return pd.DataFrame(data)


def init_session_state():
  """Initialize session state variables."""
  if 'show_job_detail' not in st.session_state:
    st.session_state['show_job_detail'] = False
  
  if 'selected_job_id' not in st.session_state:
    st.session_state['selected_job_id'] = None
