import os

from setuptools import setup, find_packages

#here = os.path.abspath(os.path.dirname(__file__))
#README = open(os.path.join(here, 'README.txt')).read()
#CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'trumpet>=0.1.1dev', # pull from github
    'hubby>=0.0dev', # pull from github
    ]

setup(name='leaflet',
      version='0.0',
      description='leaflet',
      long_description="long description",
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Joseph Rawson',
      author_email='joseph.rawson.works@littledebian.org',
      url='https://github/umeboshi2/leaflet',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='leaflet',
      install_requires=requires,
      dependency_links=[
        'https://github.com/umeboshi2/trumpet/archive/master.tar.gz#egg=trumpet-0.1.1dev',
        'https://github.com/umeboshi2/hubby/archive/master.tar.gz#egg=hubby-0.0dev',
        ],
      entry_points="""\
      [paste.app_factory]
      main = leaflet:main
      [console_scripts]
      initialize_leaflet_db = leaflet.scripts.initializedb:main
      [fanstatic.libraries]
      leaflet_lib = leaflet.resources:library
      leaflet_css = leaflet.resources:css
      leaflet_js = leaflet.resources:js
      """,
      )
