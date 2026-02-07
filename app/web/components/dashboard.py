import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import desc
from app.web.database import get_job_stats
from app.web.utils import status_badge
from app.models.job import Job


def render(db):
  """Render dashboard page."""
  st.title("📊 Dashboard")
  st.markdown("Overview of your job search progress")
  
  # Get stats
  stats = get_job_stats(db)
  
  # Metrics Row
  col1, col2, col3, col4 = st.columns(4)
  
  with col1:
    st.metric(
      "Total Jobs",
      stats['total'],
      delta=f"+{stats['recent_7days']} this week"
    )
  
  with col2:
    saved_count = stats['by_status'].get('saved', 0)
    st.metric("Saved", saved_count)
  
  with col3:
    applied_count = stats['by_status'].get('applied', 0)
    st.metric("Applied", applied_count)
  
  with col4:
    interview_count = stats['by_status'].get('interview', 0)
    st.metric("Interviews", interview_count)
  
  st.markdown("---")
  
  # Charts Row
  col1, col2 = st.columns(2)
  
  with col1:
    st.subheader("Jobs by Status")
    if stats['by_status']:
      status_df = pd.DataFrame(
        list(stats['by_status'].items()),
        columns=['Status', 'Count']
      )
      fig = px.pie(
        status_df,
        values='Count',
        names='Status',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
      )
      fig.update_layout(height=300)
      st.plotly_chart(fig, use_container_width=True)
    else:
      st.info("No jobs tracked yet. Start by scraping some jobs!")
  
  with col2:
    st.subheader("Jobs by Source")
    if stats['by_source']:
      source_df = pd.DataFrame(
        list(stats['by_source'].items()),
        columns=['Source', 'Count']
      )
      fig = px.bar(
        source_df,
        x='Source',
        y='Count',
        color='Source',
        color_discrete_sequence=px.colors.qualitative.Pastel
      )
      fig.update_layout(height=300, showlegend=False)
      st.plotly_chart(fig, use_container_width=True)
    else:
      st.info("No jobs tracked yet.")
  
  st.markdown("---")
  
  # Recent Jobs
  st.subheader("📅 Recent Jobs (Last 10)")
  recent_jobs = db.query(Job).order_by(desc(Job.created_at)).limit(10).all()
  
  if recent_jobs:
    for job in recent_jobs:
      with st.container():
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
          st.markdown(f"**{job.title}**")
          st.caption(f"{job.company} • {job.location or 'Remote'}")
        
        with col2:
          st.markdown(status_badge(job.status), unsafe_allow_html=True)
          st.caption(f"Added: {job.created_at.strftime('%Y-%m-%d')}")
        
        with col3:
          if st.button("View", key=f"view_{job.id}"):
            st.session_state['selected_job_id'] = job.id
            st.session_state['show_job_detail'] = True
            st.rerun()
        
        st.markdown("---")
  else:
    st.info("No jobs yet. Start by scraping jobs or adding them manually!")
