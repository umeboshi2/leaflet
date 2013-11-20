#from cStringIO import StringIO
from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound
import transaction


from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid

from trumpet.models.base import DBSession
from trumpet.models.usergroup import User, Group, Password
from trumpet.models.usergroup import UserGroup




from trumpet.views.menus import BaseMenu

from trumpet.managers.admin.users import UserManager

from trumpet.security import encrypt_password

from leaflet.views.base import AdminViewer
from leaflet.views.admin.base import make_main_menu

import colander
import deform



def deferred_choices(node, kw):
    choices = kw['choices']
    return deform.widget.SelectWidget(values=choices)

def make_select_widget(choices):
    return deform.widget.SelectWidget(values=choices)

def prepare_main_data(request):
    layout = request.layout_manager.layout
    layout.main_menu = make_main_menu(request)
    
    menu = BaseMenu()
    menu.set_header('Actions')
    route = 'admin_users'
    url = request.route_url(route, context='list', id='all')
    menu.append_new_entry('List Users', url)
    url = request.route_url(route, context='add', id='somebody')
    menu.append_new_entry('Add User', url)
    url = request.route_url(route, context='listgroups', id='all')
    menu.append_new_entry('List Groups', url)
    layout.title = 'Manage Users'
    layout.header = 'Manage Users' 
    layout.options_menus = dict(actions=menu)
    


class AddUserSchema(colander.Schema):
    name = colander.SchemaNode(
        colander.String(),
        title = 'User Name',
        )
    password = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=5),
        widget=deform.widget.PasswordWidget(size=20),
        title = 'Password',
        )
    confirm = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=5),
        widget=deform.widget.PasswordWidget(size=20),
        title = 'Confirm Password',
        )
    

class AddtoGroupSchema(colander.Schema):
    group = colander.SchemaNode(
        colander.Integer(),
        widget=deferred_choices,
        title='Add to Group',
        )

    
class UserManagementViewer(AdminViewer):
    def __init__(self, request):
        super(UserManagementViewer, self).__init__(request)
        prepare_main_data(self.request)
        self.users = UserManager(self.request.db)
        self._dispatch_table = dict(
            list=self.list_users,
            add=self.add_user,
            delete=self.delete_user,
            confirmdelete=self.confirm_delete_user,
            view=self.view_user,
            listgroups=self.list_groups,
            viewgroup=self.view_group,)
        self.context = self.request.matchdict['context']
        self._view = self.context
        self.dispatch()
        
    def list_users(self):
        users = self.users.user_query().all()
        template = 'trumpet:templates/user-list.mako'
        env = dict(users=users)
        self.layout.content = self.render(template, env)
        #self.layout.resources.manage_images.need()
        self.layout.resources.manage_users.need()
        
    def add_user(self):
        schema = AddUserSchema()
        form = deform.Form(schema, buttons=('submit',))
        self.layout.resources.deform_auto_need(form)
        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            self.layout.subheader = 'User Submitted'
            try:
                data = form.validate(controls)
            except deform.ValidationFailure, e:
                self.layout.content = e.render()
                return
            name = data['name']
            password = data['password']
            confirm = data['confirm']
            if password == confirm:
                user = self.users.add_user(name, password)
                content = '<p>User %s added.</p>' % user.username
                self.layout.content = content
            else:
                self.layout.content = 'password mismatch'
            return
        rendered = form.render()
        self.layout.content = rendered
        self.layout.subheader = 'Add a user'

    def delete_user(self):
        id = int(self.request.matchdict['id'])
        env = dict(id=id)
        template = 'trumpet:templates/delete-user.mako'
        self.layout.content = self.render(template, env)
        self.layout.resources.manage_users.need()
        
    def confirm_delete_user(self):
        id = int(self.request.matchdict['id'])
        self.users.delete_user(id)
            
    def view_user(self):
        id = int(self.request.matchdict['id'])
        user = self.users.get_user(id)
        allgroups = self.users.group_query().all()
        ugids = [g.id for g in user.groups]
        available = [g for g in allgroups if g.id not in ugids]
        choices = [(g.id, g.name) for g in available]
        schema = AddtoGroupSchema()
        schema['group'].widget = make_select_widget(choices)
        
        form = deform.Form(schema, buttons=('submit',))
        self.layout.resources.deform_auto_need(form)

        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            try:
                data = form.validate(controls)
            except deform.ValidationFailure, e:
                self.layout.content = e.render()
                return {}
            gid = data['group']
            self.users.add_user_to_group(gid, id)
            g = self.users.get_group(gid)
            msg = 'added user %s to group %s' % (user.username, g.name)
            self.layout.content = msg
            return {}
        env = dict(user=user, form=form.render())
        template = 'leaflet:templates/view-user.mako'
        content = self.render(template, env)
        self.layout.content = content
        

    
    def list_groups(self):
        users = self.users.user_query().all()
        groups = self.users.list_groups()
        template = 'trumpet:templates/group-list.mako'
        env = dict(groups=groups)
        self.layout.content = self.render(template, env)
        self.layout.resources.manage_users.need()
        
    def view_group(self):
        id = self.request.matchdict['id']
        group = self.users.get_group(id)
        items = ''
        for user in group.users:
            items += '<li>%s</li>\n' % user.username
        
        self.layout.content = 'View the darned group %s<ul>%s</ul>' % (group.name, items)
    
