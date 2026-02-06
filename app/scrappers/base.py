from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests
import time
import random
import logging
from app.utils.exceptions import (ScraperConnectionError, ScraperParseError, ScraperTimeoutError)

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
  """
  Abstract base class for all job scrapers.
  """

  def __init__(self, source_name: str):
    self.source_name = source_name

    # Basic headers to reduce blocking
    self.headers = {
      "User-Agent": "Mozilla/5.0"
    }

    logger.info(f"Initialized scraper for source: {self.source_name}")

  def fetch_page(self, url: str, timeout: int = 10) -> str:
    """
    Handles HTTP request logic centrally for all scrapers.
    """

    try:
      logger.debug(f"Fetching: {url}")
      response = requests.get(url, headers=self.headers, timeout=timeout)
      response.raise_for_status()
      return response.text
    except requests.Timeout:
      raise ScraperTimeoutError(
        f"Request to {url} timed out after {timeout}s",
        details={"url": url, "timeout": timeout}
      )
    except requests.ConnectionError as e:
      raise ScraperConnectionError(
        f"Failed to connect to {url}",
        details={"url": url, "error": str(e)}
      )
    except requests.HTTPError as e:
      raise ScraperConnectionError(
        f"HTTP error {e.response.status_code} from {url}",
        details={"url": url, "status_code": e.response.status_code}
      )
    except Exception as e:
      raise ScraperConnectionError(
        f"Unexpected error fetching {url}: {str(e)}",
        details={"url": url, "error": str(e)}
      )

  def polite_delay(self, min_delay: float = 1, max_delay: float = 3):
    """
    Prevents hammering websites too fast.
    """
    delay = random.uniform(min_delay, max_delay)
    logger.debug(f"Waiting {delay:.2f}s before next request")
    time.sleep(delay)

  @abstractmethod
  def scrape(self) -> List[Dict[str, Any]]:
    """
    Every scraper MUST implement this method.

    It should return a list of dicts like:
    [
      {
        "title": "...",
        "company": "...",
        "location": "...",
        "url": "...",
        "description": "...",
      }
    ]
    """
    raise NotImplementedError
  
  def normalize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensures every scraper returns consistent fields.
    """
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
