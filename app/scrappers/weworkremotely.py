from typing import List, Dict, Any
from rich.console import Console
from app.scrappers.base import BaseScraper
from app.utils.logging import get_logger

logger = get_logger(__name__)

console = Console()

class WeWorkRemotelyScraper(BaseScraper):
  
  JOBS_URL = "https://weworkremotely.com/remote-jobs"
  
  def __init__(self):
    super().__init__(source_name="weworkremotely")
  
  def normalize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
    """Override to include job_type field."""
    return {
      "title": raw_job.get("title"),
      "company": raw_job.get("company"),
      "location": raw_job.get("location"),
      "job_type": raw_job.get("job_type"),
      "salary": raw_job.get("salary"),
      "url": raw_job.get("url"),
      "description": raw_job.get("description"),
      "source": self.source_name,
    }
  
  def scrape(self) -> List[Dict[str, Any]]:
    try:
      from playwright.sync_api import sync_playwright
    except ImportError:
      logger.error(
        "Playwright not installed. Run: pip install playwright && playwright install chromium"
      )
      return []
    
    all_jobs = []
    
    try:
      logger.info("Launching browser to scrape WeWorkRemotely...")
      
      with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.set_default_timeout(60000)  # 60 seconds
        
        # Navigate to jobs page
        logger.info(f"Loading {self.JOBS_URL}...")
        page.goto(self.JOBS_URL, wait_until='domcontentloaded', timeout=60000)
        
        # Wait a bit for JavaScript to render jobs
        page.wait_for_timeout(3000)  # Wait 3 seconds
        
        # Wait for job listings to load (or timeout gracefully)
        try:
          page.wait_for_selector('section.jobs li.feature', timeout=10000)
        except Exception:
          logger.warning("Job selector not found, trying alternative selectors...")
        
        # Extract all job listings
        job_elements = page.query_selector_all('li.feature')
        
        # If no jobs found with primary selector, try alternatives
        if not job_elements:
          logger.info("Trying alternative job selectors...")
          job_elements = (
            page.query_selector_all('article.job') or
            page.query_selector_all('section.jobs li') or
            page.query_selector_all('[data-job-id]')
          )
        
        logger.info(f"Found {len(job_elements)} job listings")
        
        for job_elem in job_elements:
          parsed_job = self._parse_job_element(job_elem)
          if parsed_job:
            all_jobs.append(self.normalize_job(parsed_job))
        
        browser.close()
      
      logger.info(f"Successfully scraped {len(all_jobs)} jobs from WeWorkRemotely")
      
      self.polite_delay()
      
      return all_jobs
      
    except Exception as e:
      logger.error(f"Error scraping WeWorkRemotely: {e}")
      logger.exception("Full traceback:")
      return []
  
  def _parse_job_element(self, element) -> Dict[str, Any]:
    """
    Extract job data from Playwright element.
    """
    try:
      # Skip ads (they have title--ad class or link to external sites)
      title_elem = element.query_selector('h3.new-listing__header__title')
      if title_elem:
        title_classes = title_elem.get_attribute('class') or ''
        if 'title--ad' in title_classes:
          logger.debug("Skipping ad listing")
          return None
      
      # Get the job link - must be an internal job link
      link = element.query_selector('a.listing-link--unlocked')
      if not link:
        link = element.query_selector('a[href^="/remote-jobs/"]')
      
      if not link:
        logger.debug("No valid job link found")
        return None
      
      job_url = link.get_attribute('href')
      
      # Skip if it's an external link (ads)
      if job_url and ('http' in job_url or 'link.' in job_url):
        logger.debug(f"Skipping external link: {job_url}")
        return None
      
      if job_url and not job_url.startswith('http'):
        job_url = f"https://weworkremotely.com{job_url}"
      
      # Extract title from h3
      title = None
      if title_elem:
        title = title_elem.inner_text().strip()
      
      if not title:
        return None
      
      # Extract company from the company profile link or flag logo tooltip
      company = 'Unknown Company'
      company_link = element.query_selector('.tooltip--flag-logo a')
      if company_link:
        company_href = company_link.get_attribute('href')
        if company_href and '/company/' in company_href:
          # Extract company name from URL
          company = company_href.split('/company/')[-1].replace('-', ' ').title()
      
      # Try to get company from tooltip text
      tooltip = element.query_selector('.tooltip--flag-logo__tooltiptext')
      if tooltip and 'View Company Profile' not in tooltip.inner_text():
        company = tooltip.inner_text().strip()
      
      # Extract region/location from new-listing__header__icons
      location = 'Remote - Worldwide'
      region_elem = element.query_selector('.new-listing__header__icons .region')
      if region_elem:
        location = region_elem.inner_text().strip()
      
      # Extract tags/category
      tags_elem = element.query_selector('.new-listing__header__icons')
      tags_text = tags_elem.inner_text() if tags_elem else ''
      
      # Determine job type from tags
      job_type = self._determine_job_type_from_text(tags_text)
      
      return {
        "title": title,
        "company": company,
        "location": location,
        "job_type": job_type,
        "salary": None,
        "url": job_url,
        "description": title,
      }
      
    except Exception as e:
      logger.error(f"Error parsing job element: {e}")
      return None
  
  def _determine_job_type(self, element) -> str:
    """
    Determine job type from element.
    """
    try:
      # Get all text from the icons section
      icons = element.query_selector('.new-listing__header__icons')
      if icons:
        text = icons.inner_text().lower()
        return self._determine_job_type_from_text(text)
    except Exception:
      pass
    
    return 'remote'
  
  def _determine_job_type_from_text(self, text: str) -> str:
    """
    Determine job type from text content.
    """
    text_lower = text.lower()
    
    if 'contract' in text_lower or 'freelance' in text_lower:
      return 'contract'
    elif 'part-time' in text_lower or 'part time' in text_lower:
      return 'part-time'
    elif 'full-time' in text_lower or 'full time' in text_lower:
      return 'full-time'
    
    return 'remote'
