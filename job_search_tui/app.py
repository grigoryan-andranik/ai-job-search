"""Textual application for the job-search workspace."""

from __future__ import annotations

import asyncio
from pathlib import Path

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    RichLog,
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


class WorkflowList(ListView):
    """Workflow menu where Enter launches the highlighted action."""

    def action_select_cursor(self) -> None:
        self.app.action_run()


class HelpScreen(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "dismiss_help", "Close", show=False),
        Binding("question_mark", "dismiss_help", "Close", show=False),
        Binding("q", "dismiss_help", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="help-card"):
            yield Static("Keyboard guide", id="help-title")
            yield Static(
                "Workflows\n"
                "  j / k or arrows   Move selection\n"
                "  g / G             First / last workflow\n"
                "  Enter             Run selected workflow\n\n"
                "Workspace\n"
                "  h / l             Previous / next tab\n"
                "  1 / 2 / 3         Applications / jobs / output\n"
                "  Ctrl+D / Ctrl+U   Page down / up\n\n"
                "Actions\n"
                "  /                 Edit arguments or reply\n"
                "  Ctrl+R            Run or continue\n"
                "  Ctrl+C            Cancel running workflow\n"
                "  r                 Refresh data\n"
                "  Esc               Return to workflows\n"
                "  ?                 Toggle this guide\n"
                "  q                 Quit",
                id="help-copy",
            )
            yield Button("Close", id="close-help", variant="primary")

    def action_dismiss_help(self) -> None:
        self.dismiss()

    @on(Button.Pressed, "#close-help")
    def close_help(self) -> None:
        self.dismiss()


class JobSearchApp(App[None]):
    TITLE = "AI Job Search"
    SUB_TITLE = "Codex workflow cockpit"
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("ctrl+r", "run", "Run workflow", show=True),
        Binding("ctrl+c", "cancel_workflow", "Cancel", show=False),
        Binding("/", "focus_arguments", "Arguments"),
        Binding("question_mark", "show_help", "Help"),
        Binding("1", "show_applications", "Applications", show=False),
        Binding("2", "show_jobs", "Saved jobs", show=False),
        Binding("3", "show_output", "Output", show=False),
        Binding("j", "vim_down", show=False),
        Binding("k", "vim_up", show=False),
        Binding("h", "vim_left", show=False),
        Binding("l", "vim_right", show=False),
        Binding("g", "vim_first", show=False),
        Binding("shift+g", "vim_last", show=False),
        Binding("ctrl+d", "vim_page_down", show=False),
        Binding("ctrl+u", "vim_page_up", show=False),
        Binding("escape", "vim_normal", show=False),
    ]

    def __init__(self, root: Path) -> None:
        super().__init__()
        self.root = root.resolve()
        self.dashboard = DashboardData((), (), {})
        self.selected_workflow = WORKFLOWS[0]
        self.workflow_process: asyncio.subprocess.Process | None = None
        self.workflow_session_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="body"):
            with Vertical(id="sidebar"):
                yield Static("Workflows  j/k", classes="section-title")
                yield WorkflowList(
                    *(WorkflowItem(workflow) for workflow in WORKFLOWS),
                    id="workflow-list",
                )
            with Vertical(id="workspace"):
                yield Static(id="stats")
                with TabbedContent(id="tables"):
                    with TabPane("1 Applications", id="applications-tab"):
                        yield DataTable(id="applications", cursor_type="row", zebra_stripes=True)
                    with TabPane("2 Saved jobs", id="jobs-tab"):
                        yield DataTable(id="jobs", cursor_type="row", zebra_stripes=True)
                    with TabPane("3 Output", id="output-tab"):
                        yield RichLog(id="workflow-output", wrap=True, highlight=True, markup=False)
                with Vertical(id="launcher"):
                    yield Static("Search jobs", id="workflow-title")
                    yield Static(self.selected_workflow.description, id="workflow-description")
                    yield Input(placeholder="No arguments required", id="workflow-arguments")
                    with Horizontal(id="launcher-actions"):
                        yield Button("Run workflow", id="run", variant="primary")
                        yield Static("/ arguments  ·  Esc workflows  ·  ? help", id="launcher-help")
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
        self.query_one("#status-line", Static).update(
            "Ready — j/k choose · Enter run · / arguments · ? help"
        )

    def action_focus_arguments(self) -> None:
        self.query_one("#workflow-arguments", Input).focus()
        self.query_one("#status-line", Static).update("Type arguments or a reply · Enter run · Esc workflows")

    def action_show_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_show_applications(self) -> None:
        self.query_one("#tables", TabbedContent).active = "applications-tab"
        self.query_one("#applications", DataTable).focus()
        self._show_navigation_status("Applications")

    def action_show_jobs(self) -> None:
        self.query_one("#tables", TabbedContent).active = "jobs-tab"
        self.query_one("#jobs", DataTable).focus()
        self._show_navigation_status("Saved jobs")

    def action_show_output(self) -> None:
        self.query_one("#tables", TabbedContent).active = "output-tab"
        self.query_one("#workflow-output", RichLog).focus()
        self._show_navigation_status("Workflow output")

    def action_vim_down(self) -> None:
        focused = self.focused
        if isinstance(focused, (ListView, DataTable)):
            focused.action_cursor_down()
        elif isinstance(focused, RichLog):
            focused.action_scroll_down()
        elif not isinstance(focused, Input):
            self.action_focus_next()

    def action_vim_up(self) -> None:
        focused = self.focused
        if isinstance(focused, (ListView, DataTable)):
            focused.action_cursor_up()
        elif isinstance(focused, RichLog):
            focused.action_scroll_up()
        elif not isinstance(focused, Input):
            self.action_focus_previous()

    def action_vim_left(self) -> None:
        if isinstance(self.focused, Input):
            return
        if isinstance(self.focused, WorkflowList):
            return
        self._cycle_tab(-1)

    def action_vim_right(self) -> None:
        if isinstance(self.focused, Input):
            return
        if isinstance(self.focused, WorkflowList):
            self._focus_active_tab()
            return
        self._cycle_tab(1)

    def action_vim_first(self) -> None:
        focused = self.focused
        if isinstance(focused, ListView):
            focused.index = 0
        elif isinstance(focused, DataTable) and focused.row_count:
            focused.move_cursor(row=0)
        elif isinstance(focused, RichLog):
            focused.action_scroll_home()

    def action_vim_last(self) -> None:
        focused = self.focused
        if isinstance(focused, ListView):
            focused.index = len(focused.children) - 1
        elif isinstance(focused, DataTable) and focused.row_count:
            focused.move_cursor(row=focused.row_count - 1)
        elif isinstance(focused, RichLog):
            focused.action_scroll_end()

    def action_vim_page_down(self) -> None:
        focused = self.focused
        if isinstance(focused, (ListView, DataTable, RichLog)):
            focused.action_page_down()

    def action_vim_page_up(self) -> None:
        focused = self.focused
        if isinstance(focused, (ListView, DataTable, RichLog)):
            focused.action_page_up()

    def action_vim_normal(self) -> None:
        self.query_one("#workflow-list", ListView).focus()
        self.query_one("#status-line", Static).update(
            "Workflows — j/k choose · Enter run · l workspace · ? help"
        )

    def _cycle_tab(self, offset: int) -> None:
        tabs = ("applications-tab", "jobs-tab", "output-tab")
        tabbed_content = self.query_one("#tables", TabbedContent)
        current = tabs.index(tabbed_content.active)
        tabbed_content.active = tabs[(current + offset) % len(tabs)]
        self._focus_active_tab()

    def _focus_active_tab(self) -> None:
        active = self.query_one("#tables", TabbedContent).active
        targets = {
            "applications-tab": ("#applications", DataTable, "Applications"),
            "jobs-tab": ("#jobs", DataTable, "Saved jobs"),
            "output-tab": ("#workflow-output", RichLog, "Workflow output"),
        }
        selector, widget_type, label = targets[active]
        self.query_one(selector, widget_type).focus()
        self._show_navigation_status(label)

    def _show_navigation_status(self, label: str) -> None:
        self.query_one("#status-line", Static).update(
            f"{label} — j/k move · h/l tabs · Esc workflows · ? help"
        )

    def action_run(self) -> None:
        if self.workflow_process is not None and self.workflow_process.returncode is None:
            self.action_cancel_workflow()
            return
        arguments = self.query_one("#workflow-arguments", Input).value
        if self.workflow_session_id and not arguments.strip():
            self.notify("Enter a reply before continuing.", severity="warning")
            return
        status = self.query_one("#status-line", Static)
        output = self.query_one("#workflow-output", RichLog)
        if self.workflow_session_id:
            output.write("\nYou: " + arguments.strip())
            output.write("Continuing workflow…")
        else:
            output.clear()
            output.write(f"Running {self.selected_workflow.prompt} inside the dashboard…")
        self.query_one("#tables", TabbedContent).active = "output-tab"
        self.query_one("#workflow-arguments", Input).disabled = True
        self.query_one("#workflow-list", ListView).disabled = True
        button = self.query_one("#run", Button)
        button.label = "Cancel workflow"
        button.variant = "warning"
        status.update(f"Running {self.selected_workflow.prompt} …")
        self.run_worker(
            self._execute_workflow(
                self.selected_workflow,
                arguments,
                self.workflow_session_id,
            ),
            name="codex-workflow",
            group="codex-workflow",
            exclusive=True,
        )

    async def _execute_workflow(
        self,
        workflow: Workflow,
        arguments: str,
        session_id: str | None,
    ) -> None:
        status = self.query_one("#status-line", Static)
        try:
            return_code = await run_workflow(
                self.root,
                workflow.name,
                arguments,
                on_output=self._write_workflow_output,
                on_process=self._set_workflow_process,
                on_session=self._set_workflow_session,
                session_id=session_id,
            )
        except RunnerError as exc:
            self.notify(str(exc), title="Cannot launch workflow", severity="error")
            status.update(str(exc))
            return
        finally:
            self.workflow_process = None
            self.query_one("#workflow-arguments", Input).disabled = False
            self.query_one("#workflow-list", ListView).disabled = False
            button = self.query_one("#run", Button)
            button.label = "Continue workflow" if self.workflow_session_id else "Run workflow"
            button.variant = "primary"
        self.dashboard = load_dashboard(self.root)
        self._render_stats()
        self._render_applications()
        self._render_jobs()
        if return_code == 0:
            status.update(f"{workflow.prompt} turn complete — reply to continue or choose another workflow")
            arguments_widget = self.query_one("#workflow-arguments", Input)
            arguments_widget.value = ""
            arguments_widget.placeholder = "Reply to Codex, or choose another workflow"
        elif return_code < 0:
            status.update(f"{workflow.prompt} cancelled")
        else:
            message = f"{workflow.prompt} exited with status {return_code}"
            status.update(message)
            self.notify(message, severity="warning")

    def action_cancel_workflow(self) -> None:
        process = self.workflow_process
        if process is None or process.returncode is not None:
            return
        process.terminate()
        self.query_one("#status-line", Static).update("Cancelling workflow…")

    def _set_workflow_process(self, process: asyncio.subprocess.Process) -> None:
        self.workflow_process = process

    def _set_workflow_session(self, session_id: str) -> None:
        self.workflow_session_id = session_id

    def _write_workflow_output(self, message: str) -> None:
        self.query_one("#workflow-output", RichLog).write(message)

    @on(Button.Pressed, "#run")
    def run_button_pressed(self) -> None:
        self.action_run()

    @on(Input.Submitted, "#workflow-arguments")
    def arguments_submitted(self) -> None:
        self.action_run()

    @on(ListView.Selected, "#workflow-list")
    def workflow_selected(self, event: ListView.Selected) -> None:
        self._select_workflow(event.item)

    @on(ListView.Highlighted, "#workflow-list")
    def workflow_highlighted(self, event: ListView.Highlighted) -> None:
        self._select_workflow(event.item)

    def _select_workflow(self, item: ListItem | None) -> None:
        if not isinstance(item, WorkflowItem):
            return
        if item.workflow != self.selected_workflow:
            self.workflow_session_id = None
        self.selected_workflow = item.workflow
        self.query_one("#workflow-title", Static).update(item.workflow.label)
        self.query_one("#workflow-description", Static).update(item.workflow.description)
        arguments = self.query_one("#workflow-arguments", Input)
        arguments.value = ""
        arguments.placeholder = item.workflow.argument_hint or "No arguments required"
        self.query_one("#run", Button).label = "Run workflow"

    def _render_stats(self) -> None:
        counts = "  ".join(f"{key}: {value}" for key, value in self.dashboard.status_counts.items())
        summary = Text()
        summary.append(f"{self.dashboard.total_applications}", style="bold #fabd2f")
        summary.append(" applications   ")
        summary.append(f"{self.dashboard.active_applications}", style="bold #b8bb26")
        summary.append(" active   ")
        summary.append(f"{self.dashboard.ranked_jobs}", style="bold #fe8019")
        summary.append(" ranked jobs")
        if counts:
            summary.append(f"\n{counts}", style="#a89984")
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
