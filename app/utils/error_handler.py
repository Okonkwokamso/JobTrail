import logging
import traceback
import sys
from functools import wraps
from typing import Callable, Any
from rich.console import Console
from app.utils.exceptions import JobTrailException

logger = logging.getLogger(__name__)
console = Console()

def handle_exceptions(func: Callable) -> Callable:
  @wraps(func)
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except JobTrailException as e:
      # Our custom exceptions
      logger.error(f"{e.__class__.__name__}: {e.message}")
      if e.details:
        logger.debug(f"Error details: {e.details}")
      console.print(f"[bold red]❌ {e.message}[/bold red]")
      return None
    except KeyboardInterrupt:
      logger.info("Operation cancelled by user")
      console.print("\n[yellow]⚠️  Operation cancelled[/yellow]")
      sys.exit(0)
    except Exception as e:
      # Unexpected exceptions
      logger.exception(f"Unexpected error in {func.__name__}: {str(e)}")
      console.print(f"[bold red]❌ Unexpected error: {str(e)}[/bold red]")
      console.print("[dim]Check logs for full traceback[/dim]")
      return None
  
  return wrapper


def safe_execute(func: Callable, *args, default=None, **kwargs) -> Any:
  """
  Safely execute a function and return default value on error.
  
  Args:
    func: Function to execute
    *args: Positional arguments
    default: Default value to return on error
    **kwargs: Keyword arguments
    
  Returns:
    Function result or default value
  """
  try:
    return func(*args, **kwargs)
  except Exception as e:
    logger.error(f"Error executing {func.__name__}: {str(e)}")
    return default


class ErrorContext:
  """
  Context manager for error handling with cleanup.
  
  Usage:
    with ErrorContext("Scraping jobs"):
      scraper.scrape()
  """
  def __init__(self, operation: str, cleanup: Callable = None):
    self.operation = operation
    self.cleanup = cleanup
  
  def __enter__(self):
    logger.info(f"Starting: {self.operation}")
    return self
  
  def __exit__(self, exc_type, exc_val, exc_tb):
    if exc_type is not None:
      logger.error(f"Error during {self.operation}: {exc_val}")
      console.print(f"[bold red]❌ Failed: {self.operation}[/bold red]")
      
      # Run cleanup if provided
      if self.cleanup:
        try:
          self.cleanup()
        except Exception as e:
          logger.error(f"Cleanup failed: {e}")
    else:
      logger.info(f"Completed: {self.operation}")
    
    # Return False to propagate the exception
    return False
