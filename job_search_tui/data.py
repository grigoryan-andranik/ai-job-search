"""Read-only adapters for tracker and scraper state."""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class Application:
    date: str
    company: str
    role: str
    status: str
    fit_rating: str
    deadline: str
    source: str
    notes: str


@dataclass(frozen=True, slots=True)
class SavedJob:
    key: str
    company: str
    title: str
    status: str
    score: str
    verdict: str
    posted_date: str
    deadline: str
    portal: str
    url: str


@dataclass(frozen=True, slots=True)
class DashboardData:
    applications: tuple[Application, ...]
    jobs: tuple[SavedJob, ...]
    status_counts: dict[str, int]

    @property
    def total_applications(self) -> int:
        return len(self.applications)

    @property
    def active_applications(self) -> int:
        inactive = {"rejected", "withdrawn", "expired", "hired", "offer_declined"}
        return sum(app.status.lower() not in inactive for app in self.applications)

    @property
    def ranked_jobs(self) -> int:
        return sum(job.status == "ranked" for job in self.jobs)


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def load_applications(path: Path) -> tuple[Application, ...]:
    if not path.exists():
        return ()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        applications = [
            Application(
                date=_text(row.get("date")),
                company=_text(row.get("company")) or "Unknown",
                role=_text(row.get("role")) or "Unknown",
                status=_text(row.get("status")) or "unknown",
                fit_rating=_text(row.get("fit_rating")),
                deadline=_text(row.get("deadline")),
                source=_text(row.get("source")),
                notes=_text(row.get("notes")),
            )
            for row in rows
        ]
    return tuple(reversed(applications))


def load_saved_jobs(path: Path) -> tuple[SavedJob, ...]:
    if not path.exists():
        return ()
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return ()
    seen = payload.get("seen", {}) if isinstance(payload, dict) else {}
    if not isinstance(seen, dict):
        return ()
    jobs: list[SavedJob] = []
    for key, raw in seen.items():
        if not isinstance(raw, dict):
            continue
        jobs.append(
            SavedJob(
                key=_text(key),
                company=_text(raw.get("company")) or "Unknown",
                title=_text(raw.get("title")) or "Unknown",
                status=_text(raw.get("status")) or "seen",
                score=_text(raw.get("rank_score")),
                verdict=_text(raw.get("rank_verdict")),
                posted_date=_text(raw.get("posted_date")),
                deadline=_text(raw.get("deadline")),
                portal=_text(raw.get("portal")),
                url=_text(raw.get("url")),
            )
        )
    jobs.sort(
        key=lambda job: (
            int(job.score) if job.score.isdigit() else -1,
            job.posted_date,
        ),
        reverse=True,
    )
    return tuple(jobs)


def load_dashboard(root: Path) -> DashboardData:
    applications = load_applications(root / "job_search_tracker.csv")
    jobs = load_saved_jobs(root / "job_scraper" / "seen_jobs.json")
    counts = Counter(app.status.lower() for app in applications)
    return DashboardData(applications, jobs, dict(sorted(counts.items())))

