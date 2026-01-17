import uuid
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.sqlite import BLOB
from datetime import datetime, timezone

from app.db.base import Base


class Job(Base):
  __tablename__ = "jobs"

  id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
  title = Column(String, nullable=False)
  company = Column(String, nullable=False)
  location = Column(String, nullable=False)
  job_type = Column(String, nullable=False)  # remote, hybrid, onsite
  salary = Column(String, nullable=True)
  description = Column(Text, nullable=True)

  url = Column(String, nullable=False, unique=True)
  source = Column(String, nullable=False)

  date_posted = Column(DateTime, nullable=True)
  status = Column(String, default="saved")  # saved, applied, interview...
  notes = Column(Text, nullable=True)

  created_at = Column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc))
