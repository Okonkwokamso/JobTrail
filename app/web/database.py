import streamlit as st
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.db.session import SessionLocal
from app.models.job import Job


@st.cache_resource
def get_db() -> Session:
  """Get database session (cached)."""
  return SessionLocal()


def get_job_stats(db: Session) -> dict:
  """Get statistics about jobs."""
  total = db.query(Job).count()
  by_status = db.query(Job.status, func.count(Job.id)).group_by(Job.status).all()
  by_source = db.query(Job.source, func.count(Job.id)).group_by(Job.source).all()

  recent_7days = db.query(Job).filter(
    Job.created_at >= datetime.now() - timedelta(days=7)
  ).count()

  return {
    'total': total,
    'by_status': dict(by_status),
    'by_source': dict(by_source),
    'recent_7days': recent_7days
  }


def get_jobs_with_filters(db: Session, filters: dict = None):
  """Get jobs with optional filters."""
  query = db.query(Job)

  if filters:
    if filters.get('search'):
      search_term = f"%{filters['search']}%"
      query = query.filter(
        (Job.title.ilike(search_term)) |
        (Job.company.ilike(search_term))
      )

    if filters.get('status') and filters['status'] != 'All':
      query = query.filter(Job.status == filters['status'])

    if filters.get('source') and filters['source'] != 'All':
      query = query.filter(Job.source == filters['source'])

    if filters.get('job_type') and filters['job_type'] != 'All':
      query = query.filter(Job.job_type == filters['job_type'])

  return query.order_by(desc(Job.created_at)).all()

