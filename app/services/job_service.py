from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.job import Job
from app.schemas.jobs import JobCreate, JobUpdate, JobFilters, JobStats
from app.utils.logging import get_logger

logger = get_logger(__name__)


def get_jobs(
  db: Session,
  filters: Optional[JobFilters]
) -> List[Job]:
  """    
  Returns:
    List of Job objects matching filters
  """
  query = db.query(Job)
  
  # Apply filters if provided
  if filters:
    # Search in title and company
    if filters.search:
      search_term = f"%{filters.search}%"
      query = query.filter(
        or_(
          Job.title.ilike(search_term),
          Job.company.ilike(search_term),
          Job.description.ilike(search_term)
        )
      )
    
    # Filter by status
    if filters.status:
      query = query.filter(Job.status == filters.status)
    
    # Filter by source
    if filters.source:
      query = query.filter(Job.source == filters.source)
    
    # Filter by job type
    if filters.job_type:
      query = query.filter(Job.job_type == filters.job_type)
    
    # Filter by location
    if filters.location:
      location_term = f"%{filters.location}%"
      query = query.filter(Job.location.ilike(location_term))
    
    # Filter by date range
    if filters.date_from:
      query = query.filter(Job.created_at >= filters.date_from)
    
    if filters.date_to:
      query = query.filter(Job.created_at <= filters.date_to)
    
    # Default ordering: newest first
    query = query.order_by(desc(Job.created_at))

    # Pagination
    if filters.offset:
      query = query.offset(filters.offset)
    
    if filters.limit:
      query = query.limit(filters.limit)
  

  
  return query.all()


def get_job_by_id(db: Session, job_id: str) -> Optional[Job]:
  """
  Returns:
    Job object or None if not found
  """
  return db.query(Job).filter(Job.id == job_id).first()


def create_job(db: Session, job_data: JobCreate) -> Optional[Job]:
  """
  Returns:
    Created Job object or None if duplicate
  """
  # Check if job with this URL already exists
  existing_job = db.query(Job).filter(Job.url == job_data.url).first()
  
  if existing_job:
    logger.debug(f"Job already exists: {job_data.title} at {job_data.company}")
    return None
  
  try:
    # Create new job
    new_job = Job(**job_data.model_dump())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    logger.debug(f"Created job: {job_data.title} at {job_data.company}")
    return new_job
  
  except IntegrityError as e:
    db.rollback()
    logger.warning(f"Database integrity error (likely duplicate): {job_data.url}")
    return None
  except Exception as e:
    db.rollback()
    logger.error(f"Error creating job: {e}")
    raise


def update_job(
  db: Session,
  job_id: str,
  job_data: JobUpdate
) -> Optional[Job]:
  """ 
  Returns:
    Updated Job object or None if not found
  """
  job = get_job_by_id(db, job_id)
  
  if not job:
    logger.warning(f"Job {job_id} not found for update")
    return None
  
  try:
    # Update only provided fields
    update_data = job_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
      setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    logger.info(f"Updated job: {job.title}")
    return job
  
  except Exception as e:
    db.rollback()
    logger.error(f"Error updating job {job_id}: {e}")
    raise


def delete_job(db: Session, job_id: str) -> bool:
  """ 
  Returns:
    True if deleted, False if not found
  """
  job = get_job_by_id(db, job_id)
  
  if not job:
    logger.warning(f"Job {job_id} not found for deletion")
    return False
  
  try:
    db.delete(job)
    db.commit()
    logger.info(f"Deleted job: {job.title}")
    return True
  
  except Exception as e:
    db.rollback()
    logger.error(f"Error deleting job {job_id}: {e}")
    raise


def get_job_stats(db: Session) -> JobStats:
  """
  Returns:
    JobStats object with counts and breakdowns
  """
  total = db.query(Job).count()
  
  # Group by status
  by_status = db.query(
    Job.status,
    func.count(Job.id)
  ).group_by(Job.status).all()
  
  # Group by source
  by_source = db.query(
    Job.source,
    func.count(Job.id)
  ).group_by(Job.source).all()

  # Group by job type
  by_job_type = db.query(
    Job.job_type, 
    func.count(Job.id)
  ).group_by(Job.job_type).all()
  
  # Recent jobs (last 7 days)
  recent_7days = db.query(Job).filter(
    Job.created_at >= datetime.now() - timedelta(days=7)
  ).count()

  # Recent jobs (last 30 days)
  recent_30days = db.query(Job).filter(
    Job.created_at >= datetime.now() - timedelta(days=30)
  ).count()

  
  return JobStats(
    total=total,
    by_status=dict(by_status),
    by_source=dict(by_source),
    by_job_type=dict(by_job_type),
    recent_7days=recent_7days,
    recent_30days=recent_30days,
  )


def update_job_status(
  db: Session,
  job_id: str,
  new_status: str
) -> Optional[Job]:
  """
  Returns:
    Updated Job or None
  """
  return update_job(
    db,
    job_id,
    JobUpdate(status=new_status)
  )


def bulk_update_status(
  db: Session,
  job_ids: List[str],
  new_status: str
) -> int:
  """
  Update status for multiple jobs at once.
 
  Returns:
    Number of jobs updated
  """
  try:
    count = db.query(Job).filter(
      Job.id.in_(job_ids)
    ).update(
      {Job.status: new_status},
      synchronize_session=False
    )
    db.commit()
    logger.info(f"Bulk updated {count} jobs to status: {new_status}")
    return count
  except Exception as e:
    db.rollback()
    logger.error(f"Error in bulk update: {e}")
    raise
