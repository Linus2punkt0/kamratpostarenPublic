import gnistor, radar, dukop, gatorna

# This is simply the function where we put all events together. At some point I should add a function sorting the events
# as at the moment the events from the different sources are just added one after the other.

def gather():
    radarEvents = radar.get()
    gnistorEvents = gnistor.get()
    gatornaEvents = gatorna.get()
    dukopEvents = dukop.get()
    events = radarEvents + gnistorEvents + gatornaEvents + dukopEvents
    return events
