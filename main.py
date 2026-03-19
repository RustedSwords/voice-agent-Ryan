from fastapi import FastAPI
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import os

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

app = FastAPI()

# Load credentials from json file or run the OAuth flow if not available
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
else:
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_console(port=0)
    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)

class Event(BaseModel):
    name: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    title: str = "Meeting"

@app.post("/create-event")
def create_event(event: Event):
    event_start = f"{event.date}T{event.time}:00"
    event_body = {
        "summary": event.title,
        "description": f"Scheduled by voice assistant for {event.name}",
        "start": {"dateTime": event_start, "timeZone": "Europe/Berlin"},
        "end": {"dateTime": event_start, "timeZone": "Europe/Berlin"},  # For now, same start/end
    }
    created_event = service.events().insert(calendarId='primary', body=event_body).execute()
    return {
        "status": "success",
        "message": f"Event '{created_event['summary']}' created for {event.name}"
    }