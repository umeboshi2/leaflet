from trumpet.config.base import basetemplate
from trumpet.config.base import add_view

viewers = dict(contacts='ContactViewer',
               clients='ClientViewer',
               calendar='CalendarViewer',)


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

