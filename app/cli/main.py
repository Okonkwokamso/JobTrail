import typer
from app.cli.commands.scrape import app as scrape_app
from app.cli.commands.jobs import app as jobs_app
from app.cli.commands.export import app as export_app

app = typer.Typer(help="JobTrail CLI - Job scraping and tracking tool")

app.add_typer(scrape_app)
app.add_typer(jobs_app)
app.add_typer(export_app)


def main():
  app()

if __name__ == "__main__":
  main()
