from trumpet.config.base import basetemplate
from trumpet.config.base import add_view

main_view = 'leaflet.views.admin.main.MainViewer'


def configure_admin(config, rootpath='/admin', permission='admin'):
    config.add_route('admin', rootpath)
    add_view(config, main_view, 'admin', permission=permission)
    config.add_route('admin_images', '%s/images/{context}/{id}' % rootpath)
    add_view(config, 'leaflet.views.admin.images.ImageManagementViewer',
             'admin_images', permission=permission)
    config.add_route('admin_sitetext', '%s/sitetext/{context}/{id}' % rootpath)
    add_view(config, 'leaflet.views.admin.sitetext.SiteTextViewer',
             'admin_sitetext', permission=permission)
    config.add_route('admin_users', '%s/users/{context}/{id}' % rootpath)
    add_view(config, 'leaflet.views.admin.users.UserManagementViewer',
               'admin_users', permission=permission)

    route = 'admin_site_templates'
    config.add_route(route, '%s/sitetemplates/{context}/{id}' % rootpath)
    add_view(config, 'leaflet.views.admin.templatemgr.MainViewer',
             route, permission=permission)
    
    route = 'admin_sitecontent_mgr'
    config.add_route(route, '%s/sitecontentmgr/{context}/{id}' % rootpath)
    add_view(config, 'leaflet.views.admin.contentmgr.MainViewer',
             route, permission=permission)
    
