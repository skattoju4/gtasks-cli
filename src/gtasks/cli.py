"""Command-line interface for gtasks."""

import click

from .auth import get_tasks_service
from .config import get_current_task_list, set_current_task_list


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

    service = get_tasks_service(ctx.obj["auth_flow"])

    if name:
        results = service.tasklists().list(maxResults=100).execute()
        items = results.get("items", [])
        for item in items:
            if item["title"] == name:
                list_id = item["id"]
                break
        if not list_id:
            raise click.UsageError(f"Task list with name '{name}' not found.")

    set_current_task_list(list_id)
    click.echo(f"Current task list set to '{list_id}'.")


@list.command("task-lists")
@click.pass_context
def list_task_lists(ctx):
    """Lists your task lists."""
    service = get_tasks_service(ctx.obj["auth_flow"])

    results = service.tasklists().list(maxResults=10).execute()
    items = results.get("items", [])

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
@click.pass_context
def list_tasks(ctx, tasklist_id, status):
    """Lists the tasks in a task list."""
    service = get_tasks_service(ctx.obj["auth_flow"])

    if not tasklist_id:
        tasklist_id = get_current_task_list()
        if not tasklist_id:
            raise click.UsageError(
                "No current task list set. Use 'gtasks use list' to set one."
            )

    show_completed = status in ["all", "completed"]
    results = (
        service.tasks().list(tasklist=tasklist_id, showCompleted=show_completed).execute()
    )
    items = results.get("items", [])

    if status == "completed":
        items = [item for item in items if item.get("status") == "completed"]

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
@click.pass_context
def edit_task(ctx, task_id, description, tasklist_id):
    """Edits a task."""
    service = get_tasks_service(ctx.obj["auth_flow"])

    if not tasklist_id:
        tasklist_id = get_current_task_list()
        if not tasklist_id:
            raise click.UsageError(
                "No current task list set. Use 'gtasks use list' to set one."
            )

    body = {}
    if description:
        body["notes"] = description

    if not body:
        click.echo("Nothing to update.")
        return

    service.tasks().patch(tasklist=tasklist_id, task=task_id, body=body).execute()
    click.echo("Task updated.")


@edit.command("task-lists")
@click.option("--id", "list_id", required=True, help="The ID of the task list to edit.")
@click.option("--name", help="The new name for the task list.")
@click.pass_context
def edit_task_lists(ctx, list_id, name):
    """Edits a task list."""
    service = get_tasks_service(ctx.obj["auth_flow"])

    body = {}
    if name:
        body["title"] = name

    if not body:
        click.echo("Nothing to update.")
        return

    service.tasklists().patch(tasklist=list_id, body=body).execute()
    click.echo("Task list updated.")


@main.command()
@click.option("--title", required=True, help="The title of the task.")
@click.option("--tasklist-id", help="The ID of the task list to add the task to.")
@click.pass_context
def add(ctx, title, tasklist_id):
    """Adds a new task."""
    service = get_tasks_service(ctx.obj["auth_flow"])

    if not tasklist_id:
        tasklist_id = get_current_task_list()
        if not tasklist_id:
            raise click.UsageError(
                "No current task list set. Use 'gtasks use list' to set one."
            )

    body = {"title": title}
    result = service.tasks().insert(tasklist=tasklist_id, body=body).execute()
    click.echo(f"Task '{result['title']}' created.")


@main.command()
@click.option("--task-id", required=True, help="The ID of the task to delete.")
@click.option("--tasklist-id", help="The ID of the task list to delete the task from.")
@click.pass_context
def delete(ctx, task_id, tasklist_id):
    """Deletes a task."""
    service = get_tasks_service(ctx.obj["auth_flow"])

    if not tasklist_id:
        tasklist_id = get_current_task_list()
        if not tasklist_id:
            raise click.UsageError(
                "No current task list set. Use 'gtasks use list' to set one."
            )

    service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
    click.echo("Task deleted.")


@main.command()
@click.option("--task-id", required=True, help="The ID of the task to complete.")
@click.option("--tasklist-id", help="The ID of the task list to complete the task from.")
@click.pass_context
def complete(ctx, task_id, tasklist_id):
    """Marks a task as complete."""
    service = get_tasks_service(ctx.obj["auth_flow"])

    if not tasklist_id:
        tasklist_id = get_current_task_list()
        if not tasklist_id:
            raise click.UsageError(
                "No current task list set. Use 'gtasks use list' to set one."
            )

    body = {"status": "completed"}
    service.tasks().update(tasklist=tasklist_id, task=task_id, body=body).execute()
    click.echo("Task marked as complete.")
