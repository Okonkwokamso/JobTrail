import typer
from typing import Optional
from rich.console import Console
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.scrappers.engine import ScraperEngine
from app.scrappers.weworkremotely import WeWorkRemotelyScraper
from app.scrappers.remoteok import RemoteOKScraper

#scrape_app = typer.Typer(help="Scrape job sources")

app = typer.Typer()
console = Console()

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
    console.print("[bold red]❌ Please specify --source or --all[/bold red]")
    raise typer.Exit(code=1)

  if source and all:
    console.print("[bold red]❌ Use either --source or --all, not both[/bold red]")
    raise typer.Exit(code=1)

  db = get_db()
  engine = ScraperEngine(db)

  console.print("[bold cyan]🚀 Starting scraping process...[/bold cyan]")

  if all:
    scrapers = [cls() for cls in SCRAPERS.values()]
    total = engine.run_multiple(scrapers)
    console.print(f"\n[bold green]✅ Finished scraping all sources. Total jobs saved: {total}[bold green]")
  else:
    source = source.lower()

    if source not in SCRAPERS:
      console.print(f"[bold red]❌ Unknown source:[/bold red] {source}")
      console.print(f"[yellow]Available sources:[/yellow] {', '.join(SCRAPERS.keys())}")
      raise typer.Exit(code=1)

    scraper = SCRAPERS[source]()
    count = engine.run_scraper(scraper)
    typer.echo(f"\n[bold green]✅ Finished scraping {source}. Jobs saved: {count}[/bold green]")

  db.close()
