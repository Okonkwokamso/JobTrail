import typer
from typing import Optional
from rich.console import Console
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.scrappers.engine import ScraperEngine
from app.scrappers.weworkremotely import WeWorkRemotelyScraper
from app.scrappers.remoteok import RemoteOKScraper
from app.scrappers.remotive import RemotiveScraper
from app.utils.logging import setup_logging, get_logger
from app.utils.error_handler import handle_exceptions, ErrorContext


# Initialize logging
setup_logging(log_level="INFO", log_to_file=True)
logger = get_logger(__name__)

app = typer.Typer()
console = Console()

SCRAPERS = {
  "weworkremotely": WeWorkRemotelyScraper,
  "remoteok": RemoteOKScraper,
  "remotive": RemotiveScraper,

}


def get_db() -> Session:
  return SessionLocal()


@app.command()
@handle_exceptions
def scrape(
  source: Optional[str] = typer.Option(None, "--source", "-s", help="Scrape a single source"),
  all: bool = typer.Option(False, "--all", help="Scrape all sources"),
  debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
  """
  Run job scrapers and save results to the database.
  """

  if debug:
    import logging
    logging.getLogger().setLevel(logging.DEBUG)
    logger.debug("Debug mode enabled")

  if not source and not all:
    console.print("[bold red]❌ Please specify --source or --all[/bold red]")
    raise typer.Exit(code=1)

  if source and all:
    console.print("[bold red]❌ Use either --source or --all, not both[/bold red]")
    raise typer.Exit(code=1)
  
  db = None

  try: 

    db = get_db()
    engine = ScraperEngine(db)

    console.print("[bold cyan]🚀 Starting scraping process...[/bold cyan]")

    if all:
      scrapers = [cls() for cls in SCRAPERS.values()]
      total = engine.run_multiple(scrapers)
      console.print(f"\n [bold cyan]✅ Finished scraping all sources. Total jobs saved: {total}[bold cyan]")
    else:
      source = source.lower()

      if source not in SCRAPERS:
        console.print(f"[bold red]❌ Unknown source:[/bold red] {source}")
        console.print(f"[yellow]Available sources:[/yellow] {', '.join(SCRAPERS.keys())}")
        raise typer.Exit(code=1)

      scraper = SCRAPERS[source]()

      with ErrorContext(f"Scraping {source}"):
        count = engine.run_scraper(scraper)
        console.print(f"\n[bold green]✅ Finished scraping {source}. Jobs saved: {count}[/bold green]")

  except KeyboardInterrupt:
    console.print("\n[yellow]⚠️  Scraping cancelled by user[/yellow]")
    logger.info("Scraping process cancelled by user")
  except Exception as e:
    logger.exception(f"Fatal error during scraping: {str(e)}")
    console.print(f"[bold red]❌ Fatal error:[/bold red] {str(e)}")
    
  finally:
    if db:
      db.close()
      logger.debug("Database session closed")
