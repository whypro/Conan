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
    return render_template('music_index.html')

@music.route('/op/', methods=['GET'])
def show_op():
    db = connect_db()
    cur = db.music.find({'category': 'OP'}).sort([('number', 1)])
    return render_template('show_music.html', records=cur, category='op')

@music.route('/ed/', methods=['GET'])
def show_ed():
    db = connect_db()
    cur = db.music.find({'category': 'ED'}).sort([('number', 1)])
    return render_template('show_music.html', records=cur, category='ed')

@music.route('/in/', methods=['GET'])
def show_in():
    db = connect_db()
    cur = db.music.find({'category': 'IN'}).sort([('number', 1)])
    return render_template('show_music.html', records=cur, category='in')
