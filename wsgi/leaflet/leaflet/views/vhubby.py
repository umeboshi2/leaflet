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
from hubby.database import Tag
from hubby.util import legistar_id_guid
from hubby.collector.main import MainCollector
from hubby.collector.main import PickleCollector

from hubby.manager import ModelManager
from hubby.tagger import tag_all_items
from hubby.tagger import add_tag_names

from leaflet.resources import show_attachments
from leaflet.resources import hubby_css


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
    hubby_css.need()
    
class MainViewer(BaseViewer):
    def __init__(self, request):
        BaseViewer.__init__(self, request)
        self.context = None
        if 'context' in self.request.matchdict:
            self.context = self.request.matchdict['context']
        prepare_main_data(self.request)
        self.dbsession = self.request.db
        self.manager = ModelManager(self.dbsession)
        # make left menu
        entries = []
        url = self.url(context='dbmeetings', id=None)
        entries.append(('Meetings', url))
        url = self.url(context='items', id=None)
        url = self.url(context='viewdepts', id=None)
        entries.append(('View Departments', url))
        url = self.url(context='viewpeople', id=None)
        entries.append(('View People', url))
        url = self.url(context='tagitems', id=None)
        entries.append(('Tag Items', url))
        if self.context in ['viewfeed']:
            url = self.url(context='deletefeed',
                           feed=self.request.matchdict['feed'])
            entries.append(('Delete Feed', url))
        header = 'Hubby Menu'
        self.layout.left_menu.set_new_entries(entries, header=header)
        

        # make dispatch table
        self._cntxt_meth = dict(dbmeetings=self.view_db_meetings,
                                viewmeeting=self.view_meeting,
                                viewdepts=self.view_departments,
                                viewpeople=self.view_people,
                                viewdepartment=self.view_dept_meetings,
                                tagitems=self.view_tag_items,
                                )
                
        
        # dispatch context request
        if self.context in self._cntxt_meth:
            self._cntxt_meth[self.context]()
        else:
            msg = 'Undefined Context: %s' % self.context
            self.layout.content = '<b>%s</b>' % msg


    def view_db_meetings(self):
        query = self.dbsession.query(Meeting).order_by(desc(Meeting.date))
        meetings = query.all()
        items = []
        for meeting in meetings:
            url = self.url(context='viewmeeting', id=meeting.id)
            anchor = '<a href="%s">%s</a>' % (url, meeting.title)
            anchor += '<a href="%s">(link)</a>' % meeting.link
            if meeting.dept_id is None:
                anchor += '<b>(collect)</b>'
            item = '<li>%s</li>' % anchor
            items.append(item)            
        content = '<p>There are %d entries</p>' % len(meetings)
        ul = '<ul>%s</ul>' % '\n'.join(items)
        self.layout.content = '%s\n%s' % (content, ul)
        
    def view_meeting(self):
        id = self.request.matchdict['id']
        session = self.dbsession
        meeting = session.query(Meeting).get(id)
        if meeting is None:
            self.layout.content = "<b>Meeting not found!!!</b>"
            return
        self.layout.header = "View Meeting"
        self.layout.subheader = meeting.title
        env = dict(meeting=meeting)
        template = 'leaflet:templates/meeting.mako'
        self.layout.content = render(template, env, request=self.request)
        show_attachments.need()
        self.layout.resources.jqueryui.need()
    
        
    def view_departments(self):
        rows = self.dbsession.query(Department).all()
        if not rows:
            self.manager.add_departments()
        rows = self.dbsession.query(Department).all()
        dept_links = []
        for dept in rows:
            url = self.url(context='viewdepartment', id=dept.id)
            item = '<li><a href="%s">%s</a></li>' % (url, dept.name)
            dept_links.append(item)
        content = '<ul>%s</ul>' % '\n'.join(dept_links)
        self.layout.content = content

    def view_dept_meetings(self):
        dept_id = self.request.matchdict['id']
        dept = self.request.db.query(Department).get(dept_id)
        env = dict(dept=dept)
        template = 'leaflet:templates/dept_meetings.mako'
        self.layout.content = render(template, env, request=self.request)
        
    def view_people(self):
        people = self.dbsession.query(Person).all()
        if not people:
            self.manager.add_people()
        people = self.dbsession.query(Person).all()
        plist = []
        for person in people:
            url = self.url(context='viewperson', id=person.id)
            name = '%s %s' % (person.firstname, person.lastname)
            anchor = '<a href="%s">%s</a>' % (url, name)
            anchor += '&nbsp;<a href="%s">(photo)</a>' % person.photo_link
            item = '<li>%s</li>' % anchor
            plist.append(item)
        ul = '<ul>%s</ul>' % '\n'.join(plist)
        self.layout.content = ul

    def view_person(self):
        pass
    
    def view_tag_items(self):
        session = self.request.db
        add_tag_names(session)
        tags = session.query(Tag)
        tag_all_items(session)
        self.layout.content = '<b>Items have been tagged.</b>'
        
