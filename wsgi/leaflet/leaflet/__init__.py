import os

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid_beaker import session_factory_from_settings

from trumpet.security import authn_policy, authz_policy

from trumpet.models.base import DBSession, Base
from trumpet.models.usergroup import populate
from trumpet.models.wiki import populate_wiki
from trumpet.models.rssdata import populate_feeds
from trumpet.models.base import initialize_sql

from trumpet.config.base import basetemplate, configure_base_layout
from trumpet.config.static import configure_static
from trumpet.config.wiki import configure_wiki
from trumpet.config.rssviewer import configure_rssviewer
from trumpet.config.login import configure_login


def get_dburl():
    dbhost = os.environ['OPENSHIFT_POSTGRESQL_DB_HOST']
    dbport = os.environ['OPENSHIFT_POSTGRESQL_DB_PORT']
    dbuser = os.environ['OPENSHIFT_POSTGRESQL_DB_USERNAME']
    dbpass = os.environ['OPENSHIFT_POSTGRESQL_DB_PASSWORD']
    #dbprefix = os.environ['OPENSHIFT_POSTGRESQL_DB_URL']
    #dbuser = '%s/leaflet' % dbprefix
    dburl = "postgresql://%s:%s@%s:%s/leaflet"
    dburl = dburl % (dbuser, dbpass, dbhost, dbport)
    return dburl

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if 'OPENSHIFT_POSTGRESQL_DB_HOST' in os.environ:
        settings['sqlalchemy.url'] = get_dburl()
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    initialize_sql(engine, [populate,
                            populate_wiki,
                            populate_feeds])
    session_factory = session_factory_from_settings(settings)
    root_factory = 'trumpet.resources.RootGroupFactory'
    request_factory = 'trumpet.request.AlchemyRequest'
    config = Configurator(settings=settings,
                          root_factory=root_factory,
                          request_factory=request_factory,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy,
                          session_factory=session_factory
                          )
    configure_static(config)
    configure_base_layout(config)
    
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_view('trumpet.views.main.MainViewer',
                    route_name='home',
                    renderer=basetemplate,
                    layout='base')

    configure_login(config)
    configure_rssviewer(config, '/rssviewer')
    configure_wiki(config, '/wiki')

    config.add_route('hubby', '/hubby')
    config.add_route('hubby_context', '/hubby/{context}/{id}')
    config.add_route('hubby_collect', '/hubby/collect/{object}/{id}')
    for route in ['hubby', 'hubby_context']:
        config.add_view('leaflet.views.vhubby.MainViewer',
                        route_name=route,
                        renderer=basetemplate,
                        layout='base')

    
    return config.make_wsgi_app()



