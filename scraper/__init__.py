"""Job discovery scrapers (LinkedIn/Indeed via JobSpy, Workday CXS REST)."""

from scraper.ingest import IngestSummary, run_ingestion
from scraper.linkedin_jobspy import fetch_linkedin_indeed
from scraper.models import RawPosting, to_job
from scraper.workday_rest import fetch_all_workday, fetch_workday

__all__ = [
    "IngestSummary",
    "RawPosting",
    "fetch_all_workday",
    "fetch_linkedin_indeed",
    "fetch_workday",
    "run_ingestion",
    "to_job",
]
