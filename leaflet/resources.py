from fanstatic import Library
from fanstatic import Resource


library = Library('leaflet', 'static')

show_attachments = Resource(library, 'show_attachments.js')

hubby_css = Resource(library, 'hubbycss/stylesheets/screen.css')
