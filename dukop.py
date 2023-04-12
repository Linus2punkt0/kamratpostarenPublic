# -*- coding: utf-8 -*-
from datetime import datetime
import feedparser, pytz

tz = pytz.timezone("Europe/Stockholm")
curTime = datetime.now(tz)

# Function for gathering data from dukop

def get():
    print("Gathering events from Dukop")
    # Posts are saved in an array, which is then returned
    posts = []
    try:
        # RSS 6 is the specific feed for Lund and Malmö, the only Swedish cities included on dukop
        calendar = feedparser.parse("https://dukop.dk/en/feed/sphere/rss/6/")
        for post in calendar.entries:
            organizer = post.author
            title = post.title
            eventTitle = title
            # Sometimes unwanted information is added into the city-tag in the RSS feed, which we remove here
            location = post.city.split(" - ")[0]
            # Here we check if the organizer of the event is specified and if it is not already in the event title, 
            # in which case we add it into the event title.
            if len(organizer) > 0 and organizer not in title and organizer != "Unspecified host":
                eventTitle = organizer + " anordnar " + eventTitle
            url = post.link
            eventTime = datetime.strptime(post.start_datetime, '%a, %d %b %Y %X %z')
            # Checking to make sure we don't add events in the past (I believe those events are already removed from the
            # feed but just to make sure)
            if (eventTime > curTime):
                item = {
                    "title": eventTitle,
                    "shortTitle": title,
                    "eventTime": eventTime,
                    "url": url,
                    "location": location
                }
                # The events are returned in reverse chronological order, so we flip them around here by adding each new event
                # at the beginning of the array
                posts.insert(0, item)
    except:
        print("Collecting info from Dukop failed")
    print("Finished")
    return posts

# Uncommenting this will allow us to run just this script and print the result.
#print(get())