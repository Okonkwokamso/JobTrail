from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


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

class JobFilters(BaseModel):
  """Filter parameters for job queries."""
  search: Optional[str] = Field(None, description="Search in title and company")
  status: Optional[str] = Field(None, description="Filter by status")
  source: Optional[str] = Field(None, description="Filter by source")
  job_type: Optional[str] = Field(None, description="Filter by job type")
  location: Optional[str] = Field(None, description="Filter by location")
  salary_min: Optional[int] = Field(None, description="Minimum salary")
  salary_max: Optional[int] = Field(None, description="Maximum salary")
  date_from: Optional[datetime] = Field(None, description="Filter jobs added after this date")
  date_to: Optional[datetime] = Field(None, description="Filter jobs added before this date")
  limit: Optional[int] = Field(100, description="Maximum number of results")
  offset: Optional[int] = Field(0, description="Pagination offset")


class JobStats(BaseModel):
  """Job statistics model."""
  total: int
  by_status: Dict[str, int]
  by_source: Dict[str, int]
  by_job_type: Dict[str, int]
  recent_7days: int
  recent_30days: int