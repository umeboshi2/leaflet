from setuptools import setup

requires = [
    'pyramid',
    'repoze.tm2>=1.0b1', # default_commit_veto
    'sqlalchemy',
    'zope.sqlalchemy',
    'Mako',
    'docutils',
    'feedparser',
    'mechanize',
    'beautifulsoup4',
    'pyramid-beaker',
    'pyramid-tm',
    'pyramid-rpc',
    'pyramid-layout',
    'pyramid-debugtoolbar',
    'WebError',
    'FormEncode',
    'WTForms',
    'trumpet>=0.1.1dev', # pull from github
    'hubby>=0.0dev',   # pull from github
    'waitress',
    ]


setup(name='leaflet_openshift',
      version='0.0',
      description='OpenShift App',
      author='Joseph Rawson',
      author_email='joseph.rawson.works@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=requires,
      dependency_links=[
        'https://github.com/umeboshi2/trumpet/archive/master.tar.gz#egg=trumpet-0.1.1dev',
        'https://github.com/umeboshi2/hubby/archive/master.tar.gz#egg=hubby-0.0dev',
        ],
      entry_points={
        'fanstatic.libraries' : [
            'trumpet = trumpet.resources:library',
            'leaflet = leaflet.resources:library',
            ]
        }
      )

      
      
