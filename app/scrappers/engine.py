from typing import List, Type
from sqlalchemy.orm import Session
from .base import BaseScraper
from app.services import job_service
from app.schemas.jobs import JobCreate


class ScraperEngine:
  """
  Responsible for running scrapers and saving results to DB.
  """

  def __init__(self, db: Session):
    self.db = db

  def run_scraper(self, scraper: BaseScraper) -> int:
    """
    Runs a single scraper and saves jobs.
    Returns number of jobs saved.
    """
    print(f"Running scraper: {scraper.source_name}")

    jobs = scraper.scrape()
    saved_count = 0

    for job_data in jobs:
      try:
        job_schema = JobCreate(**job_data)
        job_service.create_job(self.db, job_schema)
        saved_count += 1
      except Exception as e:
        print(f"Skipping job due to error: {e}")

    print(f"Saved {saved_count} jobs from {scraper.source_name}")
    return saved_count

  def run_multiple(self, scrapers: List[BaseScraper]) -> int:
    """
    Runs multiple scrapers.
    """
    total = 0
    for scraper in scrapers:
      total += self.run_scraper(scraper)

    print(f"Total jobs saved: {total}")
    return total
