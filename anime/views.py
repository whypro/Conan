# -*- coding: utf-8 -*- 
from flask import render_template, request, redirect, url_for, g
from urllib2 import urlopen, HTTPError
from urllib import quote, urlencode
import json
import threading
from anime import anime
from pymongo import MongoClient
from pymongo.son_manipulator import AutoReference, NamespaceInjector

@anime.route('/', methods=['GET'])
def show_all():
    client = MongoClient()
    cur = client.conan.tv.find().sort([('number', 1)])
    print cur.count()
    return render_template('show.html', records=cur)
    
@anime.route('/add/', defaults={'n': 5}, methods=['GET', 'POST'])
@anime.route('/add/<int:n>', methods=['GET', 'POST'])
def add_record(n):
    if request.method == 'POST':
        items = dict(request.form)
        for number in items['number']:
            pass
        numbers = request.form.getlist('number')
        cn_titles = request.form.getlist('cn_title')
        jp_titles = request.form.getlist('jp_title')
        rates = request.form.getlist('rate')
        print dict(request.form)
#        print dir(request.form)
        return 'aaa'
        client = MongoClient()
        data = {'number': int(number), 'cn_title': cn_title, 'jp_title': jp_title, 'rate': int(rate)}
        cur = client.conan.tv.insert(data)
        return redirect(url_for('.show_all'))
    elif request.method == 'GET':
        return render_template('add.html', n=n)

@anime.route('/delete/<int:number>/', methods=['GET'])
def delete_record(number):
    client = MongoClient()
    cur = client.conan.tv.remove({'number': number})
    return redirect(url_for('.show_all'))
        
