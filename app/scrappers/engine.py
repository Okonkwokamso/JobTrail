from typing import List, Type
from sqlalchemy.orm import Session
from rich.console import Console
from .base import BaseScraper
from app.services import job_service
from app.schemas.jobs import JobCreate
from app.utils.logging import get_logger

logger = get_logger(__name__)

console = Console()

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
    console.print(f"[blue]🔎 Running scraper:[/blue] {scraper.source_name}")

    jobs = scraper.scrape()

    if not jobs:
      console.print(f"[yellow]⚠️ No jobs found from {scraper.source_name}[/yellow]")
      return 0
    
    logger.info(f"Found {len(jobs)} jobs from {scraper.source_name}")

    saved_count = 0
    duplicate_count = 0
    error_count = 0

    for job_data in jobs:
      try:
        job_schema = JobCreate(**job_data)
        result = job_service.create_job(self.db, job_schema)

        if result:
          saved_count += 1
        else:
          duplicate_count += 1
      except Exception as e:
        error_count += 1
        logger.error(f"Error saving job from {scraper.source_name}: {str(e)}")
    
    logger.info(f"Scraper {scraper.source_name} results: {saved_count} saved, {duplicate_count} duplicates, {error_count} errors")

    #console.print(f"[green]Saved {saved_count} jobs from {scraper.source_name}[/green]")
    return saved_count

  def run_multiple(self, scrapers: List[BaseScraper]) -> int:
    """
    Runs multiple scrapers.
    """
    total = 0
    for scraper in scrapers:
      try:
        count = self.run_scraper(scraper)
        total += count
      except Exception as e:
        logger.error(f"Error running scraper {scraper.source_name}: {str(e)}")

    #console.print(f"Total jobs saved: [green]{total}[/green]")
    return total
