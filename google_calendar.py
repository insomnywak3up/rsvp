from datetime import datetime, timedelta

def generate_event_link(event_name, event_start_time):
    """Generates a Google Calendar event creation link."""
    event_end_time = event_start_time + timedelta(hours=1)
    start_time_str = event_start_time.strftime('%Y%m%dT%H%M%SZ')
    end_time_str = event_end_time.strftime('%Y%m%dT%H%M%SZ')
    event_link = (
        f"https://calendar.google.com/calendar/r/eventedit?"
        f"text={event_name}&"
        f"dates={start_time_str}/{end_time_str}"
    )
    return event_link