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

@music.route('/<category>/', methods=['GET'])
def show_music(category):
    if category not in ('op', 'ed', 'in'):
        abort(404)
    db = connect_db()
    cur = db.music.find({'category': category.upper()}).sort([('number', 1)])
    return render_template('show_music.html', records=cur, category=category)

@music.route('/<category>/add/', defaults={'n': 5}, methods=['GET', 'POST'])
@music.route('/<category>/add/<int:n>/', methods=['GET', 'POST'])
@login_required
def add_record(category, n):
    if category not in ('op', 'ed', 'in'):
        abort(404)

    if request.method == 'POST':
        items = dict(request.form)
        db = connect_db()
        # 循环获得记录信息
        for i in range(0, n):
            number = items['number'][i]
            # 如果 number 非空，插入记录
            if number.isdigit():
                cn_title = request.form['cn_title'][i]
                jp_title = request.form['jp_title'][i]
                artist = request.form['artist'][i]
                rate = request.form['rate'][i]
                begin = request.form['begin'][i]
                end = request.form['end'][i]
                
                data = {
                    'number': int(number), 
                    'cn_title': cn_title, 
                    'jp_title': jp_title, 
                    'artist': artist,
                    'rate': None if not rate.isdigit() else int(rate), 
                    'begin': begin, 
                    'end': end,
                    'category': category.upper(),
                }
                cur = db.music.insert(data)
        return redirect(url_for('music.show_music', category=category))
    elif request.method == 'GET':
        return render_template('add_music.html', n=n)


@music.route('/<category>/modify/<id>/', methods=['GET', 'POST'])
@login_required
def modify_record(category, id):
    if request.method == 'POST':
        if not g.user.is_admin():
            flash(u'权限不足，请联系管理员，3 秒钟内将返回首页……')
            return render_template('flash.html', target=url_for('music.show_music', category=category))
        else:
            number = request.form['number']
            # 如果 number 非空，插入记录
            if number.isdigit():
                cn_title = request.form['cn_title']
                jp_title = request.form['jp_title']
                artist = request.form['artist']
                rate = request.form['rate']
                begin = request.form['begin']
                end = request.form['end']

                db = connect_db()
                cur = db.music.update({'_id': ObjectId(id)}, {'$set': {'number': int(number), 'cn_title': cn_title, 'jp_title': jp_title, 'artist': artist, 'rate': None if not rate.isdigit() else int(rate), 'begin': int(begin), 'end': int(end)}})
            return redirect(url_for('music.show_music', category=category))

    elif request.method == 'GET':
        db = connect_db()
        cur = db.music.find_one({'_id': ObjectId(id)})
        if not cur:
            abort(404)
        else:
            return render_template('modify_music.html', record=cur)

@music.route('/<category>/delete/<id>/', methods=['GET'])
@login_required
def delete_record(category, id):
    if not g.user.is_admin():
        flash(u'权限不足，请联系管理员，3 秒钟内将返回首页……')
        return render_template('flash.html', target=url_for('music.show_music', category=category))
    else:
        db = connect_db()
        cur = db.music.remove({'_id': ObjectId(id)})
        return redirect(url_for('music.show_music', category=category))
