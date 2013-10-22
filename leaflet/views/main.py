from trumpet.views.base import prepare_layout
from trumpet.views.base import BaseViewer

def prepare_main_layout(request):
    layout = request.layout_manager.layout
    prepare_layout(layout)
    layout.left_menu.set_header('Leaflet Menu')
    url = request.route_url('hubby_context', context='dbmeetings', id=None)
    layout.left_menu.append_new_entry('hubby', url)
    url = request.route_url('view_wiki')
    layout.left_menu.append_new_entry('wiki', url)
    url = request.route_url('rssviewer', context='listfeeds', feed=None)
    layout.left_menu.append_new_entry('rss', url)
    layout.title = 'Leaflet'
    layout.header = 'Leaflet'
    layout.subheader = 'Revealed from opening a small mailbox.'
    

    

class MainViewer(BaseViewer):
    def __init__(self, request):
        BaseViewer.__init__(self, request)
        prepare_main_layout(self.request)
        
