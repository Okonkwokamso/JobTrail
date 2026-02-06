import typer
from pathlib import Path
from rich.console import Console
from app.db.session import SessionLocal
from app.services.job_service import get_all_jobs
from app.utils.export import export_csv, export_json
from app.utils.logging import get_logger

app = typer.Typer()
console = Console()

logger = get_logger(__name__)

SUPPORTED_FORMATS = ["csv", "json"]


@app.command()
def export(
  format: str = typer.Option(..., "--format", "-f", help="Export format: csv or json"),
):
  """
  Export jobs to a file (csv or json).
  """

  format = format.lower()

  if format not in SUPPORTED_FORMATS:
    logger.info(f"[bold red]❌ Unsupported format:[/bold red] {format}")
    logger.info(f"[yellow]Supported formats:[/yellow] {', '.join(SUPPORTED_FORMATS)}")
    raise typer.Exit(code=1)

  db = SessionLocal()
  jobs = get_all_jobs(db)

  if not jobs:
    logger.info("[yellow]No jobs to export.[/yellow]")
    return

  output_dir = Path("exports")
  output_dir.mkdir(exist_ok=True)

  if format == "csv":
    export_csv(jobs, output_dir / "jobs.csv")
  elif format == "json":
    export_json(jobs, output_dir / "jobs.json")

  logger.info(f"[bold green]✅ Export completed:[/bold green] exports/jobs.{format}")
  db.close()
