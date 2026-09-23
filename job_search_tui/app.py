"""Textual application for the job-search workspace."""

from __future__ import annotations

from pathlib import Path

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult, SuspendNotSupported
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
    TabbedContent,
    TabPane,
)

from .data import DashboardData, load_dashboard
from .runner import RunnerError, run_workflow
from .workflows import WORKFLOWS, Workflow


class WorkflowItem(ListItem):
    def __init__(self, workflow: Workflow) -> None:
        super().__init__(Label(workflow.label))
        self.workflow = workflow


class JobSearchApp(App[None]):
    TITLE = "AI Job Search"
    SUB_TITLE = "Codex workflow cockpit"
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("ctrl+r", "run", "Run workflow", show=True),
        Binding("/", "focus_arguments", "Arguments"),
    ]

    def __init__(self, root: Path) -> None:
        super().__init__()
        self.root = root.resolve()
        self.dashboard = DashboardData((), (), {})
        self.selected_workflow = WORKFLOWS[0]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="body"):
            with Vertical(id="sidebar"):
                yield Static("WORKFLOWS", classes="section-title")
                yield ListView(
                    *(WorkflowItem(workflow) for workflow in WORKFLOWS),
                    id="workflow-list",
                )
            with Vertical(id="workspace"):
                yield Static(id="stats")
                with TabbedContent(id="tables"):
                    with TabPane("Applications", id="applications-tab"):
                        yield DataTable(id="applications", cursor_type="row", zebra_stripes=True)
                    with TabPane("Saved jobs", id="jobs-tab"):
                        yield DataTable(id="jobs", cursor_type="row", zebra_stripes=True)
                with Vertical(id="launcher"):
                    yield Static("Search jobs", id="workflow-title")
                    yield Static(self.selected_workflow.description, id="workflow-description")
                    yield Input(placeholder="No arguments required", id="workflow-arguments")
                    with Horizontal(id="launcher-actions"):
                        yield Button("Run in Codex", id="run", variant="primary")
                        yield Static("Ctrl+R run  / arguments  R refresh", id="launcher-help")
                yield Static("Ready", id="status-line")
        yield Footer()

    def on_mount(self) -> None:
        applications = self.query_one("#applications", DataTable)
        applications.add_columns("Date", "Company", "Role", "Status", "Fit", "Deadline")
        jobs = self.query_one("#jobs", DataTable)
        jobs.add_columns("Score", "Company", "Role", "Status", "Posted", "Portal")
        workflow_list = self.query_one("#workflow-list", ListView)
        workflow_list.index = 0
        workflow_list.focus()
        self.action_refresh()

    def action_refresh(self) -> None:
        self.dashboard = load_dashboard(self.root)
        self._render_stats()
        self._render_applications()
        self._render_jobs()
        self.query_one("#status-line", Static).update("Data refreshed from repository")

    def action_focus_arguments(self) -> None:
        self.query_one("#workflow-arguments", Input).focus()

    def action_run(self) -> None:
        arguments = self.query_one("#workflow-arguments", Input).value
        status = self.query_one("#status-line", Static)
        status.update(f"Launching {self.selected_workflow.prompt} …")
        try:
            with self.suspend():
                return_code = run_workflow(self.root, self.selected_workflow.name, arguments)
        except RunnerError as exc:
            self.notify(str(exc), title="Cannot launch workflow", severity="error")
            status.update(str(exc))
            return
        except SuspendNotSupported as exc:
            self.notify(str(exc), title="Workflow failed", severity="error")
            status.update(f"Workflow failed: {exc}")
            return
        self.action_refresh()
        if return_code == 0:
            status.update(f"{self.selected_workflow.prompt} finished successfully")
        else:
            message = f"{self.selected_workflow.prompt} exited with status {return_code}"
            status.update(message)
            self.notify(message, severity="warning")

    @on(Button.Pressed, "#run")
    def run_button_pressed(self) -> None:
        self.action_run()

    @on(Input.Submitted, "#workflow-arguments")
    def arguments_submitted(self) -> None:
        self.action_run()

    @on(ListView.Selected, "#workflow-list")
    def workflow_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not isinstance(item, WorkflowItem):
            return
        self.selected_workflow = item.workflow
        self.query_one("#workflow-title", Static).update(item.workflow.label)
        self.query_one("#workflow-description", Static).update(item.workflow.description)
        arguments = self.query_one("#workflow-arguments", Input)
        arguments.value = ""
        arguments.placeholder = item.workflow.argument_hint or "No arguments required"

    def _render_stats(self) -> None:
        counts = "  ".join(f"{key}: {value}" for key, value in self.dashboard.status_counts.items())
        summary = Text()
        summary.append(f"{self.dashboard.total_applications}", style="bold #7dd3fc")
        summary.append(" applications   ")
        summary.append(f"{self.dashboard.active_applications}", style="bold #86efac")
        summary.append(" active   ")
        summary.append(f"{self.dashboard.ranked_jobs}", style="bold #fcd34d")
        summary.append(" ranked jobs")
        if counts:
            summary.append(f"\n{counts}", style="#94a3b8")
        self.query_one("#stats", Static).update(summary)

    def _render_applications(self) -> None:
        table = self.query_one("#applications", DataTable)
        table.clear()
        for index, application in enumerate(self.dashboard.applications):
            table.add_row(
                application.date,
                application.company,
                application.role,
                application.status,
                application.fit_rating or "-",
                application.deadline or "-",
                key=f"application-{index}",
            )

    def _render_jobs(self) -> None:
        table = self.query_one("#jobs", DataTable)
        table.clear()
        for index, job in enumerate(self.dashboard.jobs):
            table.add_row(
                job.score or "-",
                job.company,
                job.title,
                job.status,
                job.posted_date or "-",
                job.portal or "-",
                key=f"job-{index}",
            )
