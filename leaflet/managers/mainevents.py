from ConfigParser import ConfigParser
from StringIO import StringIO
from sqlalchemy.orm.exc import NoResultFound
import transaction


from leaflet.models.eventmodels import Venue, EventType
from leaflet.models.eventmodels import EventTypeColor
from leaflet.models.eventmodels import Event, EventVenue
from leaflet.models.eventmodels import Festival, FestivalEvent

from leaflet.managers.util import convert_range_to_datetime

#from leaflet.models.base import DBSession
#from leaflet.models.usergroup import User, Group, Password
#from leaflet.models.usergroup import UserGroup, UserConfig

#from trumpet.security import encrypt_password

class VenueManager(object):
    def __init__(self, session):
        self.session = session

    def query(self):
        return self.session.query(Venue)

    def get(self, venue_id):
        return self.query().get(venue_id)

    def add_venue(self, name, description):
        with transaction.manager:
            v = Venue()
            v.name = name
            v.description = description
            self.session.add(v)
        return self.session.merge(v)

    def delete_venue(self, venue_id):
        with transaction.manager:
            v = self.get(venue_id)
            if v is not None:
                self.self.delete(v)



class EventManager(object):
    def __init__(self, session):
        self.session = session

    def query(self):
        return self.session.query(Event)

    def etype_query(self):
        return session.query(EventType)

    def get(self, event_id):
        return self.query().get(event_id)

    def get_etype(self, name):
        q = self.etype_query()
        q = q.filter_by(name=name)
        return q.one()

    def add_event(self, etype_id, title, start, end,
                  description, all_day, user_id, venue_id):
        now = datetime.now()
        with transaction.manager:
            event = Event(title)
            event.start = start
            event.end = end
            event.start_date = start.date()
            event.start_time = start.time()
            event.end_date = end.date()
            event.end_time = end.time()
            event.title = title
            event.description = description
            event.all_day = all_day
            event.created = now
            event.event_type_id = etype_id
            event.venue_id = venue_id
            self.session.add(event)
        return self.session.merge(event)

    # FIXME: either need better updated or
    # perform that a layer above this
    def update_event(self, event_id,
                     title, start, end, description, all_day, user_id):
        with transaction.manager:
            event = self.get(event_id)
            if event is None:
                raise RuntimeError, "event should be in database"
            if event.created_by_id != user_id:
                raise RuntimeError, "user didn't create event"
            event.start = start
            event.end = end
            event.start_date = start.date()
            event.start_time = start.time()
            event.end_date = end.date()
            event.end_time = end.time()
            event.title = title
            event.description = description
            event.all_day = all_day
            event = self.session.merge(event)
        return event
    

    def all(self):
        return self.query().all()

    def _range_filter(self, query, start, end):
        "start and end are datetime objects"
        query = query.filter(Event.start >= start)
        query = query.filter(Event.start <= end)
        return query

    def _common_range_query(self, start, end, timestamps):
        q = self.query()
        if start is not None:
            if timestamps:
                start, end = convert_range_to_datetime(start, end)
            q = self._range_filter(q, start, end)
        return q
    
    def get_events(self, user_id, start=None, end=None, timestamps=False):
        q = self._common_range_query(start, end, timestamps)
        q = q.filter(Event.created_by_id == user_id)
        return q.all()

    def get_all_events(self, start=None, end=None, timestamps=False):
        q = self._common_range_query(start, end, timestamps)
        return q.all()

    def export_ical(self, id):
        event = self.get(id)
        return make_ical(event)

