import os

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

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

from trumpet.security import authn_policy, authz_policy

dbhost = os.environ['OPENSHIFT_POSTGRESQL_DB_HOST']
dbport = os.environ['OPENSHIFT_POSTGRESQL_DB_PORT']
dbuser = os.environ['OPENSHIFT_POSTGRESQL_DB_USERNAME']
dbpass = os.environ['OPENSHIFT_POSTGRESQL_DB_PASSWORD']


dburl = "postgresql://%s:%s@%s:%s/leaflet"
dburl = dburl % (dbuser, dbpass, dbhost, dbport)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    dbsettings = {'sqlalchemy.url': dburl}
    engine = engine_from_config(dbsettings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    initialize_sql(engine, [populate,
                            populate_wiki,
                            populate_feeds])
    config = Configurator(settings=settings)
    configure_static(config)
    configure_base_layout(config)
    
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_view('trumpet.views.main.MainViewer',
                    route_name='home',
                    renderer=basetemplate,
                    layout='base')
    return config.make_wsgi_app()

