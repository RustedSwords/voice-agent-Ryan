from fastapi import FastAPI
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import os
import json

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

app = FastAPI()

creds = None

# Load from environment instead of file
if os.getenv("GOOGLE_TOKEN"):
    creds = Credentials.from_authorized_user_info(
        json.loads(os.getenv("GOOGLE_TOKEN")), SCOPES
    )
else:
    raise Exception("Missing Google token")

flow = InstalledAppFlow.from_client_config(
    json.loads(os.getenv("GOOGLE_CREDENTIALS")), SCOPES
)

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