from sqlalchemy.orm import Session
from uuid import UUID
from app.models import Job
from app.schemas.jobs import JobCreate, JobUpdate


def create_job(db: Session, job: JobCreate) -> Job:
  # Skip duplicates
  if job_exists(db, job.url):
    raise ValueError("Job with this URL already exists.")
  
  # Create a new job record in the database.

  job_data = job.model_dump()
  db_job = Job(**job_data)

  # Save to database
  db.add(db_job)
  db.commit()
  db.refresh(db_job)

  return db_job


def get_all_jobs(db: Session):
  """
  Return all jobs from the database.
  """
  return db.query(Job).order_by(Job.created_at.desc()).all()

def get_job_by_id(db: Session, job_id: str) -> Job | None:
  """
  Retrieve a job by its ID.
  """

  return db.query(Job).filter(Job.id == job_id).first()

def update_job(db: Session, job_id: str, job_data: JobUpdate) -> Job | None:
  """
  Update a job with the provided fields.
  """

  job = get_job_by_id(db, job.id)

  if not job:
    return None
  
  update_data = job_data.model_dump(exclude_unset=True)

  for key, value in update_data.items():
    setattr(job, key, value)

  db.commit()
  db.refresh(job)

  return job

def delete_job(db: Session, job_id: str) -> bool:
  """
  Delete a job by its ID.
  """

  job = get_job_by_id(db, job_id)

  if not job:
    return False
  
  db.delete(job)
  db.commit()

  return True

def job_exists(db: Session, url: str) -> bool:
  """
  Check if a job with the given URL already exists.
  """

  return db.query(Job).filter(Job.url == url).first() is not None