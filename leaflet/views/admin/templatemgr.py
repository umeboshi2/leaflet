from cStringIO import StringIO
from datetime import datetime

import transaction

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from pyramid.renderers import render
from pyramid.response import Response


from trumpet.models.sitecontent import SiteText

from trumpet.resources import MemoryTmpStore

from trumpet.views.menus import BaseMenu

from leaflet.views.base import AdminViewer
from leaflet.views.admin.base import make_main_menu
from leaflet.managers.wiki import WikiArchiver


import colander
import deform

tmpstore = MemoryTmpStore()

def prepare_main_data(request):
    layout = request.layout_manager.layout
    layout.main_menu = make_main_menu(request)
    
    menu = BaseMenu()
    menu.set_header('Actions')
    imgroute = 'admin_images'
    url = request.route_url(imgroute, context='list', id=None)
    menu.append_new_entry('List Images', url)
    url = request.route_url(imgroute, context='add', id=None)
    menu.append_new_entry('Add Image', url)
    layout.options_menus = dict(actions=menu)
    
    layout.title = 'Manage Site Templates'
    layout.header = 'Manage Site Templates' 

class TextSchema(colander.Schema):
    name = colander.SchemaNode(
        colander.String(),
        title='Name')
    content = colander.SchemaNode(
        colander.String(),
        title='Content',
        widget=deform.widget.TextAreaWidget(rows=10, cols=60))


    
class MainViewer(AdminViewer):
    def __init__(self, request):
        super(MainViewer, self).__init__(request)
        self.layout.main_menu = make_main_menu(self.request)
        self._dispatch_table = dict(
            list=self.list_templates,
            create=self.create_template,
            delete=self.delete_template,
            confirmdelete=self.delete_template,
            viewentry=self.view_template,
            editentry=self.edit_template,
            )
        self.context = self.request.matchdict['context']
        self._view = self.context
        self._set_menu()
        self.dispatch()

    def _set_menu(self):
        menu = BaseMenu()
        menu.set_header('Site Text Menu')

        url = self.url(context='list', id='all')
        menu.append_new_entry('List Entries', url)

        url = self.url(context='create', id='new')
        menu.append_new_entry('Create New Entry', url)        
        self.layout.options_menus = dict(actions=menu)

            

    def list_templates(self):
        templates = self.content_mgr.tmpl_query().all()
        env = dict(templates=templates)
        rtemplate = 'leaflet:templates/list-site-templates.mako'
        self.layout.content = self.render(rtemplate, env)


    def _text_form(self):
        schema = TextSchema()
        form = deform.Form(schema, buttons=('submit',))
        self.layout.resources.deform_auto_need(form)
        return form
    
    def _text_form_submitted(self, form, action='insert'):
        controls = self.request.POST.items()
        self.layout.subheader = "submitted to database"
        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            self.layout.content = e.render()
            return
        name = data['name']
        content = data['content']
        template = self.content_mgr.add_template(name, content)
        
    def create_template(self):
        form = self._text_form()
        if 'submit' in self.request.POST:
            self._text_form_submitted(form, action='insert')
        else:
            self.layout.content = form.render()

    def _edit_template_submitted(self, form):
        controls = self.request.POST.items()
        self.layout.subheader = "submitted to database"
        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            self.layout.content = e.render()
            return
        name = data['name']
        content = data['content']
        id = int(self.request.matchdict['id'])
        t = self.content_mgr.update_template(id, content)
        self.layout.content = 'ok'

    
    def edit_template(self):
        form = self._text_form()
        id = self.request.matchdict['id']
        t = self.content_mgr.tmpl_query().get(int(id))
        data = dict(name=t.name, content=t.content)
        if 'submit' in self.request.POST:
            self._edit_template_submitted(form)
        else:
            self.layout.content = form.render(data)
            
    def delete_template(self):
        pass
    def view_template(self):
        pass
    

            
