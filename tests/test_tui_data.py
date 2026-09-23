import json
import tempfile
import unittest
from pathlib import Path

from job_search_tui.data import load_applications, load_dashboard, load_saved_jobs


class TrackerDataTests(unittest.TestCase):
    def test_loads_utf8_bom_tracker_and_reverses_newest_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tracker.csv"
            path.write_text(
                "\ufeffdate,company,role,status,fit_rating,deadline,source,notes\n"
                "2026-01-01,First,Engineer,applied,70,,,old\n"
                "2026-02-01,Second,SRE,interview,90,2026-03-01,,new\n",
                encoding="utf-8",
            )
            applications = load_applications(path)
        self.assertEqual(applications[0].company, "Second")
        self.assertEqual(applications[1].status, "applied")

    def test_missing_tracker_is_empty(self):
        self.assertEqual(load_applications(Path("/missing/tracker.csv")), ())


class SavedJobDataTests(unittest.TestCase):
    def test_jobs_are_sorted_by_numeric_score(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "seen.json"
            path.write_text(
                json.dumps(
                    {
                        "seen": {
                            "low": {"company": "Low", "title": "SRE", "rank_score": 20},
                            "high": {"company": "High", "title": "DevOps", "rank_score": 91},
                        }
                    }
                ),
                encoding="utf-8",
            )
            jobs = load_saved_jobs(path)
        self.assertEqual([job.company for job in jobs], ["High", "Low"])

    def test_invalid_json_degrades_to_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "seen.json"
            path.write_text("not-json", encoding="utf-8")
            self.assertEqual(load_saved_jobs(path), ())


class DashboardTests(unittest.TestCase):
    def test_computes_active_and_ranked_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "job_scraper").mkdir()
            (root / "job_search_tracker.csv").write_text(
                "date,company,role,status,fit_rating,deadline,source,notes\n"
                "2026-01-01,A,SRE,applied,,,,\n"
                "2026-01-02,B,SRE,rejected,,,,\n",
                encoding="utf-8",
            )
            (root / "job_scraper" / "seen_jobs.json").write_text(
                json.dumps({"seen": {"a": {"status": "ranked"}, "b": {"status": "seen"}}}),
                encoding="utf-8",
            )
            dashboard = load_dashboard(root)
        self.assertEqual(dashboard.total_applications, 2)
        self.assertEqual(dashboard.active_applications, 1)
        self.assertEqual(dashboard.ranked_jobs, 1)


if __name__ == "__main__":
    unittest.main()

