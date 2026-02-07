import streamlit as st
from app.models.job import Job


def render(db):
  """Render applications kanban board."""
  st.title("📝 Application Pipeline")
  st.markdown("Kanban board view of your applications")
  
  statuses = ['saved', 'applied', 'interview', 'offer', 'rejected']
  cols = st.columns(len(statuses))
  
  for idx, status in enumerate(statuses):
    with cols[idx]:
      jobs = db.query(Job).filter(Job.status == status).all()
      
      st.markdown(f"### {status.upper()}")
      st.markdown(f"**{len(jobs)} jobs**")
      st.markdown("---")
      
      for job in jobs:
        with st.container():
          st.markdown(f"**{job.title}**")
          st.caption(job.company)
          
          if st.button("👁️", key=f"view_kanban_{job.id}"):
            st.session_state['selected_job_id'] = job.id
            st.session_state['show_job_detail'] = True
            st.rerun()
          
          st.markdown("---")
