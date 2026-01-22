import typer
from app.cli.commands.scrape import app as scrape_app

app = typer.Typer(help="JobTrail CLI - Job scraping and tracking tool")

app.add_typer(scrape_app)

def main():
  app()

if __name__ == "__main__":
  main()
