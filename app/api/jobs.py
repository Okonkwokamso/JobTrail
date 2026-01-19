from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.deps import get_db
from app.models import Job
from app.schemas.jobs import JobCreate, JobUpdate, JobOut
from app.services.job_service import create_job, get_all_jobs, get_job_by_id, delete_job, update_job

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# Create a job
@router.post("/", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
  return create_job(db, job)

#List all jobs
@router.get("/", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)):
  return get_all_jobs(db)

#Get one job
@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: str, db: Session = Depends(get_db)):
  job = get_job_by_id(db, job_id)

  if not job:
    raise HTTPException(status_code=404, detail="Job not found")
  return job

# Update a job
@router.put("/{job_id}", response_model=JobOut)
def update_job(job_id: str, payload: JobUpdate, db: Session = Depends(get_db)):
  job = update_job(db, job_id, payload)
  if not job:
    raise HTTPException(status_code=404, detail="Job not found")

  return job


# Delete a job
@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: str, db: Session = Depends(get_db)):
  job = delete_job(db, job_id)
  if not job:
    raise HTTPException(status_code=404, detail="Job not found")
  
  return None