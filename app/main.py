from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine
from app.models import job

app = FastAPI(title="JobTrail API")

# Create tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
  return {"message": "JobTrail API is running"}
