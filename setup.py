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
    'pyramid_handlers',
    'pyramid-rpc',
    'pyramid-layout',
    'pyramid-debugtoolbar',
    'WebError',
    'FormEncode',
    'WTForms',
    'deform',  # depends on colander and peppercorn
    'pyramid-deform',
    'trumpet>=0.1dev',
    'hubby>=0.0dev',
    
    ]


setup(name='leaflet',
      version='0.0',
      description='OpenShift App',
      author='Joseph Rawson',
      author_email='joseph.rawson.works@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=requires,
      dependency_links=[
        'https://github.com/umeboshi2/trumpet/archive/master.tar.gz#egg=trumpet-0.1dev',
        'https://github.com/umeboshi2/hubby/archive/master.tar.gz#egg=hubby-0.0dev',
        ],
      )

      
      
