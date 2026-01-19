from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class JobBase(BaseModel):
  title: str
  company: str
  location: str
  job_type: str
  salary: Optional[str] = None
  description: Optional[str] = None
  url: str
  source: str
  # date_posted: Optional[datetime] = None
  # status: str = "saved"
  # notes: Optional[str] = None


class JobCreate(JobBase):
  pass


class JobUpdate(BaseModel):
  title: Optional[str] = None
  company: Optional[str] = None
  location: Optional[str] = None
  job_type: Optional[str] = None
  salary: Optional[str] = None
  description: Optional[str] = None
  status: Optional[str] = None
  notes: Optional[str] = None


class JobOut(JobBase):
  id: str
  title: str
  status: str
  notes: Optional[str] = None
  created_at: datetime

  class Config:
    orm_mode = True
