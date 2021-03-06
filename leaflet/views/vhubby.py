from mako.template import Template

from sqlalchemy import desc

from pyramid.renderers import render


from trumpet.views.base import BaseViewer
from trumpet.views.menus import BaseMenu

from hubby.database import Meeting, Department, Person
from hubby.database import Tag

from hubby.manager import ModelManager
from hubby.tagger import tag_all_items
from hubby.tagger import add_tag_names

from leaflet.resources import show_attachments

from leaflet.views.base import BaseViewer

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

def prepare_main_data(request):
    layout = request.layout_manager.layout
    layout.title = 'Hubby Page'
    layout.header = 'Hubby Page'
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
        url = self.url(context='main', id='calendar')
        entries.append(('Main View', url))
        url = self.url(context='dbmeetings', id=None)
        entries.append(('Meetings', url))
        url = self.url(context='items', id=None)
        url = self.url(context='viewdepts', id=None)
        entries.append(('View Departments', url))
        url = self.url(context='viewpeople', id=None)
        entries.append(('View People', url))
        url = self.url(context='tagitems', id=None)
        entries.append(('Tag Items', url))
        url = self.url(context='viewtags', id=None)
        entries.append(('View Tags', url))

        if self.context in ['viewfeed']:
            url = self.url(context='deletefeed',
                           feed=self.request.matchdict['feed'])
            entries.append(('Delete Feed', url))
        header = 'Hubby Menu'
        menu = BaseMenu()
        menu.set_new_entries(entries, header=header)
        self.layout.options_menus = dict(actions=menu)
        
        

        # make dispatch table
        self._cntxt_meth = dict(
            main=self.main_calendar_view,
            dbmeetings=self.view_db_meetings,
            viewmeeting=self.view_meeting,
            viewdepts=self.view_departments,
            viewpeople=self.view_people,
            viewdepartment=self.view_dept_meetings,
            tagitems=self.view_tag_items,
            viewtags=self.view_tags,
            viewtaggeditem=self.view_items_with_tag,
            )
                
        
        # dispatch context request
        if self.context in self._cntxt_meth:
            self._cntxt_meth[self.context]()
        else:
            msg = 'Undefined Context: %s' % self.context
            self.layout.content = '<b>%s</b>' % msg


    def main_calendar_view(self):
        template = 'leaflet:templates/mainview-calendar.mako'
        env = dict()
        content = self.render(template, env)
        self.layout.content = content
        self.layout.resources.main_calendar_view.need()
        self.layout.resources.cornsilk.need()
        
    def view_db_meetings(self):
        query = self.dbsession.query(Meeting).order_by(desc(Meeting.date))
        meetings = query.all()
        items = []
        template = 'leaflet:templates/meetinglist.mako'
        env = dict(meetings=meetings)
        content = self.render(template, env)
        self.layout.content = content

    def _oldstuff(self):
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
        from hubby import util
        env = dict(meeting=meeting, util=util)
        template = 'leaflet:templates/meeting.mako'
        self.layout.content = render(template, env, request=self.request)
        self.layout.resources.jqueryui.need()
        show_attachments.need()
        self.layout.resources.cornsilk.need()
        #from trumpet.resources import cornsilk
        #cornsilk.need()
        
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
        tag_all_items(session)
        self.layout.content = '<b>Items have been tagged.</b>'

    def view_tags(self):
        db = self.request.db
        tags = db.query(Tag).all()
        divs = []
        for tag in tags:
            context = 'viewtaggeditem'
            id = tag.name
            url = self.url(context=context, id=id)
            anchor = '<a href="%s">%s</a>' % (url, tag.name)
            div = '<div>%s</div>' % anchor
            divs.append(div)
        content = '<div>%s</div>' % '\n'.join(divs)
        self.layout.content = content
        
    def view_items_with_tag(self):
        tag = self.request.matchdict['id']
        db = self.request.db
        tag = db.query(Tag).get(tag)
        env = dict(items=tag.items, db=db)
        template = 'leaflet:templates/tagged-items.mako'
        self.layout.resources.jqueryui.need()
        show_attachments.need()
        
        self.layout.content = render(template, env, request=self.request)
        
