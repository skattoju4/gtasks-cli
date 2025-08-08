"""Handles authentication with the Google Tasks API using a manual flow."""

import os.path
import json
import click
import threading
from wsgiref.simple_server import make_server

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

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
                SCOPES
            )

            server = make_server('localhost', 0, None)
            flow.redirect_uri = f'http://localhost:{server.server_port}'

            auth_url, _ = flow.authorization_url()

            print(f'Please visit this URL to authorize this application: {auth_url}')

            def _shutdown_server(environ, start_response):
                query_params = parse_qs(environ['QUERY_STRING'])
                code = query_params.get('code', [''])[0]
                flow.fetch_token(code=code)
                start_response('200 OK', [('Content-type', 'text/plain')])
                threading.Thread(target=server.shutdown).start()
                return [b'Authorization successful. You can close this window.']

            server.set_app(_shutdown_server)
            server.serve_forever()

            creds = flow.credentials

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_tasks_service():
    """Returns an authenticated Google Tasks API service object."""
    creds = get_credentials()
    service = build("tasks", "v1", credentials=creds)
    return service


