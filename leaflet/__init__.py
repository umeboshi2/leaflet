import os
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid_beaker import session_factory_from_settings

from trumpet.config.base import basetemplate, configure_base_layout
from trumpet.models.sitecontent import SitePath
from trumpet.managers.admin.siteviews import PyramidConfigManager

from leaflet.security import make_authn_authz_policies, authenticate
from leaflet.models.base import DBSession, Base
from leaflet.config.admin import configure_admin
from leaflet.config.main import configure_wiki
from leaflet.config.main import configure_hubby
from leaflet.config.main import configure_mainevent

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # set app name
    appname = 'leaflet'
    from leaflet.resources import RootGroupFactory
    root_factory = RootGroupFactory
    # alchemy request provides .db method
    request_factory = 'trumpet.request.AlchemyRequest'
    # get admin username
    admin_username = settings.get('leaflet.admin.admin_username', 'admin')
    # create db engine
    engine = engine_from_config(settings, 'sqlalchemy.')
    # setup db.sessionmaker
    settings['db.sessionmaker'] = DBSession
    # bind session to engine
    DBSession.configure(bind=engine)
    # bind objects to engine
    Base.metadata.bind = engine
    from trumpet.models.base import Base as TrumpetBase
    TrumpetBase.metadata.bind = engine
    if settings.get('db.populate', 'False') == 'True':
        import leaflet.models.eventmodels
        from leaflet.models.main import make_test_data
        Base.metadata.create_all(engine)
        TrumpetBase.metadata.create_all(engine)
        #initialize_sql(engine)
        #make_test_data(DBSession)
        from leaflet.models.initialize import initialize_database
        from leaflet.models.initialize import IntegrityError
        initialize_database(settings)
    
        #vmgr = PyramidConfigManager(DBSession)
        #try:
        #    vmgr.add_route('view_wiki', '/foowiki')
        #    vmgr.add_route('list_pages', '/foowiki/listpages')
        #    vmgr.add_route('view_page', '/foowiki/{pagename}')
        #    vmgr.add_route('add_page', '/foowiki/add_page/{pagename}')
        #    vmgr.add_route('edit_page', '/foowiki/{pagename}/edit_page')
        #    
        #    wikiview = 'leaflet.views.wiki.WikiViewer'
        #    vmgr.add_view(vmgr.get_route_id('view_wiki'), wikiview)
        #    vmgr.add_view(vmgr.get_route_id('list_pages'), wikiview)
        #    vmgr.add_view(vmgr.get_route_id('view_page'), wikiview)
        #    vmgr.add_view(vmgr.get_route_id('add_page'), wikiview,
        #                  permission='wiki_add')
        #    vmgr.add_view(vmgr.get_route_id('edit_page'), wikiview,
        #                  permission='wiki_edit')
        #except IntegrityError:
        #    import transaction
        #    transaction.abort()
        #    
        
        
    # setup authn and authz
    secret = settings['%s.authn.secret' % appname]
    cookie = settings['%s.authn.cookie' % appname]
    timeout = int(settings['%s.authn.timeout' % appname])
    authn_policy, authz_policy = make_authn_authz_policies(
        secret, cookie, callback=authenticate,
        timeout=timeout, tkt=False)
    root_factory.authn_policy = authn_policy

    # create config object
    config = Configurator(settings=settings,
                          root_factory=root_factory,
                          request_factory=request_factory,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)
    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)

    config.include('pyramid_fanstatic')

    config.include(configure_base_layout)
    config.include(configure_admin)
    configure_wiki(config, '/pkg_wiki')
    #vmgr = PyramidConfigManager(DBSession)
    #vmgr.configure(config)
    config.add_static_view('static',
                           'leaflet:static', cache_max_age=3600)
    ##################################
    # Main Views
    ##################################
    config.add_route('home', '/')
    config.add_view('leaflet.views.main.MainViewer',
                    layout='base',
                    renderer=basetemplate,
                    route_name='home')
    config.add_route('main', '/main/{context}/{id}')
    config.add_view('leaflet.views.main.MainViewer',
                    layout='base',
                    renderer=basetemplate,
                    route_name='main')
    config.add_route('initdb', '/initdb/{context}/{id}')
    config.add_view('leaflet.views.main.MainViewer',
                    layout='base',
                    renderer=basetemplate,
                    route_name='initdb')
    config.add_route('blob', '/blob/{filetype}/{id}')
    config.add_view('trumpet.views.blobs.BlobViewer', route_name='blob',
                    renderer='string',
                    layout='base')
    ##################################
    # Hubby Views
    ##################################
    configure_hubby(config, '/hubby')

    # more views
    configure_mainevent(config)
    ##################################
    # Login Views
    ##################################
    login_viewer = 'leaflet.views.login.LoginViewer'
    config.add_route('login', '/login')
    config.add_view(login_viewer,
                    renderer=basetemplate,
                    layout='base',
                    route_name='login')
    
    
    config.add_route('logout', '/logout')
    config.add_view(login_viewer,
                    renderer=basetemplate,
                    layout='base',
                    route_name='logout')

    
    # Handle HTTPForbidden errors with a
    # redirect to a login page.
    config.add_view(login_viewer,
                    context='pyramid.httpexceptions.HTTPForbidden',
                    renderer=basetemplate,
                    layout='base')
    ##################################

    ##################################
    # Views for Users
    ##################################
    config.add_route('user', '/user/{context}')
    config.add_view('leaflet.views.userview.MainViewer',
                    route_name='user',
                    renderer=basetemplate,
                    layout='base',
                    permission='user')
    
    ##################################
    
    
    app = config.make_wsgi_app()

    # FIXME: maybe do this somewhere else?
    # wrap app with Fanstatic
    from fanstatic import Fanstatic
    return Fanstatic(app)

