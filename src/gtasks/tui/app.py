from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, TabbedContent, TabPane, ListView, ListItem, Checkbox, Select, Input
from textual.screen import Screen
from textual import work

from ..api import get_task_lists, get_tasks, complete_task
from ..config import set_current_task_list


class SplashScreen(Screen):
    """A splash screen for the application."""

    def compose(self) -> ComposeResult:
        yield Static("Welcome to gtasks!", id="splash-title")
        yield Static("Loading...", id="splash-subtitle")

    def on_mount(self) -> None:
        """When the screen is mounted, set a timer to dismiss it."""
        self.set_timer(2, self.dismiss)


class GTasksApp(App):
    """A Textual app to manage Google Tasks."""

    CSS = """
    #splash-title {
        text-align: center;
        margin-top: 5;
    }
    #splash-subtitle {
        text-align: center;
        margin-top: 2;
    }
    """

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def on_mount(self) -> None:
        """When the app is mounted, show the splash screen."""
        self.push_screen(SplashScreen())
        self.populate_task_lists()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Input(placeholder="Search for a task")
        yield Select([], id="task_list_select", prompt="Select a task list")
        with TabbedContent(initial="tasks"):
            with TabPane("Tasks", id="tasks"):
                yield ListView(id="task_list")
            with TabPane("Completed", id="completed"):
                yield ListView(id="completed_list")
        yield Footer()

    @work(thread=True)
    def populate_task_lists(self) -> None:
        """Fetch task lists and populate the select widget."""
        task_lists = get_task_lists()
        select = self.query_one("#task_list_select", Select)
        options = [(tl["title"], tl["id"]) for tl in task_lists]
        self.call_from_thread(select.set_options, options)
        if task_lists:
            # For simplicity, we'll use the first task list initially
            self.call_from_thread(self.fetch_tasks, task_lists[0]["id"])

    @work(thread=True)
    def fetch_tasks(self, task_list_id: str) -> None:
        """Fetch tasks from the API."""
        set_current_task_list(task_list_id)
        tasks = get_tasks(task_list_id)
        self.call_from_thread(self.update_task_list, tasks, task_list_id)

    def update_task_list(self, tasks: list, task_list_id: str) -> None:
        """Update the task list view with the fetched tasks."""
        self.query_one("#task_list", ListView).clear()
        self.query_one("#completed_list", ListView).clear()
        task_list_view = self.query_one("#task_list", ListView)
        completed_list_view = self.query_one("#completed_list", ListView)
        for task in tasks:
            if task.get("status") == "completed":
                item = ListItem(Checkbox(task["title"], value=True))
                item.disabled = True
                completed_list_view.append(item)
            else:
                item = ListItem(Checkbox(task["title"]))
                item.data = {"task": task, "task_list_id": task_list_id}
                task_list_view.append(item)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle the checkbox changed event."""
        if event.value:
            item = event.checkbox.parent
            task_data = item.data
            self.complete_task(task_data["task"]["id"], task_data["task_list_id"])
            item.remove()
            completed_list_view = self.query_one("#completed_list", ListView)
            completed_item = ListItem(Checkbox(task_data["task"]["title"], value=True))
            completed_item.disabled = True
            completed_list_view.append(completed_item)

    @work(thread=True)
    def complete_task(self, task_id: str, task_list_id: str) -> None:
        """Complete a task."""
        complete_task(task_id, task_list_id)

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle the select changed event."""
        self.fetch_tasks(event.value)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle the input changed event."""
        query = event.value.lower()
        task_list_view = self.query_one("#task_list", ListView)
        for item in task_list_view.children:
            task_title = item.children[0].label.plain.lower()
            item.display = query in task_title

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = GTasksApp()
    app.run()
