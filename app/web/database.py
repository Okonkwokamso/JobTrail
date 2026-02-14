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