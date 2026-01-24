import typer
from pathlib import Path
from rich.console import Console
from app.db.session import SessionLocal
from app.services.job_service import get_all_jobs
from app.utils.export import export_csv, export_json

app = typer.Typer()
console = Console()

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
    console.print(f"[bold red]❌ Unsupported format:[/bold red] {format}")
    console.print(f"[yellow]Supported formats:[/yellow] {', '.join(SUPPORTED_FORMATS)}")
    raise typer.Exit(code=1)

  db = SessionLocal()
  jobs = get_all_jobs(db)

  if not jobs:
    console.print("[yellow]No jobs to export.[/yellow]")
    return

  output_dir = Path("exports")
  output_dir.mkdir(exist_ok=True)

  if format == "csv":
    export_csv(jobs, output_dir / "jobs.csv")
  elif format == "json":
    export_json(jobs, output_dir / "jobs.json")

  console.print(f"[bold green]✅ Export completed:[/bold green] exports/jobs.{format}")
  db.close()
