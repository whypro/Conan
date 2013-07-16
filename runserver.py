# -*- coding: utf-8 -*-
from flask import Flask, g
import os
from anime import anime
from anime.views import *

app = Flask(__name__)
app.config.from_object('config')
app.register_blueprint(anime, url_prefix='/anime')
app.debug = True
    
if 'SERVER_SOFTWARE' in os.environ:
    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)

elif __name__ == '__main__':
    app.run()
    