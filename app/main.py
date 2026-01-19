from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.models import Job
from app.api.jobs import router as jobs_router

app = FastAPI(title="JobTrail API")

# Create tables
Base.metadata.create_all(bind=engine)


app.include_router(jobs_router)


@app.get("/")
def root():
  return {"message": "JobTrail API is running"}
