from trumpet.views.base import BaseViewer as TrumpetViewer
from trumpet.views.base import BaseMenu
from trumpet.views.menus import BaseMenu, TopBar

from leaflet.resources import StaticResources
from leaflet.models.usergroup import User

from leaflet.views.util import prepare_user_menu, prepare_layout
from leaflet.views.util import get_admin_username, get_user_id
from leaflet.views.util import get_regular_users



def make_main_menu(request):
    menu = BaseMenu(header='Main Menu', class_='submenu')
    user = request.session.get('user', None)
    logged_in = user is not None
    if 'user' in request.session:
        user = request.session['user']
        url = request.route_url('view_wiki')
        menu.append_new_entry('Wiki', url)
        url = request.route_url('mainevent_venue', context='main', id='main')
        menu.append_new_entry('Venues', url)
        
    url = request.route_url('hubby_main', context='main', id='calendar')
    menu.append_new_entry('Hubby', url)
    return menu
    
class BaseViewer(TrumpetViewer):
    def __init__(self, request):
        super(BaseViewer, self).__init__(request)
        prepare_layout(self.layout)
        self.layout.user_menu = prepare_user_menu(request)
        self.css = self.layout.resources.main_screen
        
    def __call__(self):
        if hasattr(self, 'css'):
            self.css.need()
        return super(BaseViewer, self).__call__()

    def get_admin_username(self):
        return get_admin_username(self.request)

    def is_admin_authn(self, authn):
        username = self.get_admin_username()
        user_id = get_user_id(self.request, username)
        return authn == user_id

    def get_current_user(self):
        user_id = self.get_current_user_id()
        return self.request.db.query(User).get(user_id)
    

    
class AdminViewer(BaseViewer):
    def __init__(self, request):
        super(AdminViewer, self).__init__(request)
        self.css = self.layout.resources.admin_screen
        
