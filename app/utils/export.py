import csv
import json
from pathlib import Path

def export_csv(jobs, path: Path):
  with open(path, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    # Header
    writer.writerow([
      "id",
      "title",
      "company",
      "job_type",
      "source",
      "url",
    ])

    # Rows
    for job in jobs:
      writer.writerow([
          job.id,
          job.title,
          job.company,
          job.job_type,
          job.source,
          job.url,
      ])


def export_json(jobs, path: Path):
  data = [
    {
      "id": job.id,
      "title": job.title,
      "company": job.company,
      "location": job.location,
      "job_type": job.job_type,
      "source": job.source,
      "url": job.url,
    }
    for job in jobs
  ]

  with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
