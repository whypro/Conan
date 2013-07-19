# -*- coding: utf-8 -*- 
from flask import render_template, request, redirect, url_for
from anime import anime
from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.son_manipulator import AutoReference, NamespaceInjector
from run import app

# 显示所有
@anime.route('/', methods=['GET'])
def show_all():
    db = connect_db()
    cur = db.tv.find().sort([('number', 1)])
    print cur.count()
    return render_template('show.html', records=cur)

@anime.route('/add/', defaults={'n': 5}, methods=['GET', 'POST'])
@anime.route('/add/<int:n>/', methods=['GET', 'POST'])
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
                
                data = {'number': int(number), 'cn_title': cn_title, 'jp_title': jp_title, 'rate': None if not rate.isdigit() else int(rate)}
                cur = db.tv.insert(data) 
        return redirect(url_for('.show_all'))
    elif request.method == 'GET':
        return render_template('add.html', n=n)

@anime.route('/delete/<id>/', methods=['GET'])
def delete_record(id):
    db = connect_db()
    cur = db.tv.remove({'_id': ObjectId(id)})
    return redirect(url_for('.show_all'))

def connect_db():
    client = MongoClient(app.config['DB_HOST'], app.config['DB_PORT'])
    db = client[app.config['DB_DATABASE']]
    db.authenticate(app.config['DB_USERNAME'], app.config['DB_PASSWORD'])
    return db