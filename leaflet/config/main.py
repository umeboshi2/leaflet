from trumpet.config.base import basetemplate
from trumpet.config.base import add_view

viewers = dict(contacts='ContactViewer',
               clients='ClientViewer',
               calendar='CalendarViewer',)


def configure_mainevent(config, rootpath='/mainevent'):
    route_name = 'mainevent_venue'
    config.add_route(route_name, '%s/venue/{context}/{id}' % rootpath)
    config.add_view('leaflet.views.venues.MainViewer',
                    route_name=route_name,
                    renderer=basetemplate,
                    layout='base',)
    
    
def configure_hubby(config, rootpath='/hubby'):
    route_name = 'hubby_main'
    config.add_route(route_name, '%s/main/{context}/{id}' % rootpath)
    #add_view(config, 'leaflet.views.vhubby.MainViewer', route_name)
    config.add_view('leaflet.views.vhubby.MainViewer',
                    route_name=route_name,
                    renderer=basetemplate,
                    layout='base',)
    route_name = 'hubby_json'
    config.add_route(route_name, '%s/json/{context}/{id}' % rootpath)
    config.add_view('leaflet.views.hubjson.MainViewer',
                    route_name=route_name,
                    renderer='json',
                    layout='base',)
    route_name = 'hubby_frag'
    config.add_route(route_name, '%s/frag/{context}/{id}' % rootpath)
    config.add_view('leaflet.views.hubjax.MainViewer',
                    route_name=route_name,
                    renderer='string',
                    layout='base',)
    
    
def configure_wiki(config, rootpath):
    wiki_view = 'leaflet.views.wiki.WikiViewer'
    config.add_route('view_wiki', rootpath)
    add_view(config, wiki_view, 'view_wiki')

    config.add_route('list_pages', '%s/listpages' % rootpath)
    add_view(config, wiki_view, 'list_pages')

    config.add_route('view_page', '%s/{pagename}' % rootpath)
    add_view(config, wiki_view, 'view_page')

    config.add_route('add_page', '%s/add_page/{pagename}' % rootpath)
    add_view(config, wiki_view, 'add_page', permission='wiki_add')

    config.add_route('edit_page', '%s/{pagename}/edit_page' % rootpath)
    add_view(config, wiki_view, 'edit_page', permission='wiki_edit')

