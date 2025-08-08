"""Handles authentication with the Google Tasks API using a manual flow."""

import os.path
import threading
import json
import click
import webbrowser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from http.server import HTTPServer, BaseHTTPRequestHandler
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
            class RequestHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"Authentication successful! You can close this window.")
                    self.server.auth_code = parse_qs(urlparse(self.path).query).get('code', [None])[0]

            server = HTTPServer(('localhost', 0), RequestHandler)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            redirect_uri = f'http://{server.server_name}:{server.server_port}'

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", 
                SCOPES,
                redirect_uri=redirect_uri
            )

            auth_url, _ = flow.authorization_url(prompt='consent')
            click.echo('Please go to this URL to authorize access:')
            click.echo(auth_url)

            while not hasattr(server, 'auth_code'):
                pass

            flow.fetch_token(code=server.auth_code)
            creds = flow.credentials
            server.shutdown()

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_tasks_service():
    """Returns an authenticated Google Tasks API service object."""
    creds = get_credentials()
    service = build("tasks", "v1", credentials=creds)
    return service

