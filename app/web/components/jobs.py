import streamlit as st
from app.web.database import get_jobs_with_filters
from app.web.utils import status_badge, jobs_to_dataframe
from app.models.job import Job


def render(db):
  """Render jobs listing page."""
  st.title("💼 All Jobs")
  
  # Filters
  with st.expander("🔍 Filters", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
      search = st.text_input("Search", placeholder="Job title or company")
    
    with col2:
      sources = ['All'] + list(set([s for s, in db.query(Job.source).distinct().all()]))
      source_filter = st.selectbox("Source", sources)
    
    with col3:
      statuses = ['All', 'saved', 'applied', 'interview', 'offer', 'rejected']
      status_filter = st.selectbox("Status", statuses)
    
    with col4:
      job_types = ['All'] + list(set([jt for jt, in db.query(Job.job_type).distinct().all() if jt]))
      type_filter = st.selectbox("Job Type", job_types)
  
  # Build filters dict
  filters = {
    'search': search if search else None,
    'source': source_filter,
    'status': status_filter,
    'job_type': type_filter
  }
  
  # Get filtered jobs
  jobs = get_jobs_with_filters(db, filters)
  df = jobs_to_dataframe(jobs)
  
  if not df.empty:
    st.markdown(f"**Showing {len(df)} jobs**")
    
    # Display options
    view_mode = st.radio("View as:", ["Cards", "Table"], horizontal=True)
    
    if view_mode == "Table":
      st.dataframe(
        df[['Title', 'Company', 'Location', 'Type', 'Status', 'Source', 'Date Added']],
        use_container_width=True,
        hide_index=True
      )
    else:
      _render_card_view(df, db)
  else:
    st.info("No jobs found matching your filters.")


def _render_card_view(df, db):
  """Render jobs in card view."""
  for idx, row in df.iterrows():
    with st.container():
      col1, col2, col3 = st.columns([4, 2, 1])
      
      with col1:
        st.markdown(f"### {row['Title']}")
        st.markdown(f"**{row['Company']}** • {row['Location']}")
        if row['Salary'] != 'Not specified':
          st.caption(f"💰 {row['Salary']}")
      
      with col2:
        st.markdown(status_badge(row['Status']), unsafe_allow_html=True)
        st.caption(f"📅 {row['Date Added']}")
        st.caption(f"🔗 Source: {row['Source']}")
      
      with col3:
        if st.button("View Details", key=f"view_{row['ID']}"):
          st.session_state['selected_job_id'] = row['ID']
          st.session_state['show_job_detail'] = True
        
        if st.button("🔗 Apply", key=f"apply_{row['ID']}"):
          st.markdown(f"[Open Job]({row['URL']})")
      
      st.markdown("---")
  
  # Job detail modal
  if st.session_state.get('show_job_detail'):
    _render_job_detail(db)


def _render_job_detail(db):
  """Render job detail modal."""
  job_id = st.session_state.get('selected_job_id')
  job = db.query(Job).filter(Job.id == job_id).first()
  
  if job:
    with st.expander(f"📋 Job Details: {job.title}", expanded=True):
      col1, col2 = st.columns([2, 1])
      
      with col1:
        st.markdown(f"**Company:** {job.company}")
        st.markdown(f"**Location:** {job.location or 'Remote'}")
        st.markdown(f"**Type:** {job.job_type or 'N/A'}")
        if job.salary:
          st.markdown(f"**Salary:** {job.salary}")
        
        st.markdown("**Description:**")
        st.write(job.description or "No description available")
        
        st.markdown(f"[🔗 View Original Posting]({job.url})")
      
      with col2:
        st.markdown("**Update Status**")
        new_status = st.selectbox(
          "Status",
          ['saved', 'applied', 'interview', 'offer', 'rejected'],
          index=['saved', 'applied', 'interview', 'offer', 'rejected'].index(job.status),
          key=f"status_{job.id}"
        )
        
        if st.button("Update Status"):
          job.status = new_status
          db.commit()
          st.success(f"Status updated to {new_status}!")
          st.rerun()
        
        st.markdown("**Notes**")
        notes = st.text_area(
          "Notes",
          value=job.notes or "",
          key=f"notes_{job.id}",
          label_visibility="collapsed"
        )
        
        if st.button("Save Notes"):
          job.notes = notes
          db.commit()
          st.success("Notes saved!")
      
      if st.button("Close"):
        st.session_state['show_job_detail'] = False
        st.rerun()
