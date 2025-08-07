"""Command-line interface for gtasks."""

import click

from .auth import get_tasks_service


@click.group()
def main():
    """A CLI for managing your Google Tasks."""
    pass


@main.command()
def list():
    """Lists your task lists."""
    service = get_tasks_service()

    # Call the Tasks API
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get("items", [])

    if not items:
        click.echo("No task lists found.")
    else:
        click.echo("Task lists:")
        for item in items:
            click.echo(f"- {item['title']} ({item['id']})")