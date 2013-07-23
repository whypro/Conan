# -*- coding: utf-8 -*- 
from flask import render_template, request, redirect, url_for
from anime import anime
from bson.objectid import ObjectId
from flask.ext.login import login_required
from database import connect_db
import datetime

# 显示所有
@anime.route('/', methods=['GET'])
def show_all():
    db = connect_db()
    cur = db.tv.find().sort([('number', 1)])
    print cur.count()
    return render_template('show.html', records=cur)

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
                
                data = {'number': int(number), 'cn_title': cn_title, 'jp_title': jp_title, 'rate': None if not rate.isdigit() else int(rate), 'date': str_to_datetime(date_str)}
                cur = db.tv.insert(data) 
        return redirect(url_for('.show_all'))
    elif request.method == 'GET':
        return render_template('add.html', n=n)

def str_to_datetime(date_str):
    try:
        datetime_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except:
        datetime_obj = None
    return datetime_obj

@anime.route('/modify/<id>/', methods=['GET', 'POST'])
@login_required
def modify_record(id):
    if request.method == 'POST':
        number = request.form['number']
        # 如果 number 非空，插入记录
        if number.isdigit():
            cn_title = request.form['cn_title']
            jp_title = request.form['jp_title']
            rate = request.form['rate']
            date_str = request.form['date']
            db = connect_db()
            cur = db.tv.update({'_id': ObjectId(id)}, {'$set': {'number': int(number), 'cn_title': cn_title, 'jp_title': jp_title, 'rate': None if not rate.isdigit() else int(rate), 'date': str_to_datetime(date_str)}})
        return redirect(url_for('.show_all'))
        
    elif request.method == 'GET':
        db = connect_db()
        cur = db.tv.find_one({'_id': ObjectId(id)})
        return render_template('modify.html', record=cur)
        

@anime.route('/delete/<id>/', methods=['GET'])
@login_required
def delete_record(id):
    db = connect_db()
    cur = db.tv.remove({'_id': ObjectId(id)})
    return redirect(url_for('.show_all'))
