from trumpet.views.base import BaseViewer

from hubby.database import Meeting
from hubby.database import Item

from hubby.manager import ModelManager


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
    
