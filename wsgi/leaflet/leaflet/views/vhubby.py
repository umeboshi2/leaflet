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
from hubby.util import legistar_id_guid
from hubby.collector.main import MainCollector
from hubby.collector.main import PickleCollector

from hubby.manager import ModelManager







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
        if self.context in ['viewfeed']:
            url = self.url(context='deletefeed',
                           feed=self.request.matchdict['feed'])
            entries.append(('Delete Feed', url))
        header = 'Hubby Menu'
        self.make_left_menu(header, entries)

        # make dispatch table
        self._cntxt_meth = dict(rssmeetings=self.view_rss_meetings,
                                dbmeetings=self.view_db_meetings,
                                viewmeeting=self.view_meeting_better,
                                viewdepts=self.view_departments,
                                viewpeople=self.view_people)
                
        
        # dispatch context request
        if self.context in self._cntxt_meth:
            self._cntxt_meth[self.context]()
        else:
            msg = 'Undefined Context: %s' % self.context
            self.layout.content = '<b>%s</b>' % msg

    def _get_all_rss_entries(self):
        q = self.dbsession.query(Feed).filter_by(name='legistar all years')
        feed = q.one()
        q = self.dbsession.query(FeedData).filter_by(feed_id=feed.id)
        fdata = q.order_by(desc(FeedData.retrieved)).first()
        entries = fdata.content.entries
        links = [e.link for e in entries]
        q = self.dbsession.query(Feed).filter_by(name='legistar 2011')
        feed = q.one()
        q = self.dbsession.query(FeedData).filter_by(feed_id=feed.id)
        fdata = q.order_by(desc(FeedData.retrieved)).first()
        for entry in fdata.content.entries:
            if entry.link not in links:
                entries.append(entry)
        return entries
        
    def view_rss_meetings(self):
        entries = self._get_all_rss_entries()
        items = []
        for entry in entries:
            id, guid = legistar_id_guid(entry.link)
            query = self.dbsession.query(Meeting).filter_by(id=id)
            try:
                meeting = query.one()
            except NoResultFound:
                self.manager.add_meeting_from_rss(entry)
            meeting = query.one()
            url = self.url(context='viewmeeting', id=meeting.id)
            anchor = '<a href="%s">%s</a>' % (url, meeting.title)
            anchor += '<a href="%s">(link)</a>' % meeting.link
            item = '<li>%s</li>' % anchor
            items.append(item)
        content = '<p>There are %d entries</p>' % len(entries)
        ul = '<ul>%s</ul>' % '\n'.join(items)
        self.layout.content = '%s\n%s' % (content, ul)
        

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

    def _collect_meeting_info(self, id):
        collector = MainCollector()
        session = self.dbsession
        meeting = session.query(Meeting).filter_by(id=id).one()
        collector.set_url(meeting.link)
        collector.collect('meeting')
        return collector.result
        
    def view_meeting(self):
        id = self.request.matchdict['id']
        collected = None
        session = self.dbsession
        idquery = session.query(Meeting).filter_by(id=id)
        query = idquery.filter(Meeting.dept_id != None)
        try:
            meeting = query.one()
        except NoResultFound:
            meeting = None
            collected = True #this is a lie
        if collected is not None:
            self.manager.merge_meeting_from_legistar(id)
            meeting = query.one()
        rows = []
        for key in ['id', 'guid', 'date', 'time', 'link',
                    'dept_id', 'agenda_status', 'minutes_status']:
            label = '<td>%s:</td>' % key
            value = '<td>%s</td>' %  getattr(meeting, key)
            row = '<tr>%s%s</tr>' % (label, value)
            rows.append(row)
        msg = '<p>Meeting taken from database.</p>'
        if collected is not None:
            msg = '<p>Meeting collected from legistar.</p>'
        table = '<table><tr><th>Name</th><th>Value</th></tr>\n%s</table>'
        table = table % '\n'.join(rows)
        url = self.url(context='updatemeetingitems', id=meeting.id)
        update = '<a href="%s">update items</a><br/>' % url
        url = self.url(context='viewmeetingitemlist', id=meeting.id)
        view = '<a href="%s">view items</a><br/>' % url
        content = '\n'.join([msg, table, update, view])
        self.layout.content = content

    def view_meeting_better(self):
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
                                                 
    
        
    def _update_department(self, dept):
        id, guid, name = dept
        sess = self.dbsession
        try:
            dept = sess.query(Department).filter_by(id=id).one()
        except NoResultFound:
            transaction.begin()
            dept = Department(id, guid)
            dept.name = name
            sess.add(dept)
            sess.flush()
            transaction.commit()
            return
        dept.id = id
        dept.guid = guid
        dept.name = name
        transaction.begin()
        self.dbsession.add(dept)
        self.dbsession.flush()
        transaction.commit()

    def update_departments(self):
        collector = MainCollector()
        collector.collect('dept')
        depts = collector.result
        for dept in depts:
            self._update_department(dept)
        
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
        
    def _update_people(self, people):
        s = self.dbsession
        for aperson in people:
            q = s.query(Person).filter_by(id=aperson['id'])
            try:
                p = q.one()
            except NoResultFound:
                transaction.begin()
                p = Person()
                for key in aperson:
                    setattr(p, key, aperson[key])
                s.add(p)
                s.flush()
                transaction.commit()

    
    
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
    
