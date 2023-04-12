from datetime import datetime, timedelta
import os, pytz
from paths import logPath

# This file contains some base functionality that is reused across the application

tz = pytz.timezone("Europe/Stockholm")
curTime = datetime.now(tz)
timeLimit = curTime - timedelta(hours = 1)

# This function does as the name implies: it writes to a log file with the format kamrat_[date].log in the log folder.
def writeLog(message):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    date = datetime.now().strftime("%y%m%d")
    message = str(now) + ": " + message + "\n"
    log = logPath + "kamrat_" + date + ".log"
    if os.path.exists(log):
        append_write = 'a'
    else:
        append_write = 'w'
    dst = open(log, append_write)
    dst.write(message)
    dst.close()


# This function is also pretty self explanatory, it returns true if it's the last day of the month, otherwise it returns false
def isLastOfMonth():
    today = curTime.month
    tomorrow = (curTime+timedelta(days=1)).month
    if (today != tomorrow):
        return True
    else:
        return False