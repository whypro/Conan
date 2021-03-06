# -*- coding: utf-8 -*- 
from __future__ import division
from flask import render_template, request, redirect, url_for, abort, g, flash
from anime import anime
from bson.objectid import ObjectId
from flask.ext.login import login_required
from database import connect_db
import datetime
from math import ceil

# 显示所有
@anime.route('/', methods=['GET'])
def index():
    return render_template('anime_index.html')

@anime.route('/<category>/', defaults={'page': 1}, methods=['GET'])
@anime.route('/<category>/page/<int:page>/', methods=['GET'])
def show_anime(category, page):
    if category not in ('tv', 'movie'):
        abort(404)

    # 分页
    records = []
    total_pages = 0
    records_per_page = 100
    offset = (page - 1) * records_per_page
    
    db = connect_db()
    records = db[category].find().sort([('number', 1)]).skip(offset).limit(records_per_page)

    total_records = records.count(with_limit_and_skip=False)
    cur_records = records.count(with_limit_and_skip=True)
    
    total_pages = int(ceil(total_records / records_per_page)) # from __future__ import division
        
    if page != 1 and not cur_records:
        abort(404)
    
    return render_template('show.html', records=records, category=category, cur_page=page, total_pages=total_pages)


@anime.route('/<category>/add/', defaults={'n': 5}, methods=['GET', 'POST'])
@anime.route('/<category>/add/<int:n>/', methods=['GET', 'POST'])
@login_required
def add_record(category, n):
    if category not in ('tv', 'movie'):
        abort(404)

    if request.method == 'POST':
        items = dict(request.form)
        db = connect_db()
        # 循环获得记录信息
        for i in range(0, n):
            number = items['number'][i]
            # 如果 number 非空，插入记录
            if number.isdigit():
                cn_title = items['cn_title'][i]
                jp_title = items['jp_title'][i]
                rate = items['rate'][i]
                date_str = items['date'][i]
                
                data = {
                    'number': int(number), 
                    'cn_title': cn_title, 
                    'jp_title': jp_title, 
                    'rate': None if not rate.isdigit() else int(rate), 
                    'date': str_to_datetime(date_str)
                }
                cur = db[category].insert(data)
        return redirect(url_for('anime.show_anime', category=category))
    elif request.method == 'GET':
        return render_template('add.html', n=n)

def str_to_datetime(date_str):
    try:
        datetime_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except:
        datetime_obj = None
    return datetime_obj

@anime.route('/<category>/modify/<id>/', methods=['GET', 'POST'])
@login_required
def modify_record(category, id):
    if request.method == 'POST':
        if not g.user.is_admin():
            flash(u'权限不足，请联系管理员，3 秒钟内将返回首页……')
            return render_template('flash.html', target=url_for('anime.show_anime', category=category))
        else:
            number = request.form['number']
            # 如果 number 非空，插入记录
            if number.isdigit():
                cn_title = request.form['cn_title']
                jp_title = request.form['jp_title']
                rate = request.form['rate']
                date_str = request.form['date']
                db = connect_db()
                cur = db[category.lower()].update({'_id': ObjectId(id)}, {'$set': {'number': int(number), 'cn_title': cn_title, 'jp_title': jp_title, 'rate': None if not rate.isdigit() else int(rate), 'date': str_to_datetime(date_str)}})
            return redirect(url_for('anime.show_anime', category=category))

    elif request.method == 'GET':
        db = connect_db()
        cur = db[category.lower()].find_one({'_id': ObjectId(id)})
        if not cur:
            abort(404)
        else:
            return render_template('modify.html', record=cur)
        

@anime.route('/<category>/delete/<id>/', methods=['GET'])
@login_required
def delete_record(category, id):
    if not g.user.is_admin():
        flash(u'权限不足，请联系管理员，3 秒钟内将返回首页……')
        return render_template('flash.html', target=url_for('anime.show_anime', category=category))
    else:
        db = connect_db()
        cur = db[category.lower()].remove({'_id': ObjectId(id)})
        return redirect(url_for('anime.show_anime', category=category))
