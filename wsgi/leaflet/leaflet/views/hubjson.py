from datetime import datetime, timedelta
from mako.template import Template


import feedparser

import transaction
from formencode.htmlgen import html
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc

from pyramid.renderers import render
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid


from trumpet.models.rssdata import Feed, FeedData

from trumpet.views.base import BaseViewer


from hubby.legistar import legistar_host
from hubby.database import Meeting, Department, Person
from hubby.database import Item, Action

from hubby.util import legistar_id_guid
from hubby.collector.main import MainCollector
from hubby.collector.main import PickleCollector

from hubby.manager import ModelManager

from leaflet.resources import show_attachments

NUMBER_OF_DEPARTMENTS = 10

item_keys = [
    'file_id',
    'name',
    'result',
    'version',
    'title',
    'item_page',
    'agenda_num',
    'video',
    'action',
    'type',
    'action_details',
    ] 

item_template ="""
<b>%(name)s</b>&nbsp;<a href="%(item_page)s">(%(file_id)s)</a>
<hr>
<p>%(title)s</p>
"""

MEETING_TEMPLATE = """
<div class="hubby-meeting">
<p>Meeting for ${str(meeting.date)} Department: ${meeting.dept.name}.</p>
<ul>
%for mitem in meeting.meeting_items:
    <li>${mitem.item.name}</li>
%endfor
</ul>
</div>
"""
MeetingTemplate = Template(MEETING_TEMPLATE)

def make_item_row(item):
    cells = []
    page = 'http://%s/%s' % (legistar_host, item['item_page'])
    item['item_page'] = page
    content = item_template % item
    return '<tr><td>%s</td></tr>' % content

def make_item_roworig(item):
    cells = []
    for key in item_keys:
        cells += '<td>%s</td>' % item[key]
    return '<tr>%s</tr>' % ''.join(cells)


def prepare_main_data(request):
    layout = request.layout_manager.layout
    layout.title = 'Hubby Page'
    layout.header = 'Hubby Page'
    layout.subheader = ''
    layout.content = ''
    layout.footer = str(request.params)
    
class MainViewer(BaseViewer):
    def __init__(self, request):
        BaseViewer.__init__(self, request)
        self.context = None
        if 'context' in self.request.matchdict:
            self.context = self.request.matchdict['context']

        self.db = self.request.db
        self.manager = ModelManager(self.db)

        # make dispatch table
        self._cntxt_meth = dict(
            meeting=self.get_meeting,
            item=self.get_item,
            dept=self.get_dept,
            people=self.get_people,
            itemactions=self.get_item_actions,
            )
        # dispatch context request
        if self.context in self._cntxt_meth:
            self._cntxt_meth[self.context]()
        else:
            msg = 'Undefined Context: %s' % self.context
            self.layout.content = '<b>%s</b>' % msg


    def serialize_meeting(self, meeting):
        data = dict(id=meeting.id, guid=meeting.guid,
                    title=meeting.title, date=str(meeting.date),
                    time=meeting.time, link=meeting.link,
                    dept_id=meeting.dept_id, updated=str(meeting.updated))
        return data

    def serialize_item(self, item):
        data = dict()
        keys = ['id', 'guid', 'file_id', 'filetype', 'name', 'title',
                'status', 'acted_on']
        for key in keys:
            data[key] = getattr(item, key)
        return data

    def serialize_action(self, action):
        data = dict()
        keys = ['id', 'guid', 'file_id', 'filetype', 'mover_id', 'seconder_id',
                'result', 'agenda_note', 'minutes_note', 'action',
                'action_text']
        for key in keys:
            data[key] = getattr(action, key)
        data['mover'] = '%s %s' % (action.mover.firstname,
                                   action.mover.lastname)
        data['seconder'] = '%s %s' % (action.seconder.firstname,
                                      action.seconder.lastname)
        
        return data
        
    def get_item_actions(self):
        item_id = self.request.matchdict['id']
        item = self.db.query(Item).get(item_id)
        actions = []
        for action in item.actions:
            actions.append(self.serialize_action(action))
        self._exception = dict(actions=actions)
    
    def get_meeting(self):
        id = self.request.matchdict['id']
        meeting = self.db.query(Meeting).get(id)
        self._exception = self.serialize_meeting(meeting)
    
    def get_item(self):
        id = self.request.matchdict['id']
        pass

    def get_dept(self):
        id = self.request.matchdict['id']
        pass

    def get_people(self):
        id = self.request.matchdict['id']
        pass
    
