import re
from datetime import datetime

import transaction
from docutils.core import publish_parts

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from pyramid.view import view_config

import colander
import deform

from leaflet.models.base import DBSession
from trumpet.models.sitecontent import SiteText

from trumpet.views.base import render_rst
from trumpet.views.menus import BaseMenu

from leaflet.views.base import BaseViewer
from leaflet.views.base import make_main_menu

from leaflet.managers.wiki import WikiManager

# regular expression used to find WikiWords
wikiwords = re.compile(r":\b([A-Z]\w+[A-Z]+\w+)")

EDIT_PAGE_FORM = """<form action="%s" method="post">
          <textarea name="body" rows="10"
                    cols="60">%s</textarea><br/>
          <input type="submit" name="form.submitted" value="Save">
        </form>"""


class EditPageSchema(colander.Schema):
    body = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(rows=10, cols=60),
        )
    

class AddPageSchema(colander.Schema):
    body = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(rows=10, cols=60),
        )
    
    
def _anchor(href, value):
    return '<a href="%s">%s</a>' % (href, value)


def prepare_main_data(request):
    layout = request.layout_manager.layout
    layout.title = 'Wiki Page'
    layout.header = 'Wiki Page'
    layout.main_menu = make_main_menu(request)
    


class WikiViewer(BaseViewer):
    def __init__(self, request):
        super(WikiViewer, self).__init__(request)
        # dispatch table
        self._dispatch_table = dict(view_wiki=self.view_wiki,
                                    view_page=self.view_page,
                                    add_page=self.add_page,
                                    edit_page=self.edit_page,
                                    list_pages=self.list_pages)
        self.route = request.matched_route.name
        self.pages = WikiManager(self.request.db)
        self._view = self.route
        prepare_main_data(self.request)
        
        menu = BaseMenu()
        menu.set_header('Wiki Menu')
        url = self.request.route_url('view_page', pagename='MainPlan')
        menu.append_new_entry('Main Plan', url)
        url = self.request.route_url('list_pages')
        menu.append_new_entry('List Pages', url)
        self.layout.options_menus = dict(actions=menu)
        
        
        getattr(self, self.route)()
        
    def _anchor(self, href, value):
        return '<a href="%s">%s</a>' % (href, value)

    def view_wiki(self):
        location = self.request.route_url('view_page', pagename='FrontPage')
        self.response = HTTPFound(location=location)

    def view_page(self):
        pagename = self.request.matchdict['pagename']
        page = self.pages.getbyname(pagename)
        if page is None:
            location = self.url(route='add_page', pagename=pagename)
            self.response = HTTPFound(location=location)
            return

        def check(match):
            word = match.group(1)
            exists = self.pages.list_pages()
            if exists:
                url = self.url(route='view_page', pagename=word)
            else:
                url = self.url(route='add_page', pagename=word)
            return self._anchor(url, word)
        # this is a sad "markup" system
        # good for a tutorial, but needs to be better
        # for actual use.
        content = render_rst(page.content)
        content = wikiwords.sub(check, content)

        edit_url = self.url(route='edit_page', pagename=pagename)
        # We should check the session here
        # this is from tutorial, but we need better
        # solution.
        #logged_in = authenticated_userid(self.request)
        l = self.layout
        l.title = "Wiki: %s" % page.name
        l.header = page.name
        l.content = content
        l.footer = self._anchor(edit_url, "Edit Page")
        

    def _page_form_submitted(self, form, page=None):
        controls = self.request.POST.items()
        try:
            data = form.validate(controls)
        except deform.ValidationFailure, e:
            self.layout.content = e.render()
            return
        content = data['body']
        if page is not None:
            page = self.pages.update_page(page.id, content)
        else:
            name = self.request.matchdict['pagename']
            page = self.pages.add_page(name, content)
        return page
    
    def add_page(self):
        name = self.request.matchdict['pagename']
        schema = AddPageSchema()
        form = deform.Form(schema, buttons=('submit',))
        self.layout.resources.deform_auto_need(form)
        if 'submit' in self.request.POST:
            self._page_form_submitted(form)
            self.response = HTTPFound(
                self.url(route='view_page', pagename=name))
        else:
            self.layout.content = form.render()
        self.layout.footer = "adding page"
        
    def edit_page(self):
        name = self.request.matchdict['pagename']
        page = self.pages.getbyname(name)
        formdata = dict(body=page.content)
        schema = EditPageSchema()
        form = deform.Form(schema, buttons=('submit',))
        self.layout.resources.deform_auto_need(form)
        if 'submit' in self.request.POST:
            self._page_form_submitted(form, page=page)
            self.response = HTTPFound(
                self.url(route='view_page', pagename=name))
        else:
            self.layout.content = form.render(formdata)
        self.layout.footer = "editing page"


    def list_pages(self):
        pages = self.request.db.query(SiteText).filter_by(type='tutwiki').all()
        pagelist = []
        for page in pages:
            url = self.url(route='view_page', pagename=page.name)
            anchor = self._anchor(url, page.name)
            pagelist.append('<li>%s</li>' % anchor)
        ul = '<ul>%s</ul>' % '\n'.join(pagelist)
        self.layout.content = ul

