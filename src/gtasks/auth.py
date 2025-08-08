"""Handles authentication with the Google Tasks API using a manual flow."""

import os.path
import json
import click

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/tasks"]

def get_credentials():
    """Handles user authentication and returns credentials."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", 
                SCOPES,
                # This is crucial for the manual flow
                # redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )

            auth_url, _ = flow.authorization_url(prompt='consent')
            click.echo('Please go to this URL to authorize access:')
            click.echo(auth_url)
            creds = flow.run_console()
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_tasks_service():
    """Returns an authenticated Google Tasks API service object."""
    creds = get_credentials()
    service = build("tasks", "v1", credentials=creds)
    return service
