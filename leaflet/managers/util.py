from datetime import datetime

import vobject

def convert_range_to_datetime(start, end):
    "start and end are timestamps"
    start = datetime.fromtimestamp(float(start))
    end = datetime.fromtimestamp(float(end))
    return start, end
    

def make_ical(event):
    dtime = datetime(2001, 1, 1)
    cal = vobject.iCalendar()
    cal.add('vevent')
    cal.vevent.add('summary').value = event.title
    cal.vevent.add('description').value = event.description
    cal.vevent.add('organizer').value = event.created_by.username
    #cal.vevent.add('location').value = event.venue.name
    cal.vevent.add('dtstart').value = event.start
    cal.vevent.add('dtend').value = event.end
    return cal
