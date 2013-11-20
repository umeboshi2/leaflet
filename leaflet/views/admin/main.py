from cStringIO import StringIO
from datetime import datetime

import transaction
from PIL import Image

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from pyramid.renderers import render

from trumpet.models.base import DBSession
from trumpet.models.sitecontent import SiteImage

from trumpet.views.menus import BaseMenu

import colander
import deform


from leaflet.views.base import AdminViewer
from leaflet.views.admin.base import make_main_menu

def prepare_main_data(request):
    layout = request.layout_manager.layout

    layout.title = 'Admin Page'
    layout.header = 'Admin Page'
    menu = make_main_menu(request)
    #layout.options_menus = dict(admin=menu)
    layout.main_menu = menu
    



class MainViewer(AdminViewer):
    def __init__(self, request):
        super(MainViewer, self).__init__(request)
        prepare_main_data(request)

