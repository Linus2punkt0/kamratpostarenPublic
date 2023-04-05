# -*- coding: utf-8 -*-
import requests, pytz, feedparser
import xml.etree.cElementTree as etree
from datetime import date, datetime, timedelta

tz = pytz.timezone("Europe/Stockholm")
curTime = datetime.now(tz)
timeLimit = curTime - timedelta(hours = 1)


def get():
    print("Gathering events from Gnistor")
    posts = []
    try:
        calendar = feedparser.parse("https://www.gnistor.se/feed/index.xml")
        for post in calendar.entries:
            eventTime = datetime.strptime(post.gnistor_startdate, '%a, %d %b %Y %X %z')
            # Sometimes the titles are split into multiple lines, which is removed here
            title = post.title.replace('\n', " ")
            eventTitle = title
            # In case an event happens at multiple locations they are returned each on separate lines, which we don't want.
            # Instead we split them with commas.
            location = post.gnistor_locations.strip().replace("\n", ", ")
            # Here we check if the organizer of the event is specified and if it is not already in the event title, 
            # in which case we add it into the event title.
            if len(post.gnistor_organizer) > 0 and post.gnistor_organizer not in post.title:
                eventTitle = post.gnistor_organizer + " anordnar " + post.title
            if (eventTime > curTime):
                item = {
                    "title": eventTitle,
                    "shortTitle": title,
                    "eventTime": eventTime,
                    "url": post.link,
                    "location": location
                }
                # The events are returned in reverse chronological order, so we flip them around here by adding each new event
                # at the beginning of the array
                posts.insert(0, item)
    except:
        print("Collecting info from Gnistor failed")
    print("Finished")
    return posts