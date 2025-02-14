from __future__ import print_function
import datetime
import os.path
from google.oauth2 import service_account
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# The ID of the calendar to use
CALENDAR_ID = 'primary'

def get_service():
    """Shows basic usage of the Google Calendar API."""
    creds = None
    # Load credentials from the service account file
    SERVICE_ACCOUNT_FILE = 'credentials.json'
    creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=creds)
    return service

def create_event(event_name, event_start_time, event_end_time):
    service = get_service()

    event = {
      'summary': event_name,
      'start': {
        'dateTime': event_start_time.isoformat(),
        'timeZone': 'UTC',
      },
      'end': {
        'dateTime': event_end_time.isoformat(),
        'timeZone': 'UTC',
      },
    }

    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
    return event.get('htmlLink')

def list_events():
    service = get_service()
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return []

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
    return events