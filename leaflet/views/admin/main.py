from cStringIO import StringIO
from datetime import datetime

import transaction
from PIL import Image

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from pyramid.renderers import render

from trumpet.models.base import DBSession
from trumpet.models.sitecontent import SiteImage

from trumpet.views.base import NotFound
#from trumpet.views.base import BaseViewer, make_main_menu
from trumpet.views.menus import BaseMenu

import colander
import deform


from leaflet.views.base import AdminViewer, make_main_menu

def prepare_main_data(request):
    layout = request.layout_manager.layout
    menu = layout.ctx_menu
    url = request.route_url('admin_users', context='list', id='all')
    menu.append_new_entry('Manage Users', url)
    url = request.route_url('admin_sitetext', context='list', id=None)
    menu.append_new_entry('Manage Text', url)
    url = request.route_url('admin_images', context='list', id=None)
    menu.append_new_entry('Manage Images', url)
    main_menu = make_main_menu(request)
    layout.title = 'Admin Page'
    layout.header = 'Admin Page'
    layout.main_menu = main_menu.render()
    layout.ctx_menu = menu


class MainViewer(AdminViewer):
    def __init__(self, request):
        super(MainViewer, self).__init__(request)
        prepare_main_data(request)

