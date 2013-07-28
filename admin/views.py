# -*- coding: utf-8 -*- 
from flask import render_template, request, redirect, url_for, abort, flash, g
from admin import admin
from database import backup_db, restore_db

from flask.ext.login import login_required
from database import connect_db
import hashlib
from bson.objectid import ObjectId

# 首页
@admin.route('/', methods=['GET'])
def index():
    return render_template('admin_index.html')

# 备份数据库
@admin.route('/backup/', methods=['GET', 'POST'])
@login_required
def backup():
    if request.method == 'POST':
        if not g.user.is_admin():
            flash(u'权限不足，请联系管理员，3 秒钟内将返回首页……')
            return render_template('flash.html', target=url_for('admin.index'))
        else:
            backup_db()
            flash(u'备份成功，3 秒钟内将返回首页……')
            return render_template('flash.html', target=url_for('admin.index'))
    elif request.method == 'GET':
        return render_template('backup.html')

# 恢复数据库
@admin.route('/restore/', methods=['GET', 'POST'])
@login_required
def restore():
    if request.method == 'POST':
        if not g.user.is_admin():
            flash(u'权限不足，请联系管理员，3 秒钟内将返回首页……')
            return render_template('flash.html', target=url_for('admin.index'))
        else:
            restore_db()
            flash(u'恢复成功，3 秒钟内将返回首页……')
            return render_template('flash.html', target=url_for('admin.index'))
    elif request.method == 'GET':
        return render_template('restore.html')

@admin.route('/user/', methods=['GET'])
def show_user():
    if not g.user.is_admin():
        flash(u'权限不足，请联系管理员，3 秒钟内将返回首页……')
        return render_template('flash.html', target=url_for('admin.index'))
    else:
        db = connect_db()
        users = db.user.find().sort([('username', 1)])
        return render_template('user.html', users=users)
            
@admin.route('/user/delete/<id>/', methods=['GET'])
@login_required
def delete_user(id):
    if not g.user.is_admin():
        flash(u'权限不足，请联系管理员，3 秒钟内将返回首页……')
        return render_template('flash.html', target=url_for('admin.index'))
    elif g.user.get_id() == id:
        flash(u'不能删除你自己，3 秒钟内将返回首页……')
        return render_template('flash.html', target=url_for('admin.index'))
    else:
        db = connect_db()
        db.user.remove({'_id': ObjectId(id)})
        return redirect(url_for('admin.index'))
    