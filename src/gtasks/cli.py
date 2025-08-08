"""Command-line interface for gtasks."""

import click

from . import api
from .config import set_current_task_list
from .tui.app import GTasksApp


@click.group()
@click.option(
    "--auth-flow",
    type=click.Choice(["auto", "carbonyl", "manual"], case_sensitive=False),
    default="auto",
    help="The authentication flow to use.",
)
@click.pass_context
def main(ctx, auth_flow):
    """A CLI for managing your Google Tasks."""
    ctx.ensure_object(dict)
    ctx.obj["auth_flow"] = auth_flow


@main.group()
def list():
    """Lists resources."""
    pass


@main.group()
def use():
    """Sets the current resource."""
    pass


@main.group()
def edit():
    """Edits resources."""
    pass


@use.command("list")
@click.option("--id", "list_id", help="The ID of the task list to use.")
@click.option("--name", help="The name of the task list to use.")
@click.pass_context
def use_list(ctx, list_id, name):
    """Sets the current task list."""
    if not list_id and not name:
        raise click.UsageError("You must provide either --id or --name.")
    if list_id and name:
        raise click.UsageError("You can only provide either --id or --name, not both.")

    if name:
        task_lists = api.get_task_lists()
        for item in task_lists:
            if item["title"] == name:
                list_id = item["id"]
                break
        if not list_id:
            raise click.UsageError(f"Task list with name '{name}' not found.")

    set_current_task_list(list_id)
    click.echo(f"Current task list set to '{list_id}'.")


@list.command("task-lists")
def list_task_lists():
    """Lists your task lists."""
    items = api.get_task_lists()

    if not items:
        click.echo("No task lists found.")
    else:
        click.echo("Task lists:")
        for item in items:
            click.echo(f"- {item['title']} ({item['id']})")


@list.command("tasks")
@click.option("--tasklist-id", help="The ID of the task list to show tasks from.")
@click.option(
    "--status",
    type=click.Choice(["all", "completed", "incomplete"]),
    default="incomplete",
    help="The status of tasks to show.",
)
def list_tasks(tasklist_id, status):
    """Lists the tasks in a task list."""
    try:
        items = api.get_tasks(tasklist_id, status)
    except Exception as e:
        raise click.UsageError(str(e))

    if not items:
        click.echo("No tasks found.")
    else:
        click.echo("Tasks:")
        for item in items:
            click.echo(f"- {item['title']} ({item['id']})")


@edit.command("task")
@click.option("--id", "task_id", required=True, help="The ID of the task to edit.")
@click.option("--description", help="The new description for the task.")
@click.option("--tasklist-id", help="The ID of the task list the task belongs to.")
def edit_task(task_id, description, tasklist_id):
    """Edits a task."""
    api.edit_task(tasklist_id, task_id, description)
    click.echo("Task updated.")


@edit.command("task-lists")
@click.option("--id", "list_id", required=True, help="The ID of the task list to edit.")
@click.option("--name", help="The new name for the task list.")
def edit_task_lists(list_id, name):
    """Edits a task list."""
    api.edit_task_list(list_id, name)
    click.echo("Task list updated.")


@main.command()
@click.option("--title", required=True, help="The title of the task.")
@click.option("--tasklist-id", help="The ID of the task list to add the task to.")
def add(title, tasklist_id):
    """Adds a new task."""
    try:
        result = api.add_task(title, tasklist_id)
        click.echo(f"Task '{result['title']}' created.")
    except Exception as e:
        raise click.UsageError(str(e))


@main.command()
@click.option("--task-id", required=True, help="The ID of the task to delete.")
@click.option("--tasklist-id", help="The ID of the task list to delete the task from.")
def delete(task_id, tasklist_id):
    """Deletes a task."""
    try:
        api.delete_task(task_id, tasklist_id)
        click.echo("Task deleted.")
    except Exception as e:
        raise click.UsageError(str(e))


@main.command()
@click.option("--task-id", required=True, help="The ID of the task to complete.")
@click.option("--tasklist-id", help="The ID of the task list to complete the task from.")
def complete(task_id, tasklist_id):
    """Marks a task as complete."""
    try:
        api.complete_task(task_id, tasklist_id)
        click.echo("Task marked as complete.")
    except Exception as e:
        raise click.UsageError(str(e))


@main.command()
def tui():
    """Starts the Textual User Interface."""
    app = GTasksApp()
    app.run()
