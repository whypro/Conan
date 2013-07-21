# -*- coding: utf-8 -*-
import os
from conan import create_app
app = create_app('config')
    
if 'SERVER_SOFTWARE' in os.environ:
    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)

elif __name__ == '__main__':
    app.run()
    