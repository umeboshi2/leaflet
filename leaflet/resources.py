from pyramid.security import Allow, Everyone, Authenticated
from fanstatic import Library, Resource

from haberdashery.resources import jqueryui, fullcalendar
from haberdashery.resources import ace
from haberdashery.resources import bootstrap


#from trumpet.resources import jqueryui
from trumpet.resources import StaticResources as TrumpetResources

library = Library('leaflet_lib', 'static')
css = Library('leaflet_css', 'static/css')
js = Library('leaflet_js', 'static/js')

LIBRARY_MAP = dict(css=css, js=js, libs=library)

def _get_type(filename):
    if filename.endswith('.js'):
        marker = '.js'
    elif filename.endswith('.css'):
        marker = '.css'
    else:
        raise RuntimeError, "Bad filename %s" % filename
    return marker

def minfilename(filename, marker=None):
    if marker is None:
        marker = _get_type(filename)
    prefix = filename.split(marker)[0]
    return '%s.min%s' % (prefix, marker)

def make_resource(filename, depends=None):
    ftype = _get_type(filename)
    minified = minfilename(filename, marker=ftype)
    lib = LIBRARY_MAP[ftype[1:]]
    if depends is None:
        return Resource(lib, filename, minified=minified)
    else:
        return Resource(lib, filename, minified=minified,
                        depends=depends)

favicon = Resource(library, 'favicon.ico')

main_screen = make_resource('mainscreen.css',
                           depends=[bootstrap.bootstrap])

admin_screen = make_resource('adminscreen.css',
                             depends=[bootstrap.bootstrap])

post_to_url = make_resource('post2url.js', depends=[jqueryui])



show_attachments = Resource(js, 'show-attachments.js', depends=[jqueryui])

common_page = make_resource('common-page.js', depends=[jqueryui,
                                                       bootstrap.bootstrap])

main_calendar_view = make_resource('main-calendar-view.js',
                              depends=[fullcalendar])

admin_show_path_content = make_resource('admin-show-path-content.js',
                                   depends=[jqueryui])
admin_list_site_paths = make_resource('list-site-paths.js', depends=[jqueryui])
admin_list_site_resources = make_resource('admin-list-site-resources.js',
                                     depends=[jqueryui])
admin_edit_site_resources = make_resource('admin-edit-site-resources.js',
                                     depends=[ace.ace, jqueryui])


class StaticResources(TrumpetResources):
    main_screen = main_screen
    admin_screen = admin_screen
    
    # override trumpet favicon
    favicon = favicon
    
    common_page = common_page

    main_calendar_view = main_calendar_view
    
    admin_list_site_paths = admin_list_site_paths
    admin_show_path_content = admin_show_path_content
    admin_list_site_resources = admin_list_site_resources
    admin_edit_site_resources = admin_edit_site_resources
    
    post_to_url = post_to_url
    show_attachments = show_attachments
    
# the acl entries are allow/deny, group, permission
class RootGroupFactory(object):
    __name__ = ""
    __acl__ = [
        (Allow, Everyone, 'public'),
        (Allow, Authenticated, 'user'),
        (Allow, 'manager', 'manage'),
        (Allow, 'editor', ('wiki_add', 'wiki_edit')),
        (Allow, 'admin', ('admin', 'manage')),
        ]

    def __init__(self, request):
        # comment
        pass


