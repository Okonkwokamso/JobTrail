import typer
from rich.console import Console
from rich.table import Table
from app.db.session import SessionLocal
from app.services.job_service import get_all_jobs 

app = typer.Typer()
console = Console()


@app.command()
def list():
  """
  List all saved jobs.
  """
  db = SessionLocal()
  jobs = get_all_jobs(db)

  if not jobs:
    console.print("[yellow]No jobs found.[/yellow]")
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
