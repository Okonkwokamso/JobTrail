from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests
import time
import random


class BaseScraper(ABC):
  """
  Abstract base class for all job scrapers.
  Every scraper (Indeed, RemoteOK, etc.) must inherit from this.
  """

  def __init__(self, source_name: str):
    self.source_name = source_name

    # Basic headers to reduce blocking
    self.headers = {
      "User-Agent": "Mozilla/5.0 (JobTrail Bot 1.0)"
    }

  def fetch_page(self, url: str) -> str:
    """
    Handles HTTP request logic centrally for all scrapers.
    """
    response = requests.get(url, headers=self.headers, timeout=10)
    response.raise_for_status()
    return response.text

  def polite_delay(self):
    """
    Prevents hammering websites too fast (important later).
    """
    time.sleep(random.uniform(1, 3))

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
      "url": raw_job.get("url"),
      "description": raw_job.get("description"),
      "source": self.source_name,
    }
