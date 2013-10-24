import transaction

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode, UnicodeText
from sqlalchemy import DateTime, Date, Time
from sqlalchemy import Boolean

from sqlalchemy import ForeignKey


from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError

from leaflet.models.base import Base, DBSession

class Address(Base):
    __tablename__ = 'msl_addresses'
    id = Column(Integer, primary_key=True)
    street = Column(Unicode(150))
    street2 = Column(Unicode(150), default=None)
    city = Column(Unicode(50))
    state = Column(Unicode(2))
    zip = Column(Unicode(10))

    def __init__(self, street, city=None,
                 state=None, zip=None):
        self.street = street
        self.city = city
        self.state = state
        self.zip = zip
        
# these models depend on the Base object above

class Venue(Base):
    __tablename__ = 'lflt_venues'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), unique=True)
    #address_id = Column(Integer, ForeignKey('addresses.id'))
    description = Column(UnicodeText)
    #user_id = Column(Integer, ForeignKey('users.id'))
    #image_id = Column(Integer, ForeignKey('site_images.id'))

class EventType(Base):
    __tablename__ = 'lflt_event_types'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), unique=True)

class EventTypeColor(Base):
    __tablename__ = 'lflt_event_type_colors'
    event_id = Column(Integer,
                      ForeignKey('lflt_event_types.id'), primary_key=True)
    name = Column(Unicode(50), unique=True)
    color = Column(Unicode(10))

    def __init__(self, name, color):
        self.name = name
        self.color = color

class Event(Base):
    __tablename__ = 'lflt_events'
    id = Column(Integer, primary_key=True)
    start = Column(DateTime)
    end = Column(DateTime)
    # force split between date and time
    start_date = Column(Date)
    start_time = Column(Time)
    end_date = Column(Date)
    end_time = Column(Time)
    all_day = Column(Boolean, default=False)
    title = Column(Unicode(255))
    description = Column(UnicodeText)
    created = Column(DateTime)
    created_by_id = Column(Integer,
                           ForeignKey('users.id'),
                           nullable=False)
    event_type_id = Column(Integer,
                           ForeignKey('lflt_event_types.id'),
                           nullable=False)
    venue_id = Column(Integer,
                      ForeignKey('lflt_venues.id'),
                      # FIXME: make this defalt to False
                      nullable=True)


class EventVenue(Base):
    __tablename__ = 'lflt_event_venues'
    event_id = Column(Integer,
                      ForeignKey('lflt_events.id'), primary_key=True)
    venue_id = Column(Integer,
                      ForeignKey('lflt_venues.id'), primary_key=True)


class Festival(Base):
    __tablename__ = 'lflt_festivals'
    id = Column(Integer, primary_key=True)



class FestivalEvent(Base):
    __tablename__ = 'lflt_festival_events'
    festival_id = Column(Integer,
                         ForeignKey('lflt_festivals.id'), primary_key=True)
    event_id = Column(Integer,
                      ForeignKey('lflt_events.id'), primary_key=True)



Venue.events = relationship(Event, secondary='lflt_event_venues')



