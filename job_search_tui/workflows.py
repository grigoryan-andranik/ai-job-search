"""Canonical workflow metadata displayed by the TUI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Workflow:
    name: str
    label: str
    description: str
    argument_hint: str = ""
    accent: str = "primary"

    @property
    def prompt(self) -> str:
        return f"${self.name}"


WORKFLOWS: tuple[Workflow, ...] = (
    Workflow("scrape", "Search jobs", "Search enabled portals and deduplicate new postings.", accent="success"),
    Workflow("rank", "Rank jobs", "Score saved postings against your profile and deal-breakers.", accent="success"),
    Workflow("apply", "Prepare application", "Evaluate a posting and build the complete application kit.", "Job URL or pasted posting", "success"),
    Workflow("interview", "Prepare interview", "Build stage-specific interview preparation for a tracked application.", "Company, role, or application folder"),
    Workflow("outcome", "Record outcome", "Update application status, interview stage, offer, rejection, or follow-up.", "Company and outcome, or 'followup'"),
    Workflow("price", "Benchmark salary", "Research a defensible compensation range for a role or offer.", "Company, role, or posting URL"),
    Workflow("upskill", "Plan learning", "Find recurring skill gaps and create a prioritized learning plan.", "Optional job URL"),
    Workflow("expand", "Expand profile", "Add evidence-backed competencies from documents and public profiles."),
    Workflow("html-report", "Build dashboard", "Regenerate the offline HTML application dashboard."),
    Workflow("gmail-sync", "Sync Gmail", "Preview application-status signals from connected Gmail."),
    Workflow("notion-sync", "Sync Notion", "Publish ranked jobs and applications to connected Notion."),
    Workflow("setup", "Update profile", "Run onboarding or update one profile section.", "Optional: --section skills|experience|search"),
    Workflow("add-portal", "Add job portal", "Create and validate a new job-board search skill.", "Portal URL"),
    Workflow("add-template", "Manage templates", "Register, list, or select CV and cover-letter templates.", "Optional: --list or --use <name>"),
    Workflow("reset", "Reset data", "Preview a scoped reset. Codex still requires typed RESET confirmation.", "profile, documents, or all", "warning"),
)

WORKFLOW_BY_NAME = {workflow.name: workflow for workflow in WORKFLOWS}

