# -*- coding: utf-8 -*- 
from flask import render_template, request, redirect, url_for, abort, flash
from admin import admin
from backup import backup_db, restore_db

from flask.ext.login import login_required
from database import connect_db

# 首页
@admin.route('/', methods=['GET'])
def index():
    return render_template('admin_index.html')

# 备份数据库
@admin.route('/backup/', methods=['GET', 'POST'])
@login_required
def backup():
    if request.method == 'POST':
        backup_db()
        flash(u'备份成功，3 秒钟内将返回首页……')
        return render_template('flash.html', target=url_for('index'))
    elif request.method == 'GET':
        return render_template('backup.html')

# 恢复数据库
@admin.route('/restore/', methods=['GET', 'POST'])
@login_required
def restore():
    if request.method == 'POST':
        restore_db('ai')
        flash(u'恢复成功，3 秒钟内将返回首页……')
        return render_template('flash.html', target=url_for('index'))
    elif request.method == 'GET':
        return render_template('restore.html')
