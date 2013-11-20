from datetime import datetime, date, timedelta

from docutils.core import publish_parts

from sqlalchemy.exc import OperationalError, ProgrammingError
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from pyramid.renderers import render
from pyramid.response import Response

import colander
import deform


from trumpet.views.menus import BaseMenu

from leaflet.models.usergroup import User

from leaflet.views.base import BaseViewer
from leaflet.views.base import make_main_menu

class MainCalJSONViewer(BaseViewer):
    def __init__(self, request):
        super(MainCalJSONViewer, self).__init__(request)
        self.get_everthing()

    def _get_start_end_userid(self, user_id=True):
        start = self.request.GET['start']
        end = self.request.GET['end']
        if user_id:
            user_id = self.request.session['user'].id
        return start, end, user_id
        

    
    def get_everthing(self):
        self.response = []
        
        
    
class MainViewer(BaseViewer):
    def __init__(self, request):
        super(MainViewer, self).__init__(request)
        self.route = self.request.matched_route.name
        self.layout.main_menu = make_main_menu(self.request)
        self._user_query = self.request.db.query(User)
        
        # begin dispatch
        if self.route == 'home':
            self.main_view()
            return
        elif self.route == 'initdb':
            self.initialize_database()
            return
        if self.route == 'main':
            self.context = self.request.matchdict['context']
        

        # make dispatch table
        self._cntxt_meth = dict(
            main=self.main_view,
            viewevent=self.view_event,
            viewvenue=self.view_venue,
            viewdayevents=self.view_events_for_day,
            exportevent=self.export_event,
            )

        if self.context in self._cntxt_meth:
            self._cntxt_meth[self.context]()
        else:
            msg = 'Undefined Context: %s' % self.context
            self.layout.content = '<b>%s</b>' % msg

            
    def authenticated_view(self):
        #template = 'goout:templates/main-page.mako'
        #env = dict(dates=dates, dc=dc, dformat=dformat)
        #content = render(template, env, request=self.request)
        content = "Main Page"
        self.layout.content = content
        self.layout.subheader = 'leaflet'.capitalize()
        #self.layout.resources.maincalendar.need()
        #self.layout.resources.main_calendar_view.need()
        #self.layout.resources.cornsilk.need()
        
        template = 'leaflet:templates/mainview-calendar.mako'
        env = {}
        content = self.render(template, env)
        self.layout.content = content

        
    def main_view(self):
        authn_policy = self.request.context.authn_policy
        authn = authn_policy.authenticated_userid(self.request)
        if authn is None:
            self.unauthenticated_view()
        else:
            self.authenticated_view()
            
    def unauthenticated_view(self):
        dbconn = False
        try:
            self._user_query.first()
            dbconn = True
        except OperationalError:
            dbconn = False
        except ProgrammingError:
            dbconn = False
        if not dbconn:
            mkurl = self.request.route_url
            url = mkurl('initdb', context='initialize', id='database')
            msg = "Create Database"
            anchor = '<a class="action-button" href="%s">%s</a>' % (url, msg)
            content = anchor
        else:
            url = self.request.route_url('login')
            content = '<a href="%s">Login</a>' % url
        self.layout.content = content

    def initialize_database(self):
        context = self.request.matchdict['context']
        if context != 'initialize':
            self.layout.content = "Bad Call"
            return
        id = self.request.matchdict['id']
        if id != 'database':
            self.layout.content = "Bad Call"
            return
        from leaflet.models.initialize import initialize_database
        settings = self.get_app_settings()
        initialize_database(settings)
        self.layout.content = "Database Initialized"
    
    
    def view_event(self):
        pass
    
        
    def export_event(self):
        pass
    
        
    
    def view_venue(self):
        pass

    def view_events_for_day(self):
        pass
    


        


