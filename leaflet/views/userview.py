from datetime import datetime
from ConfigParser import NoSectionError, DuplicateSectionError

import transaction
from formencode.htmlgen import html
from sqlalchemy.orm.exc import NoResultFound

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid

from trumpet.security import check_password
from trumpet.security import encrypt_password

from leaflet.managers.admin.users import UserManager
from leaflet.views.base import BaseViewer
from leaflet.views.schema import deferred_choices, make_select_widget

from leaflet.models.base import DBSession
from leaflet.models.usergroup import User, Password
from leaflet.models.usergroup import UserConfig

#########################
#[main]
#sms_email_address = 6015551212@vtext.com
#
#[phonecall_views]
#received = agendaDay
#assigned = agendaWeek
#delegated = agendaWeek
#unread = agendaWeek
#pending = agendaWeek
#closed = month
#
#########################

def get_option(db, user_id, section, option):
    q = db.query(UserOption).filter_by(user_id=user_id)
    q = q.filter_by(section=section).filter_by(option=option)
    return q.one().value

import colander
import deform

class ChangePasswordSchema(colander.Schema):
    oldpass = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=5, max=100),
        widget=deform.widget.PasswordWidget(size=20),
        description="Please enter your password.")
    newpass = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=5, max=100),
        widget=deform.widget.PasswordWidget(size=20),
        description="Please enter a new password.")
    confirm = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=5, max=100),
        widget=deform.widget.PasswordWidget(size=20),
        description="Please confirm the new password.")


#_view_choices = ['agendaDay', 'agendaWeek', 'month']
#ViewChoices = dict(enumerate(_view_choices))
_view_choices = [(0, 'agendaDay'), (1, 'agendaWeek'), (2, 'month')]
ViewChoices = dict(_view_choices)
ViewChoiceLookup = dict([(v, k) for k,v in ViewChoices.items()])


PhoneCallViews = ['received', 'taken', 'assigned', 'delegated', 'unread',
                  'pending', 'closed']
TicketViews = ['assigned', 'delegated', 'unread', 'pending', 'closed']
CaseViews = ['accessible', 'assigned', 'delegated', 'unread',
             'pending', 'closed']


class MainOptionsSchema(colander.Schema):
    sms_email_address = colander.SchemaNode(
        colander.String(),
        title='Cell Phone Email Address',
        )
    
class TicketViewOptionsSchema(colander.Schema):
    assigned = colander.SchemaNode(
        colander.String(),
        title='Assigned',
        widget=deferred_choices,
        )
    delegated = colander.SchemaNode(
        colander.String(),
        title='Delegated',
        widget=deferred_choices,
        )
    unread = colander.SchemaNode(
        colander.String(),
        title='Unread',
        widget=deferred_choices,
        )
    pending = colander.SchemaNode(
        colander.String(),
        title='Pending',
        widget=deferred_choices,
        )
    closed = colander.SchemaNode(
        colander.String(),
        title='Closed',
        widget=deferred_choices,
        )
    

class PhoneCallViewOptionsSchema(colander.Schema):
    received = colander.SchemaNode(
        colander.String(),
        title='Received',
        widget=deferred_choices,
        )
    taken = colander.SchemaNode(
        colander.String(),
        title='Taken',
        widget=deferred_choices,
        )
    assigned = colander.SchemaNode(
        colander.String(),
        title='Assigned',
        widget=deferred_choices,
        )
    delegated = colander.SchemaNode(
        colander.String(),
        title='Delegated',
        widget=deferred_choices,
        )
    unread = colander.SchemaNode(
        colander.String(),
        title='Unread',
        widget=deferred_choices,
        )
    pending = colander.SchemaNode(
        colander.String(),
        title='Pending',
        widget=deferred_choices,
        )
    closed = colander.SchemaNode(
        colander.String(),
        title='Closed',
        widget=deferred_choices,
        )
    
class CaseViewOptionsSchema(colander.Schema):
    accessible = colander.SchemaNode(
        colander.String(),
        title='Accessible',
        widget=deferred_choices,
        )
    assigned = colander.SchemaNode(
        colander.String(),
        title='Assigned',
        widget=deferred_choices,
        )
    delegated = colander.SchemaNode(
        colander.String(),
        title='Delegated',
        widget=deferred_choices,
        )
    unread = colander.SchemaNode(
        colander.String(),
        title='Unread',
        widget=deferred_choices,
        )
    pending = colander.SchemaNode(
        colander.String(),
        title='Pending',
        widget=deferred_choices,
        )
    closed = colander.SchemaNode(
        colander.String(),
        title='Closed',
        widget=deferred_choices,
        )
    


def get_password(request):
    db = request.db
    user_id = request.session['user'].id
    return db.query(Password).filter_by(user_id=user_id).one()
    
def check_old_password(request, password):
    dbpass = get_password(request)
    return check_password(dbpass.password, password)


class MainViewer(BaseViewer):
    def __init__(self, request):
        super(MainViewer, self).__init__(request)
        self.users = UserManager(self.request.db)
        # make default config for user, if needed
        user = self.get_current_user()
        if user.config is None:
            self.users.Make_default_config(user.id)
        self.context = self.request.matchdict['context']
        self.layout.header = "User Preferences"
        self.layout.title = "User Preferences"
        # make left menu
        entries = []
        url = request.route_url('user', context='chpasswd')
        entries.append(('Change Password', url))
        url = request.route_url('user', context='status')
        entries.append(('Status', url))
        url = request.route_url('user', context='mainprefs')
        entries.append(('Main Prefs', url))
        url = request.route_url('user', context='tktprefs')
        entries.append(('Ticket Prefs', url))
        url = request.route_url('user', context='phonecallprefs')
        entries.append(('Phone Call Prefs', url))
        url = request.route_url('user', context='caseprefs')
        entries.append(('Case Prefs', url))
        menu = self.layout.ctx_menu
        menu.set_new_entries(entries, header='Preferences')
        # make dispatch table
        self._cntxt_meth = dict(
            chpasswd=self.change_password,
            mainprefs=self.main_preferences,
            tktprefs=self.ticket_preferences,
            phonecallprefs=self.phone_call_preferences,
            caseprefs=self.case_preferences,
            preferences=self.preferences_view,
            )

        # dispatch context request
        if self.context in self._cntxt_meth:
            self._cntxt_meth[self.context]()
        else:
            msg = 'Undefined Context: %s' % self.context
            self.layout.content = '<b>%s</b>' % msg
        

    def preferences_view(self):
        self.layout.content = "Here are your preferences."

    def main_preferences(self):
        schema = MainOptionsSchema()
        form = deform.Form(schema, buttons=('submit',))
        self.layout.resources.deform_auto_need(form)
        if 'submit' in self.request.POST:
            self._main_pref_form_submitted(form)
        else:
            user = self.get_current_user()
            cfg = user.config.get_config()
            data = dict()
            data['sms_email_address'] = cfg.get('main', 'sms_email_address')
            self.layout.content = form.render(data)

    def _main_pref_form_submitted(self, form):
        db = self.request.db
        controls = self.request.POST.items()
        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            self.layout.content = e.render()
            return
        user = self.get_current_user()
        cfg = user.config.get_config()
        cfg.set('main', 'sms_email_address', data['sms_email_address'])
        user.config.set_config(cfg)
        with transaction.manager:
            db.add(user.config)
                
    def ticket_preferences(self):
        schema = TicketViewOptionsSchema()
        choices = _view_choices
        for key in TicketViews:
            schema[key].widget = make_select_widget(choices)
        form = deform.Form(schema, buttons=('submit',))
        self.layout.resources.deform_auto_need(form)
        if 'submit' in self.request.POST:
            self._ticket_pref_form_submitted(form)
        else:
            user = self.get_current_user()
            cfg = user.config.get_config()
            try:
                data = dict(cfg.items('ticket_views'))
            except NoSectionError:
                data = dict(((k, 'month') for k in TicketViews))
            data = dict(((k, ViewChoiceLookup[data[k]]) for k in data))
            self.layout.content = form.render(data)

    def _ticket_pref_form_submitted(self, form):
        db = self.request.db
        controls = self.request.POST.items()
        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            self.layout.content = e.render()
            return
        fields = TicketViews
        section = 'ticket_views'
        values = [ViewChoices[int(data[f])] for f in fields]
        options = dict(zip(fields, values))
        user = self.get_current_user()
        cfg = user.config.get_config()
        try:
            cfg.add_section(section)
        except DuplicateSectionError:
            pass
        for o in options:
            cfg.set(section, o, options[o])
        user.config.set_config(cfg)
        with transaction.manager:
            db.add(user.config)
                
    def phone_call_preferences(self):
        schema = PhoneCallViewOptionsSchema()
        choices = _view_choices
        for key in PhoneCallViews:
            schema[key].widget = make_select_widget(choices)
        form = deform.Form(schema, buttons=('submit',))
        self.layout.resources.deform_auto_need(form)
        if 'submit' in self.request.POST:
            self._phone_call_pref_form_submitted(form)
        else:
            user = self.get_current_user()
            cfg = user.config.get_config()
            data = dict(cfg.items('phonecall_views'))
            data = dict(((k, ViewChoiceLookup[data[k]]) for k in data))
            self.layout.content = form.render(data)

    def _phone_call_pref_form_submitted(self, form):
        db = self.request.db
        controls = self.request.POST.items()
        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            self.layout.content = e.render()
            return
        fields = PhoneCallViews
        section = 'phonecall_views'
        values = [ViewChoices[int(data[f])] for f in fields]
        options = dict(zip(fields, values))
        user = self.get_current_user()
        cfg = user.config.get_config()
        try:
            cfg.add_section(section)
        except DuplicateSectionError:
            pass
        for o in options:
            cfg.set(section, o, options[o])
        user.config.set_config(cfg)
        with transaction.manager:
            db.add(user.config)
                
        
    def case_preferences(self):
        schema = CaseViewOptionsSchema()
        choices = _view_choices
        for key in CaseViews:
            schema[key].widget = make_select_widget(choices)
        form = deform.Form(schema, buttons=('submit',))
        self.layout.resources.deform_auto_need(form)
        if 'submit' in self.request.POST:
            self._case_pref_form_submitted(form)
        else:
            user = self.get_current_user()
            cfg = user.config.get_config()
            try:
                data = dict(cfg.items('case_views'))
            except NoSectionError:
                data = dict(((k, 'month') for k in TicketViews))
            data = dict(((k, ViewChoiceLookup[data[k]]) for k in data))
            self.layout.content = form.render(data)

    def _case_pref_form_submitted(self, form):
        db = self.request.db
        controls = self.request.POST.items()
        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            self.layout.content = e.render()
            return
        fields = CaseViews
        section = 'case_views'
        values = [ViewChoices[int(data[f])] for f in fields]
        options = dict(zip(fields, values))
        user = self.get_current_user()
        cfg = user.config.get_config()
        try:
            cfg.add_section(section)
        except DuplicateSectionError:
            pass
        for o in options:
            cfg.set(section, o, options[o])
        user.config.set_config(cfg)
        with transaction.manager:
            db.add(user.config)
                
    def change_password(self):
        schema = ChangePasswordSchema()
        form = deform.Form(schema, buttons=('update',))
        self.layout.resources.deform_auto_need(form)
        if 'update' in self.request.params:
            controls = self.request.POST.items()
            try:
                data = form.validate(controls)
            except deform.ValidationFailure, e:
                self.layout.content = e.render()
                return
            user = self.request.session['user']
            if data['oldpass'] == data['newpass']:
                self.layout.content = "Password Unchanged"
                return
            if data['newpass'] != data['confirm']:
                self.layout.content = "Password Mismatch."
                return
            if check_old_password(self.request, data['oldpass']):
                newpass = data['newpass']
                dbpass = get_password(self.request)
                dbpass.password = encrypt_password(newpass)
                with transaction.manager:
                    self.request.db.add(dbpass)
                self.layout.content = "Password Changed."
                return
            else:
                self.layout.content = "Authentication Failed."
                return
        self.layout.content = form.render()
        
    
        

