import events, twitter, localCal, posts, toot
from functions import *
import multiprocessing

# run.py is the main entrypoint for the application, here functions can be toggled by commenting them out.

# Gathering data from all added sources
eventData = events.gather()
# Sorting through data to generate posts for twitter and mastodon, saving them to a queue array.
postQueue = posts.create(eventData)
# The functions for posting to twitter and mastodon are run in parallell, since they have built in wait periods
# in case there are multiple post types for the run. If we run them sequentially one service will only start posting
# after the entire queue has been processed by the other, including wait times.
postTwitter = multiprocessing.Process(target=twitter.post, args=(postQueue,))
postMastodon = multiprocessing.Process(target=toot.post, args=(postQueue,))
postTwitter.start()
postMastodon.start()
# This makes sure we wait for the functions to finish before moving on. Not sure if this is strictly speaking necessary,
# but it might help avoid unexpected behaviors if more functions are added.
postTwitter.join()
postMastodon.join()
# Saving the gathered event data in a local calendar. This is used as base for kamratpostaren.se and to see if any new events
# are added.
localCal.save(eventData)