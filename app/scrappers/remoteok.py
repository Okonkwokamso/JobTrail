from typing import List, Dict, Any
import logging
from rich.console import Console
from app.scrappers.base import BaseScraper

console = Console()
logger = logging.getLogger(__name__)


class RemoteOKScraper(BaseScraper):
  """Scraper for RemoteOK using their public API."""
  
  API_URL = "https://remoteok.com/api"
  
  def __init__(self):
    super().__init__(source_name="remoteok")
    # Update headers for API access
    self.headers.update({
      'User-Agent': 'JobTrail/1.0 (Job Application Tracker)'
    })
  
  def scrape(self) -> List[Dict[str, Any]]:
    """
    Fetch and parse jobs from RemoteOK API.
    
    Returns:
      List of normalized job dictionaries
    """
    try:
      logger.info("Fetching jobs from RemoteOK API...")
      
      # Use the inherited fetch_page method
      response = self.fetch_page(self.API_URL)
      
      # Parse JSON response
      import json
      data = json.loads(response)
      
      # First item is metadata, skip it
      jobs = data[1:] if len(data) > 1 else []
      
      logger.info(f"Found {len(jobs)} jobs from RemoteOK")
      
      # Parse each job and normalize
      normalized_jobs = []
      for job in jobs:
        parsed_job = self._parse_job(job)
        if parsed_job:
          normalized_jobs.append(self.normalize_job(parsed_job))
      
      logger.info(f"Successfully parsed {len(normalized_jobs)} jobs")
      return normalized_jobs
      
    except Exception as e:
      logger.exception(f"Error scraping RemoteOK: {e}")
      return []
  
  def _parse_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant fields from RemoteOK API response.
    """
    try:
      # Extract salary information
      salary = self._format_salary(job_data)
      
      # Get location (RemoteOK jobs are remote, but may have preferred timezone)
      location = job_data.get('location', 'Remote - Worldwide')
      
      # Build apply URL
      apply_url = job_data.get('apply_url')
      if not apply_url:
        job_id = job_data.get('id')
        apply_url = f"https://remoteok.com/l/{job_id}" if job_id else self.API_URL
      
      # Determine job type
      job_type = self._determine_job_type(job_data)
      
      return {
        "title": job_data.get('position', 'Untitled Position'),
        "company": job_data.get('company', 'Unknown Company'),
        "location": location,
        "job_type": job_type,
        "salary": salary,
        "description": job_data.get('description', ''),
        "url": apply_url,
      }
      
    except Exception as e:
      logger.exception(f"Error parsing job: {e}")
      return None
  
  def _format_salary(self, job_data: Dict[str, Any]) -> str:
    """
    Format salary information into a string.
    """
    salary_min = job_data.get('salary_min')
    salary_max = job_data.get('salary_max')
    
    if salary_min and salary_max:
      return f"${salary_min:,} - ${salary_max:,}"
    elif salary_min:
      return f"${salary_min:,}+"
    elif salary_max:
      return f"Up to ${salary_max:,}"
    
    return None
  
  def _determine_job_type(self, job_data: Dict[str, Any]) -> str:
    """
    Determine job type from tags.
    """
    tags = [tag.lower() for tag in job_data.get('tags', [])]
    
    if 'contract' in tags:
      return 'contract'
    elif 'part-time' in tags or 'parttime' in tags:
      return 'part-time'
    else:
      return 'full-time'  # Default for RemoteOK





