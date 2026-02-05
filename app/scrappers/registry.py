from .remoteok import RemoteOKScraper
from .weworkremotely import WeWorkRemotelyScraper
from .remotive import RemotiveScraper

def get_all_scrapers():
  return [
    RemoteOKScraper(),
    WeWorkRemotelyScraper(),
    RemotiveScraper(),
  ]


def get_scraper_by_name(name: str):
  for scraper in get_all_scrapers():
    if scraper.source_name.lower() == name.lower():
      return scraper
  return None
