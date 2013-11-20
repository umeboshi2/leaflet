from cStringIO import StringIO
from datetime import datetime

import transaction

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from pyramid.renderers import render
from pyramid.response import Response


from trumpet.models.sitecontent import SiteText

from trumpet.resources import MemoryTmpStore

from trumpet.managers.admin.images import ImageManager

from trumpet.views.menus import BaseMenu

from leaflet.views.base import AdminViewer
from leaflet.views.admin.base import make_main_menu
from leaflet.managers.wiki import WikiArchiver


import colander
import deform

tmpstore = MemoryTmpStore()


class EditSiteTextSchema(colander.Schema):
    name = colander.SchemaNode(
        colander.String(),
        title='Name')
    content = colander.SchemaNode(
        colander.String(),
        title='Content',
        widget=deform.widget.TextAreaWidget(rows=10, cols=60))


    
class SiteTextViewer(AdminViewer):
    def __init__(self, request):
        super(SiteTextViewer, self).__init__(request)
        self.layout.main_menu = make_main_menu(request)
        self.images = ImageManager(self.request.db)
        self._dispatch_table = dict(
            list=self.list_site_text,
            add=self.create_site_text,
            delete=self.main,
            confirmdelete=self.main,
            viewentry=self.view_site_text,
            editentry=self.edit_site_text,
            create=self.create_site_text,
            download_wiki_archive=self.download_wiki_archive,)
        self.context = self.request.matchdict['context']
        self._view = self.context
        self._set_options_menu()
        self.dispatch()


            
    def _set_options_menu(self):
        menu = BaseMenu()
        menu.set_header('Site Text Actions')

        url = self.url(context='list', id='all')
        menu.append_new_entry('List Entries', url)

        url = self.url(context='create', id='new')
        menu.append_new_entry('Create New Entry', url)        

        url = self.url(context='download_wiki_archive', id='all')
        menu.append_new_entry('Download Wiki Archive', url)
        self.layout.options_menus = dict(actions=menu)
        
    def main(self):
        content = '<h1>Here is where we manage site text.</h1>'
        self.layout.content = content


    def manage_site_text(self):
        action = None
        if 'action' in self.request.GET:
            action = self.request.GET['action']
            return self._manage_site_text_action_map[action]()
            
        
    def view_site_text(self):
        id = int(self.request.matchdict['id'])
        self.layout.footer = str(type(id))
        entry = self.request.db.query(SiteText).get(id)
        self.layout.subheader = entry.name
        self.layout.content = '<pre width="80">%s</pre>' % entry.content


    def list_site_text(self):
        template = 'leaflet:templates/list-site-text.mako'
        entries = self.request.db.query(SiteText).all()
        env = dict(viewer=self, entries=entries)
        self.layout.content = self.render(template, env)
        
    def _edit_site_text_form(self):
        schema = EditSiteTextSchema()
        submit_button = deform.form.Button(name='submit_site_text',
                                           title='Update Content')
        form = deform.Form(schema, buttons=(submit_button,))
        self.layout.resources.deform_auto_need(form)
        return form

    def _validate_site_text(self, form, create=False):
        controls = self.request.POST.items()
        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            self.layout.content = e.render()
            return {}
        if create:
            db = self.request.db
            query = db.query(SiteText).filter_by(name=data['name'])
            rows = query.all()
            if rows:
                h1 = '<h1>Site Text "%s" already exists.</h1>'
                h1 = h1 % data['name']
                self.layout.content = h1 + form.render(data)
                return {}
            else:
                self.layout.subheader = str(rows)
        return data
    
    def _submit_site_text(self, form, data={}):
        rendered = form.render(data)
        if 'submit_site_text' in self.request.params:
            if not self._validate_site_text(form):
                return

        else:
            self.layout.content = rendered
            self.layout.subheader = 'Please edit content'
            
    def create_site_text(self):
        form = self._edit_site_text_form()
        # check submission
        if 'submit_site_text' in self.request.params:
            valid = self._validate_site_text(form, create=True)
            if not valid:
                return
            transaction.begin()
            entry = SiteText(valid['name'], valid['content'])
            self.request.db.add(entry)
            transaction.commit()
            self.layout.content = 'Submitted for approval.'            
        else:
            self.layout.content = form.render()
            self.layout.subheader = 'Please edit content'

        

    def edit_site_text(self):
        form = self._edit_site_text_form()
        rendered = form.render()
        id = int(self.request.matchdict['id'])
        entry = self.request.db.query(SiteText).get(id)
        data = dict(name=entry.name, content=entry.content)
        if 'submit_site_text' in self.request.params:
            valid = self._validate_site_text(form)
            if not valid:
                return
            transaction.begin()
            entry.content = valid['content']
            self.request.db.add(entry)
            transaction.commit()
            self.layout.content = 'Submitted for approval.'            
        else:
            self.layout.content = form.render(data)
            self.layout.subheader = 'Please edit content'
            

    def download_wiki_archive(self):
        archiver = WikiArchiver(self.request.db)
        archiver.create_new_zipfile()
        archive = archiver.archive_pages()
        content_type = 'application/zip'
        r = Response(content_type=content_type, body=archive)
        r.content_disposition = 'attachment; filename="tutwiki-archive.zip"'
        self.response = r
        
