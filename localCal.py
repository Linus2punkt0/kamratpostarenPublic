# -*- coding: utf-8 -*-
from datetime import datetime
import os, feedparser, pytz
from paths import localCalendar

tz = pytz.timezone("Europe/Stockholm")
curTime = datetime.now(tz)

# This function saves events to a local csv.

def save(events):
    print("Saving local calendar")
    # Removing existing calendar and creating a new one.
    if os.path.exists(localCalendar):
        os.remove(localCalendar)
    for event in events:
        eventTime = event["eventTime"]
        url = event["url"]
        # Since this is a csv, having commas in title or location would mess things up. Instea we replace them with the
        # HTML-code for a comma. We don't actually ever parse it as HTML, instead just doing a replace back to a regular 
        # comma, but I haven't come up with a better replacement, so this will do.
        title = event["title"].replace(",", "&comma;")
        location = event["location"].replace(",", "&comma;")
        if os.path.exists(localCalendar):
            append_write = 'a'
        else:
            append_write = 'w'
        dst = open(localCalendar, append_write, encoding='utf-8')
        dst.write(url + "," + eventTime.strftime("%Y-%m-%d %X%z") + "," + title + "," + location + "\n")
        dst.close()
    print("Finished")

