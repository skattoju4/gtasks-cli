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
def list(ctx):
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
