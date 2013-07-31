# -*- coding: utf-8 -*- 
from flask import render_template, request, redirect, url_for, abort, g, flash
from music import music
from bson.objectid import ObjectId
from flask.ext.login import login_required
from database import connect_db
import datetime

# 显示所有
@music.route('/', methods=['GET'])
def index():
    db = connect_db()
    cur = db.music.find({'category': 'OP'}).sort([('number', 1)])
    return render_template('music_index.html', records=cur, category='op')

    

