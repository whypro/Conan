# -*- coding: utf-8 -*-
from flask import Blueprint

anime = Blueprint('anime', __name__, template_folder='templates', static_folder='static', static_url_path='/%s' % __name__)