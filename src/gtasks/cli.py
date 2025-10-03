"""Command-line interface for gtasks."""

import click

from .auth import get_tasks_service


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


@main.command()
@click.pass_context
def lists(ctx):
    """Lists your task lists."""
    service = get_tasks_service(ctx.obj["auth_flow"])

    # Call the Tasks API
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get("items", [])

    if not items:
        click.echo("No task lists found.")
    else:
        click.echo("Task lists:")
        for item in items:
            click.echo(f"- {item['title']} ({item['id']})")


@main.command()
@click.argument("tasklist_id")
@click.pass_context
def tasks(ctx, tasklist_id):
    """Lists tasks in a specific task list."""
    service = get_tasks_service(ctx.obj["auth_flow"])

    results = service.tasks().list(tasklist=tasklist_id).execute()
    items = results.get("items", [])

    if not items:
        click.echo("No tasks found in the specified list.")
    else:
        click.echo("Tasks:")
        for item in items:
            status = "Completed" if item.get("status") == "completed" else "Needs Action"
            click.echo(f"- {item['title']} (id: {item['id']}, status: {status})")


@main.command()
@click.argument("tasklist_id")
@click.argument("title")
@click.pass_context
def add(ctx, tasklist_id, title):
    """Adds a new task to a specific task list."""
    service = get_tasks_service(ctx.obj["auth_flow"])

    task = {"title": title}
    result = service.tasks().insert(tasklist=tasklist_id, body=task).execute()
    click.echo(f"Task '{result['title']}' created.")


@main.command()
@click.argument("tasklist_id")
@click.argument("task_id")
@click.pass_context
def complete(ctx, tasklist_id, task_id):
    """Marks a task as complete."""
    service = get_tasks_service(ctx.obj["auth_flow"])

    task = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
    task["status"] = "completed"

    result = (
        service.tasks()
        .update(tasklist=tasklist_id, task=task_id, body=task)
        .execute()
    )
    click.echo(f"Task '{result['title']}' marked as complete.")


@main.command()
@click.argument("tasklist_id")
@click.pass_context
def delete(ctx, tasklist_id):
    """Deletes a task list."""
    service = get_tasks_service(ctx.obj["auth_flow"])

    service.tasklists().delete(tasklist=tasklist_id).execute()
    click.echo(f"Task list with id '{tasklist_id}' deleted.")


@main.command()
@click.pass_context
def demo(ctx):
    """Runs a demo of the gtasks CLI."""
    service = get_tasks_service(ctx.obj["auth_flow"])
    click.echo("Starting gtasks CLI demo...")

    # 1. Create a new task list
    click.echo("\n1. Creating a new task list named 'MVP Demo'...")
    tasklist = service.tasklists().insert(body={"title": "MVP Demo"}).execute()
    tasklist_id = tasklist["id"]
    click.echo(f"   Task list 'MVP Demo' created with id: {tasklist_id}")

    # 2. Add tasks to the list
    click.echo("\n2. Adding tasks to the 'MVP Demo' list...")
    task1 = (
        service.tasks()
        .insert(tasklist=tasklist_id, body={"title": "Learn gtasks CLI"})
        .execute()
    )
    click.echo(f"   - Task '{task1['title']}' added.")
    task2 = (
        service.tasks()
        .insert(tasklist=tasklist_id, body={"title": "Present demo"})
        .execute()
    )
    click.echo(f"   - Task '{task2['title']}' added.")

    # 3. List the tasks
    click.echo("\n3. Listing tasks in 'MVP Demo' list...")
    ctx.invoke(tasks, tasklist_id=tasklist_id)

    # 4. Mark a task as complete
    click.echo(f"\n4. Marking task '{task1['title']}' as complete...")
    ctx.invoke(complete, tasklist_id=tasklist_id, task_id=task1["id"])

    # 5. List the tasks again
    click.echo("\n5. Listing tasks again to show the updated status...")
    ctx.invoke(tasks, tasklist_id=tasklist_id)

    # 6. Delete the task list
    click.echo("\n6. Deleting the 'MVP Demo' task list...")
    ctx.invoke(delete, tasklist_id=tasklist_id)

    click.echo("\nDemo complete!")
