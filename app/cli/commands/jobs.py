import typer
from rich.console import Console
from rich.table import Table
from app.db.session import SessionLocal
from app.services.job_service import get_all_jobs 
from app.utils.logging import get_logger

app = typer.Typer()
console = Console()

logger = get_logger(__name__)


@app.command()
def list():
  """
  List all saved jobs.
  """
  db = SessionLocal()
  jobs = get_all_jobs(db)

  if not jobs:
    logger.info("[yellow]No jobs found.[/yellow]")
    return

  table = Table(title="Saved Jobs")

  table.add_column("ID", style="cyan", no_wrap=True)
  table.add_column("Title", style="white")
  table.add_column("Company", style="green")
  table.add_column("Source", style="magenta")

  for job in jobs:
    table.add_row(job.id, job.title, job.company, job.source)

  console.print(table)
  db.close()
