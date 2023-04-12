# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import os, pytz, locale
from paths import localCalendar
from functions import *

tz = pytz.timezone("Europe/Stockholm")
curTime = datetime.now(tz)

# Here we create the post queue for twitter and mastodon. The queue comes in the form of an array, containing other arrays.
# Each type of post ("events today", "events tomorrow", "events this week" etc) gets its own array, and the posts in that
# array become a thread.

# This function accepts event information and returns it as a string
def getEventInfo(title, eventTime, location, url):
        # Here we check if the event takes place this year. In that case we don't include the year in the date.
		if (eventTime.strftime("%Y") != curTime.strftime("%Y")):
			timestamp = eventTime.strftime("%-d/%-m %Y %H:%M")
		else:
			timestamp = eventTime.strftime("%-d/%-m %H:%M")
        # Different strings are created based on if we know the location of the event or not.
		if (len(location) > 0):
			eventInfo = title + "\nNär: " + timestamp + "\nVar: " + location + "\n" + url
		else:
			eventInfo = title + "\nNär: " + timestamp + "\n" + url
		return eventInfo

# This function compares returned events to the local calendar. If events are found that are not in the calendar
# we make a "new events found" post
def getNewEvents(eventData):
    # We first check if we actually have a local calendar. If not, we don't want to spam the feed with every event we found.
    if (os.path.exists(localCalendar)):
        localEvents = []
        # getting local events from the csv
        with open(localCalendar, 'r') as cal:
            for line in cal:
                # Not fully sure why I replace newlines here as there shouldn't be any in the lines, but if it ain't 
                # broke I guess.
                eventArr = line.replace('\n', "").split(',')
                url = eventArr[0]
                eventTime = datetime.strptime(eventArr[1], '%Y-%m-%d  %X%z')
                # We do not include events that have already taken place
                if (eventTime > curTime):
                    localEvents.append(url)
        if (len(localEvents) > 0):
            posts = []
            for event in eventData:
                eventTime = event["eventTime"]
                url = event["url"]
                location = event["location"]
                # The event URL acts as the unique identifier for each event, as is almost always unique (with the
                # exception of some recurring events) and most unlikely to change.
                if (eventTime > curTime and url not in localEvents):
                    title = event["title"]
                    writeLog("New event: " + title)
                    eventInfo = getEventInfo(title, eventTime, location, url)
                    writeLog("Eventinfo: " + eventInfo)
                    # Here we add the opening post to the array
                    if (len(posts) == 0):
                        posts.append("Nya evenemang har lagts till:")
                    posts.append(eventInfo)
            if len(posts) > 5:
                 writeLog("More than five new events found, assuming this is due to a local calendar error")
            elif len(posts) > 1:
                writeLog("Following new events found: \n" + "\n".join(posts))
                return posts
            else:
                writeLog("No new events in the calendar")

# This function does the oposite of the above one, checking for events that are in the local calendar, but not the one
# we've fetched, looking for events that have been cancelled.
def getCancelledEvents(eventData):
    # We first check if we actually have a local calendar. If not, there is no reason to keep running the function.
    if not os.path.exists(localCalendar):
        return
    eventURLs = []
    for event in eventData:
        url = event["url"]
        eventTime = event["eventTime"]
        if eventTime > curTime:
            eventURLs.append(url)
    posts = []
    # getting local events from the csv
    with open(localCalendar, 'r') as cal:
        for line in cal:
            eventArr = line.replace('\n', "").split(',')
            url = eventArr[0]
            eventTime = datetime.strptime(eventArr[1], '%Y-%m-%d  %X%z')
            title = eventArr[2].replace("&comma;", ",")
            location = eventArr[3].replace("&comma;", ",")
            # The event URL acts as the unique identifier for each event, as is almost always unique (with the
            # exception of some recurring events) and most unlikely to change.
            if url not in eventURLs and eventTime > curTime:
                writeLog("Cancelled event: " + title)
                eventInfo = getEventInfo(title, eventTime, location, url)
                writeLog("Eventinfo: " + eventInfo)
                # Here we add the opening post to the array
                posts.append("INSTÄLLT:\n" + eventInfo)
    if len(posts) > 3:
            writeLog("More than three cancelled events found, assuming this is due to a local calendar error")
    elif len(posts) > 0:
        writeLog("Following cancelled events found: \n" + "\n".join(posts))
        return posts
    else:
        writeLog("No cancelled events in the calendar")


# Getting events for the coming week
def comingWeek(eventData):
    posts = []
    for event in eventData:
        eventTime = event["eventTime"]
        url = event["url"]
        # We are itterating through the events and picking out the ones for the next week
        if (eventTime.isocalendar()[1] == curTime.isocalendar()[1] + 1):
            location = event["location"]
            title = event["title"]
            eventInfo = getEventInfo(title, eventTime, location, url)
            # Here we add the opening post to the array
            if (len(posts) == 0):
                posts.append("Här är händelserna för den kommande veckan:")
            posts.append(eventInfo)
    if (len(posts) > 1):
        writeLog("Following events found for the coming week: \n" + "\n".join(posts))
        return posts
    else:
        writeLog("No events in the coming week")

# Getting events for coming month. This function is only run at the last day of the month
# so we don't need to check for that in the function, it is just assumed. If it was run on another
# date, the wrong events would be returned.
def comingMonth(eventData):
    # Performing a little locale magic to get the name of the current month in Swedish.
    # First saving the default locale, then switching to sv_SE, getting the month name, and switching back.
    saved = locale._setlocale(locale.LC_TIME)
    locale.setlocale(locale.LC_TIME, 'sv_SE')
    month = (curTime+timedelta(days=1)).strftime('%B')
    locale.setlocale(locale.LC_TIME, saved)
    posts = []
    for event in eventData:
        eventTime = event["eventTime"]
        url = event["url"]
        # Checking if the event takes place in the month and year beginning tomorrow
        if ((curTime+timedelta(days=1)).month == eventTime.month and eventTime.year == (curTime+timedelta(days=1)).year):
            title = event["title"]
            location = event["location"]
            eventInfo = getEventInfo(title, eventTime, location, url)
            # Here we add the opening post to the array
            if (len(posts) == 0):
                posts.append("Här är alla planerade händelser i " + month + ":")
            posts.append(eventInfo)
    if (len(posts) > 1):
        writeLog("Following events found for the coming month: \n" + "\n".join(posts))
        return posts
    else:
        writeLog("No events in the coming month")

# Getting events for today. Pretty self explanatory.
def today(eventData):
    posts = []
    for event in eventData:
        eventTime = event["eventTime"]
        url = event["url"]
        title = event["title"]
        location = event["location"]
        eventInfo = getEventInfo(title, eventTime, location, url)
        # Here we add the opening post to the array
        if (eventTime.date() == curTime.date()):
            if (len(posts) == 0):
                posts.append("Här är dagens evenemang:")
            posts.append(eventInfo)
    if (len(posts) > 1):
        writeLog("Following events found for today: \n" + "\n".join(posts))
        return posts
    else:
        writeLog("No events today")

# Getting events for tomorrow. Also pretty self explanatory.
def tomorrow(eventData):
    posts = []
    for event in eventData:
        eventTime = event["eventTime"]
        url = event["url"]
        title = event["title"]
        location = event["location"]
        eventInfo = getEventInfo(title, eventTime, location, url)
        if (eventTime.date() == curTime.date() + timedelta(days=1)):
            # Here we add the opening post to the array
            if (len(posts) == 0):
                posts.append("Här är vad som händer imorgon:")
            posts.append(eventInfo)
    if (len(posts) > 1):
        writeLog("Following events found for tomorrow: \n" + "\n".join(posts))
        return posts
    else:
        writeLog("No events tomorrow")

# Getting events starting in two hours (or specifically between two and three hours from now)
def inTwoHours(eventData):
    posts = []
    for event in eventData:
        eventTime = event["eventTime"]
        url = event["url"]
        if (curTime+timedelta(hours=2) < eventTime < curTime+timedelta(hours=3)):
            # To make the tweet a little more natural sounding we combine event name and location into a sentence.
            # This is not perfect, it will ignore if the event has multiple locations, and might use the wrong 
            # prepositions for locations, but it's good enough!
            location = event["location"].split(",")[0]
            title = event["shortTitle"]
            if (len(location) > 0):
                if (location == "Internet"):
                    location = " på internet"
                elif (location == "Online"):
                    location = " online"
                else:
                    location = " i " + location
                posts.append("Nu börjar snart " + title.strip() + location + "! \n" + url)
            else:
                posts.append("Nu börjar snart " + title.strip() + "! \n" + url)
            writeLog("Following events found for the next two hours: \n" + "\n".join(posts)) 
    if (len(posts) > 0):
        return posts
    else:
        writeLog("No events coming up in the next two hours")

# Here's where we select what posts to get. Events coming up shortly and new events are always checked for,
# events for today and tomorrow are checked for at nine every morning, and at five in the afternoon
# on sundays and the last of the month we check for events in the upcomming week and month respectively.
def create(eventData):
    queue = [];
    queue.append(inTwoHours(eventData))
    if (isLastOfMonth() and curTime.hour == 17):
        queue.append(comingMonth(eventData))
    elif (curTime.weekday() == 6 and curTime.hour == 17 and not isLastOfMonth()):
        queue.append(comingWeek(eventData))
    elif (curTime.hour == 9):
        queue.append(today(eventData))
        queue.append(tomorrow(eventData))
    queue.append(getNewEvents(eventData))
    queue.append(getCancelledEvents(eventData))
    return queue


