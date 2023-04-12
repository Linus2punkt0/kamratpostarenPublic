# -*- coding: utf-8 -*-
import pytz, feedparser
from datetime import datetime, timedelta

tz = pytz.timezone("Europe/Stockholm")
curTime = datetime.now(tz)

# Gathering events from gatorna.info

def get():
    print("Gathering events from Gatorna")
    posts = []
    try:
        # Gatorna were nice enough to add a specific event feed for me to use, as their main feed also contains
        # blog posts
        calendar = feedparser.parse("https://gatorna.info/event-feed/")
        for post in calendar.entries:
            eventTime = tz.localize(datetime.strptime(post.ev_startdate, '%Y-%m-%d %H:%M'))
            # Sometimes unwanted information is added into the city-tag in the RSS feed, which we remove here
            location = post.ev_location.split("-")[0]
            if (eventTime > curTime):
                item = {
                    # Sometimes the titles are split into multiple lines, which is removed here
                    "title": post.title.replace("\n", " "),
                    "shortTitle": post.title,
                    "eventTime": eventTime,
                    "url": post.link,
                    "location": location.strip()
                }
                # The events are returned in reverse chronological order, so we flip them around here by adding each new event
                # at the beginning of the array
                posts.insert(0, item)
    except:
         print("Collecting info from Gatorna failed")   
    print("Finished")
    return posts

#print(get())