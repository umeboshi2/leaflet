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

from leaflet.managers.mainevents import VenueManager


from leaflet.views.base import BaseViewer
from leaflet.views.base import make_main_menu, make_ctx_menu
from leaflet.views.schema import AddVenueSchema

    
class MainViewer(BaseViewer):
    def __init__(self, request):
        super(MainViewer, self).__init__(request)
        self.route = self.request.matched_route.name
        self.layout.main_menu = make_main_menu(self.request).render()
        self._user_query = self.request.db.query(User)
        self.context = self.request.matchdict['context']

        self.venues = VenueManager(self.request.db)
        menu = make_ctx_menu(self.request)
        url = self.url(context='add', id='fff')
        menu.append_new_entry('Add Venue', url)
        self.layout.ctx_menu = menu.output()
        

        # make dispatch table
        self._cntxt_meth = dict(
            main=self.main_view,
            add=self.add_venue,
            )

        if self.context in self._cntxt_meth:
            self._cntxt_meth[self.context]()
        else:
            msg = 'Undefined Context: %s' % self.context
            self.layout.content = '<b>%s</b>' % msg


    def main_view(self):
        self.layout.content = ''
        for venue in self.venues.query().all():
            self.layout.content += '%s<br>' % venue.name


    def _add_venue_form_submitted(self, form):
        controls = self.request.POST.items()
        self.layout.subheader = "submitted to database"
        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            self.layout.content = e.render()
            return
        name = data['venue']
        description = data['description']
        venue = self.venues.add_venue(name, description)
    
    def add_venue(self):
        schema = AddVenueSchema()
        form = deform.Form(schema, buttons=('submit',))
        self.layout.resources.deform_auto_need(form)
        if 'submit' in self.request.POST:
            self._add_venue_form_submitted(form)
        else:
            self.layout.content = form.render()

        
