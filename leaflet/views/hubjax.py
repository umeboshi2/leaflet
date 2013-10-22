from pyramid.renderers import render

from trumpet.views.base import BaseViewer


from hubby.database import Meeting
from hubby.database import Item


from hubby.manager import ModelManager


def serialize_meeting(meeting):
    data = dict(id=meeting.id, guid=meeting.guid,
                title=meeting.title, date=str(meeting.date),
                time=meeting.time, link=meeting.link,
                dept_id=meeting.dept_id, updated=str(meeting.updated))
    return data

def serialize_item(item):
    data = dict()
    keys = ['id', 'guid', 'file_id', 'filetype', 'name', 'title',
            'status', 'acted_on']
    for key in keys:
        data[key] = getattr(item, key)
    return data

def serialize_action(action):
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
            itemactions=self.get_item_actions,
            )
        # dispatch context request
        if self.context in self._cntxt_meth:
            self._cntxt_meth[self.context]()
        else:
            msg = 'Undefined Context: %s' % self.context
            self.layout.content = '<b>%s</b>' % msg


    
    def get_item_actions(self):
        item_id = self.request.matchdict['id']
        item = self.db.query(Item).get(item_id)
        actions = []
        template = 'leaflet:templates/short_action.mako'
        for action in item.actions:
            env = dict(action=action)
            actions.append(render(template, env, request=self.request))
        self.response = '\n'.join(actions)
        
    
    def get_meeting(self):
        id = self.request.matchdict['id']
        meeting = self.db.query(Meeting).get(id)
        self.response = serialize_meeting(meeting)
    



class JSONViewer(BaseViewer):
    def __init__(self, request):
        BaseViewer.__init__(self, request)
        self.context = None
        if 'context' in self.request.matchdict:
            self.context = self.request.matchdict['context']

        self.db = self.request.db
        self.manager = ModelManager(self.db)

        # make dispatch table
        self._cntxt_meth = dict(
            itemactions=self.get_item_actions,
            )
        # dispatch context request
        if self.context in self._cntxt_meth:
            self._cntxt_meth[self.context]()
        else:
            msg = 'Undefined Context: %s' % self.context
            self.layout.content = '<b>%s</b>' % msg


    def get_item_actions(self):
        item_id = self.request.matchdict['id']
        item = self.db.query(Item).get(item_id)
        actions = []
        for action in item.actions:
            actions.append(self.serialize_action(action))
        self.response = dict(actions=actions)
    
    def get_meeting(self):
        id = self.request.matchdict['id']
        meeting = self.db.query(Meeting).get(id)
        self.response = serialize_meeting(meeting)
    
