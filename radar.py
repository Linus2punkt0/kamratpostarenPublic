# -*- coding: utf-8 -*-
import requests, pytz
import xml.etree.cElementTree as etree
from datetime import datetime

tz = pytz.timezone("Europe/Stockholm")
curTime = datetime.now(tz)

# Function for gathering events from radar.squat.net. This is the only source who have an API instead of an RSS feed.
def get():
    print("Gathering events from Radar")
    posts = []
    try: 
        response = requests.get('https://radar.squat.net/api/1.2/search/events.json?fields=offline,url,title,date_time&keys=Sweden')
        json = response.json()["result"]
        for id in json:
            item = json[id]
            url = item["url"]
            title = item["title"]
            uri = item["offline"][0]["uri"]
            date = datetime.fromtimestamp(int(item["date_time"][0]["value"]))
            date = tz.localize(date)
            response = requests.get(uri)
            # We get the api reponse in json format, but not all of the necessary information is returned.
            # Instead we need to make a second call to a another URL which for some reason returns the data in
            # XML-format instead. 
            xml = bytes(bytearray(response.text, encoding = 'utf-8'))
            doc = etree.XML(xml)
            country = doc.find("address").find("country").text
            location = doc.find("address").find("locality").text
            name = doc.find("address").find("name_line").text
            event = title
            # If the name of the organizer is given and not in the event title, we add it.
            if name and name not in title:
                event = name + " anordnar " + title
            if (country == "SE" and date > curTime):
                item = {
                    "title": event,
                    "shortTitle": title,
                    "eventTime": date,
                    "location": location.strip(),
                    "url": url
                }
                posts.insert(0, item)
    except Exception as e:
        print("Collecting info from Radar failed")
        print(e)
    print("Finished")
    return posts

#print(get())