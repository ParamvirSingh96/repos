from __future__ import print_function

import datetime
import os.path

import sqlite3

from time import timezone

from dateutil import parser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def addEvent(creds, duration, description):
    start = datetime.datetime.now()
    end = start + datetime.timedelta(hours=duration)  # Add duration in hours
    start_formatted = start.isoformat() + "Z"  # 'Z' indicates UTC time
    end_formatted = end.isoformat() + "Z"  # 'Z' indicates UTC time
  
    event = {
      "summary": description,
      "start": {
          "dateTime": start_formatted,
          "timeZone": "UTC",
        },
      "end": {
          "dateTime": end_formatted,
          "timeZone": "UTC",
        },
      }
  
    service = build("calendar", "v3", credentials=creds)
    event = service.events().insert(calendarId="primary", body=event).execute()
    print(f"Event created: %s" % {event.get('htmlLink')})

def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  script_dir = os.path.dirname(os.path.abspath(__file__))
  credentials_path = os.path.join(script_dir, "credentials.json")
  # Get the directory of the current script
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          credentials_path, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
    commitHours(creds)
    addEvent(creds, 2, "Test Event")
 
def commitHours(creds):
  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    today = datetime.date.today()
    timeStart = str(today) + "T00:00:00Z"
    timeEnd = str(today) + "T23:59:59Z"
    print("Getting todays productive hours")
    events_result = (service.events().list(calendarId="primary", timeMin=timeStart, timeMax=timeEnd, singleEvents=True, orderBy="startTime").execute())
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    total_duration = datetime.timedelta(seconds=0, minutes=0, hours=0)
    print("PRODUCTIVE HOURS:")
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      end = event["end"].get("dateTime", event["end"].get("date"))
      new_start = parser.isoparse(start) #changes the starttime to datetime format
      new_end = parser.isoparse(end) #changes the endtime to datetime format
      duration = new_end - new_start
      total_duration += duration
      print(f"{start} - {end}: {duration}")
    print(f"Total productive hours: {total_duration}")

    conn = sqlite3.connect(f"hours.db")
    cur = conn.cursor()
    print("Opened database successfully")
    date = datetime.date.today()

    formatted_total_duration = total_duration.total_seconds/60/60
    productive_hours = (date, "Productive", formatted_total_duration)
    cur.execute("INSERT INTO Hours VALUES (?, ?, ?)", productive_hours)
    conn.commit()

  except HttpError as error:
    print(f"An error occurred: {error}")

if __name__ == "__main__":
  main()