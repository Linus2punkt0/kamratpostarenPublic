import gnistor, radar, dukop, gatorna
from operator import itemgetter

# This is simply the function where we put all events together. Sorting them here means the previous sorting was unnecessary, but I'm not gonna change it because I 
# don't feel like it.

def gather():
    radarEvents = radar.get()
    gnistorEvents = gnistor.get()
    gatornaEvents = gatorna.get()
    dukopEvents = dukop.get()
    events = radarEvents + gnistorEvents + gatornaEvents + dukopEvents
    events = sorted(events, key=itemgetter('eventTime'))
    return events