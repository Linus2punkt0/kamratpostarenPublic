# -*- coding: utf-8 -*-
from twython import Twython
from datetime import datetime
import time, pytz
import auth, paths
from functions import *

tz = pytz.timezone("Europe/Stockholm")
curTime = datetime.now(tz)
basePath = paths.basePath
logPath = paths.logPath
localCal = paths.localCal

# This is the function for posting to twitter. I use the library twython for this. There are probably better ones,
# but this is the one I've always used and I don't feel like learning a new one.

twitter = Twython(auth.APP_KEY, auth.APP_SECRET, auth.OAUTH_TOKEN, auth.OAUTH_TOKEN_SECRET)

def post(queue):
    print("posting to twitter")
    # Depending on how many items are in the queue, a different wait time between posts are set.
    # This is to not flood the feed, and to make sure that in the unlikely scenario where we have very
    # many posts, the script doesn't run for an hour, colliding with the next scheduled run.
    # Since adding mastodon the queue does not fully work the same way,
    # as "none" items are added for post types that are not found, and so the length of the queue will be
    # a bit longer than if we only counted actual posts BUT it's good enough and I don't feel like fixing it.
    if (len(queue) == 0):
        return
    elif (len(queue) < 6):
        waitTime = 10
    elif (len(queue) < 12):
        waitTime = 5
    else:
        waitTime = 1
    # We don't want the application to sleep if there is only one post in the queue, so we only sleep if 
    # the variable sleep is true, and only set it to true after we pass the sleep function in the first loop.
    sleep = False
    for section in queue:
        if section is None:
            continue
        a = ""
        if sleep:
            time.sleep(waitTime * 60)
        sleep = True
        # Single posts are put in the queue as strings, and will be posted on their own, while queues of multiple posts
        # are put in an array, which will be itterated through and posted as a thread.
        if (isinstance(section, str)):
            a = twitter.update_status(status=section, auto_populate_reply_metadata=True)
            writeLog("Following tweet found in current section: " + section)
        else:
            writeLog("Following tweets found in current section: " + ", ".join(section))
            for tweet in section:
                # The response from mastodon is saved in a, when the next post is up, it will be posted as a response
                # to the previous one.
                if (len(a) == 0):
                    writeLog("Posting tweet: " + tweet)
                    a = twitter.update_status(status=tweet, auto_populate_reply_metadata=True)
                else:
                    writeLog("Posting tweet: " + tweet + " as a reply")
                    a = twitter.update_status(status=tweet, in_reply_to_status_id=a["id"], auto_populate_reply_metadata=True)
            writeLog("Reply from Twitter: " + str(a))

