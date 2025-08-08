"""Handles authentication with the Google Tasks API."""

import os
import webbrowser
import subprocess
import shutil
import click

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/tasks"]


def get_credentials(auth_flow="auto"):
    """Handles user authentication and returns credentials."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )

            if auth_flow == "manual":
                creds = run_manual_flow(flow)
            else:
                creds = run_browser_flow(flow, auth_flow)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def run_browser_flow(flow, auth_flow):
    """Runs the browser-based authentication flow."""
    browser_type = auth_flow

    if auth_flow == "auto":
        try:
            webbrowser.get()
            browser_type = "browser"
        except webbrowser.Error:
            if shutil.which("carbonyl"):
                browser_type = "carbonyl"
            else:
                click.echo(
                    "No graphical browser or carbonyl found. Falling back to manual flow."
                )
                return run_manual_flow(flow)

    if browser_type == "carbonyl":
        if not shutil.which("carbonyl"):
            click.echo(
                "Carbonyl not found. Please install it from https://carbonyl.sh"
            )
            click.echo("Falling back to manual authentication.")
            return run_manual_flow(flow)

        click.echo("Attempting to open carbonyl CLI browser for authentication.")

        original_open = webbrowser.open

        def carbonyl_open(url, new=0, autoraise=True):
            subprocess.run(["carbonyl", url])

        webbrowser.open = carbonyl_open
        try:
            # run_local_server will now use our carbonyl_open function
            creds = flow.run_local_server(
                port=0, success_message="Authentication successful! You can close carbonyl now."
            )
        finally:
            # Restore the original webbrowser.open function
            webbrowser.open = original_open
        return creds

    # Default to standard browser flow
    click.echo("Your browser has been opened for you to login.")
    return flow.run_local_server(port=0)


def run_manual_flow(flow):
    """Runs the manual copy-paste authentication flow."""
    auth_url, _ = flow.authorization_url(prompt="consent")

    click.echo("Please go to this URL to authorize access:")
    click.echo(auth_url)

    redirect_url = click.prompt("Paste the full redirect URL here")

    flow.fetch_token(authorization_response=redirect_url)
    return flow.credentials


def get_tasks_service(auth_flow="auto"):
    """Returns an authenticated Google Tasks API service object."""
    creds = get_credentials(auth_flow)
    service = build("tasks", "v1", credentials=creds)
    return service
