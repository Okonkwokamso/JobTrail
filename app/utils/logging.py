import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logging(log_level: str = "INFO", log_to_file: bool = True):
 
  # Create logs directory if it doesn't exist
  if log_to_file:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"jobtrail_{datetime.now().strftime('%Y%m%d')}.log"
  
 
  log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
  )
  
  # Console handler
  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setFormatter(log_format)
  console_handler.setLevel(getattr(logging, log_level.upper()))
  
  handlers = [console_handler]
  
  # File handler (rotating, max 10MB per file, keep 5 files)
  if log_to_file:
    file_handler = RotatingFileHandler(
      log_file,
      maxBytes=10 * 1024 * 1024,  # 10MB
      backupCount=5
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.DEBUG) 
    handlers.append(file_handler)
  
  # Configure root logger
  logging.basicConfig(
    level=logging.DEBUG,
    handlers=handlers
  )
  
  # Silence noisy third-party loggers
  logging.getLogger('urllib3').setLevel(logging.WARNING)
  logging.getLogger('playwright').setLevel(logging.WARNING)
  logging.getLogger('requests').setLevel(logging.WARNING)
  
  logger = logging.getLogger(__name__)
  logger.info("Logging initialized")


def get_logger(name: str) -> logging.Logger:
  """
  Get a logger instance for a module.
  """
  return logging.getLogger(name)