import streamlit as st
import pandas as pd
from app.scrappers.remoteok import RemoteOKScraper
from app.scrappers.weworkremotely import WeWorkRemotelyScraper
from app.scrappers.remotive import RemotiveScraper
from app.scrappers.engine import ScraperEngine
from app.utils.logging import get_logger

logger = get_logger(__name__)


def render(db):
  """Render scraping page."""
  st.title("🔍 Scrape Jobs")
  st.markdown("Discover new job opportunities from multiple sources")
  
  scrapers_available = {
    "RemoteOK": RemoteOKScraper,
    "WeWorkRemotely": WeWorkRemotelyScraper,
    "Remotive": RemotiveScraper
  }
  
  col1, col2 = st.columns([1, 2])
  
  with col1:
    st.markdown("### Select Sources")
    selected_scrapers = []
    
    for name, scraper_class in scrapers_available.items():
      if st.checkbox(name, value=True):
        selected_scrapers.append((name, scraper_class))
    
    st.markdown("---")
    scrape_all = st.button("🚀 Start Scraping", type="primary", width='stretch')
  
  with col2:
    st.markdown("### Scraping Results")
    
    if scrape_all and selected_scrapers:
      _run_scrapers(db, selected_scrapers)
    elif scrape_all and not selected_scrapers:
      st.warning("Please select at least one source to scrape.")


def _run_scrapers(db, selected_scrapers):
  """Run selected scrapers and display results."""
  progress_bar = st.progress(0)
  status_text = st.empty()
  results_container = st.container()
  
  total_scrapers = len(selected_scrapers)
  engine = ScraperEngine(db)
  all_results = []
  
  for idx, (name, scraper_class) in enumerate(selected_scrapers):
    status_text.text(f"Scraping {name}...")
    
    try:
      scraper = scraper_class()
      count = engine.run_scraper(scraper)
      all_results.append({
        'Source': name,
        'Status': '✅ Success',
        'Jobs Found': count
      })
    except Exception as e:
      logger.error(f"Error scraping {name}: {e}")
      all_results.append({
        'Source': name,
        'Status': '❌ Failed',
        'Jobs Found': 0
      })
    
    progress_bar.progress((idx + 1) / total_scrapers)
  
  status_text.text("✅ Scraping complete!")
  
  with results_container:
    results_df = pd.DataFrame(all_results)
    st.dataframe(results_df, width='stretch', hide_index=True)
    
    total_found = sum([r['Jobs Found'] for r in all_results])
    st.success(f"🎉 Found {total_found} new jobs across all sources!")
