import requests
from .base import BaseScraper
from app.schemas.jobs import JobCreate
from app.utils.logging import get_logger

logger = get_logger(__name__)

class RemotiveScraper(BaseScraper):
  def __init__(self):
    super().__init__("Remotive")

  url = "https://remotive.com/api/remote-jobs"

  def scrape(self) -> list[dict]:
    try:
      raw_jobs = self.fetch_jobs()
      return self.parse_jobs(raw_jobs)
    except Exception as e:
      logger.exception(f"Error scraping Remotive: {str(e)}")
      return []
  
  def fetch_jobs(self) -> list[dict]:
    response = requests.get(self.url, timeout=10)
    response.raise_for_status()

    data = response.json()
    return data.get("jobs", [])
  
  def parse_jobs(self, raw_jobs: list[dict]) -> list[dict]:

    jobs = []
    for job in raw_jobs :
      jobs.append(
        {
          "title": job.get("title"),
          "company": job.get("company_name"),
          "location": job.get("candidate_required_location"),
          "job_type": job.get('job_type'),
          "url": job.get("url"),
          "source": self.source_name,
        }
      )

    return jobs