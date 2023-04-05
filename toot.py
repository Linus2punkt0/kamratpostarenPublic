from mastodon import Mastodon
from functions import *
import time

# The gathered posts are now posted to mastodon using the library mastodon.py

mastodon = Mastodon(
    access_token = 'token.secret',
    api_base_url = 'https://mastodon.laserjesus.se/'
)

def post(queue):
    print("posting to mastodon")
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
    sleep = False;
    for section in queue:
        if section is None:
            continue
        if sleep:
            time.sleep(waitTime * 60)
        sleep = True
        a = ""
        if (isinstance(section, str)):
            a = mastodon.status_post(section)
            writeLog("Following toot found in current section: " + section)
        else:
            writeLog("Following toots found in current section: " + ", ".join(section))
            for toot in section:
                if (len(a) == 0):
                    writeLog("Posting toot: " + toot)
                    a = mastodon.status_post(toot)
                else:
                    writeLog("Posting toot: " + toot + " as a reply")
                    a = mastodon.status_post(toot, in_reply_to_id=a["id"])
            writeLog("Reply from Mastodon: " + str(a))