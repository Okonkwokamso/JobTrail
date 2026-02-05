class JobTrailException(Exception):
  """Base exception for all JobTrail errors."""
  def __init__(self, message: str, details: dict = None):
    self.message = message
    self.details = details or {}
    super().__init__(self.message)


class ScraperException(JobTrailException):
  """Base exception for scraper-related errors."""
  pass


class ScraperTimeoutError(ScraperException):
  """Raised when scraper times out."""
  pass


class ScraperParseError(ScraperException):
  """Raised when scraper fails to parse data."""
  pass


class ScraperConnectionError(ScraperException):
  """Raised when scraper can't connect to source."""
  pass


class DatabaseException(JobTrailException):
  """Base exception for database errors."""
  pass


class ValidationException(JobTrailException):
  """Raised when data validation fails."""
  pass


class AuthenticationException(JobTrailException):
  """Raised when authentication fails."""
  pass


class NotFoundException(JobTrailException):
  """Raised when a resource is not found."""
  pass
