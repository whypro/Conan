# -*- coding: utf-8 -*- 
from flask import render_template, request, redirect, url_for, abort
from anime import anime
from bson.objectid import ObjectId
from flask.ext.login import login_required
from database import connect_db
import datetime

# 显示所有
@anime.route('/', methods=['GET'])
def index():
    return render_template('anime_index.html')

@anime.route('/tv/', methods=['GET'])
def show_tv():
    db = connect_db()
    tv_records = db.tv.find().sort([('number', 1)])
    return render_template('show.html', records=tv_records, category='tv')
    
@anime.route('/ova/', methods=['GET'])
def show_ova():
    db = connect_db()
    ova_records = db.ova.find().sort([('number', 1)])
    return render_template('show.html', records=ova_records, category='ova')
    
@anime.route('/add/', defaults={'n': 5}, methods=['GET', 'POST'])
@anime.route('/add/<int:n>/', methods=['GET', 'POST'])
@login_required
def add_record(n):
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
                category = items['category'][i]
                
                data = {
                    'number': int(number), 
                    'cn_title': cn_title, 
                    'jp_title': jp_title, 
                    'rate': None if not rate.isdigit() else int(rate), 
                    'date': str_to_datetime(date_str)
                }
                cur = db[category.lower()].insert(data)
        return redirect(url_for('.index'))
    elif request.method == 'GET':
        return render_template('add.html', n=n)

def str_to_datetime(date_str):
    try:
        datetime_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except:
        datetime_obj = None
    return datetime_obj

@anime.route('/modify/<category>/<id>/', methods=['GET', 'POST'])
@login_required
def modify_record(category, id):
    if request.method == 'POST':
        number = request.form['number']
        # 如果 number 非空，插入记录
        if number.isdigit():
            cn_title = request.form['cn_title']
            jp_title = request.form['jp_title']
            rate = request.form['rate']
            date_str = request.form['date']
            db = connect_db()
            cur = db[category.lower()].update({'_id': ObjectId(id)}, {'$set': {'number': int(number), 'cn_title': cn_title, 'jp_title': jp_title, 'rate': None if not rate.isdigit() else int(rate), 'date': str_to_datetime(date_str)}})
        return redirect(url_for('.index'))
        
    elif request.method == 'GET':
        db = connect_db()
        cur = db[category.lower()].find_one({'_id': ObjectId(id)})
        if not cur:
            abort(404)
        else:
            return render_template('modify.html', record=cur)
        

@anime.route('/delete/<category>/<id>/', methods=['GET'])
@login_required
def delete_record(category, id):
    db = connect_db()
    cur = db[category.lower()].remove({'_id': ObjectId(id)})
    return redirect(url_for('.index'))
