import os

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )

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
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    return config.make_wsgi_app()

