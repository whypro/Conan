# -*- coding: utf-8 -*-
from flask import Blueprint

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static', static_url_path='/%s' % __name__)