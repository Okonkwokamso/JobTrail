import typer
from typing import Optional
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.scrappers.engine import ScraperEngine
from app.scrappers.weworkremotely import WeWorkRemotelyScraper
from app.scrappers.remoteok import RemoteOKScraper

#scrape_app = typer.Typer(help="Scrape job sources")

app = typer.Typer()

SCRAPERS = {
  "weworkremotely": WeWorkRemotelyScraper,
  "remoteok": RemoteOKScraper,
}


def get_db() -> Session:
  return SessionLocal()


@app.command()
def scrape(
  source: Optional[str] = typer.Option(None, "--source", "-s", help="Scrape a single source"),
  all: bool = typer.Option(False, "--all", help="Scrape all sources"),
):
  """
  Run job scrapers and save results to the database.
  """

  if not source and not all:
    typer.echo("❌ Please specify --source or --all")
    raise typer.Exit(code=1)

  if source and all:
    typer.echo("❌ Use either --source or --all, not both")
    raise typer.Exit(code=1)

  db = get_db()
  engine = ScraperEngine(db)

  if all:
    scrapers = [cls() for cls in SCRAPERS.values()]
    total = engine.run_multiple(scrapers)
    typer.echo(f"✅ Finished scraping all sources. Total jobs saved: {total}")
  else:
    source = source.lower()

    if source not in SCRAPERS:
      typer.echo(f"❌ Unknown source: {source}")
      typer.echo(f"Available sources: {', '.join(SCRAPERS.keys())}")
      raise typer.Exit(code=1)

    scraper = SCRAPERS[source]()
    count = engine.run_scraper(scraper)
    typer.echo(f"✅ Finished scraping {source}. Jobs saved: {count}")

  db.close()
