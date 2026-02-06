from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from app.models import Job
from app.schemas.jobs import JobCreate, JobUpdate
from app.utils.logging import get_logger

logger = get_logger(__name__)


def create_job(db: Session, job: JobCreate) -> Job | None:
  # Skip duplicates
  existing_job = db.query(Job).filter(Job.url == job.url).first()
  if existing_job:
    logger.debug(f"Job with URL {job.url} already exists. Skipping.")
    return None
  
  # if job_exists(db, job.url):
  #   raise ValueError("Job with this URL already exists.")
  

  # Create a new job record in the database.
  try:
    job_data = job.model_dump()
    db_job = Job(**job_data)

    # Save to database
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    return db_job
  
  except IntegrityError as e:
    db.rollback()
    logger.warning(f"Database integrity error (likely duplicate): {job_data.url}")
    return None
  except Exception as e:
    db.rollback()
    logger.error(f"Error creating job: {str(e)}")
    raise


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