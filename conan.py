# -*- coding: utf-8 -*-
from __future__ import division
from flask import Flask, g, flash, redirect, url_for, session
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

import os, hashlib, StringIO
from bson.objectid import ObjectId

from anime import anime
from anime.views import *
from admin import admin
from admin.views import *

from models import User
from database import connect_db
from captcha import create_captcha

from math import ceil
from urllib import urlencode

# 应用程序工厂函数
def create_app(config):
    app = Flask(__name__)
    configure_app(app, config)
    configure_views(app)
    configure_blueprints(app)
    config_before_request(app)
    configure_flasklogin(app)
    return app

# 配置应用程序
def configure_app(app, config):
    app.config.from_object(config)

# 配置视图
def configure_views(app):
    @app.route('/')
    def index():
        return redirect(url_for('anime.index'))

    # 登录页面
    @app.route('/login/', methods=['GET', 'POST'])
    def login():
        if g.user.is_authenticated():
            return redirect(url_for('index'))
        error = None
        if request.method == 'POST':
            if not request.form['username']:
                error = u'用户名不能为空'
            else:
                db = connect_db()
                encrypted_password = hashlib.md5(request.form['password']).hexdigest()
                cur = db.user.find_one({'username': request.form['username'], 'password': encrypted_password})
                if not cur:
                    error = u'用户名或密码不正确'
                else:
                    user = User(cur)
                    login_user(user, remember=('remember' in request.form))
                    flash(u'登陆成功，3 秒钟内将返回首页……')
                    return render_template('flash.html', target=url_for('index'))
        return render_template('login.html', error=error)
    
    # 注销
    @app.route('/logout/', methods=['GET'])
    @login_required
    def logout():
        logout_user()
        flash(u'已注销，3 秒钟内将返回首页……')
        return render_template('flash.html', target=url_for('index'))

    # 注册页面
    @app.route('/register/', methods=['GET', 'POST'])
    def register():
        # 已登录用户则返回首页
        if g.user.is_authenticated():
            return redirect(url_for('index'))
        error = None
        if request.method == 'POST':
            if not request.form['username']:
                error = u'用户名不能为空'
            elif not request.form['password']:
                error = u'密码不能为空'
            elif request.form['captcha'].upper() != session['captcha'].upper():
                error = u'验证码不正确'
            else:
                # 判断用户是否存在
                db = connect_db()
                username_conflict = db.user.find_one({'username': request.form['username']})
                email_conflict = db.user.find_one({'email': request.form['email']})
                
                if username_conflict:
                    error = u'用户名已存在'
                elif request.form['email'] and email_conflict:
                    error = u'邮箱已存在'
                else:
                    # 将用户写入数据库
                    if 'x-forwarded-for' in request.headers:
                        ip = request.headers['x-forwarded-for'].split(', ')[0]
                    else:
                        ip = request.remote_addr
                    db.user.insert({
                        'username': request.form['username'],
                        'password': hashlib.md5(request.form['password']).hexdigest(),
                        'email': request.form['email'], 
                        'date': datetime.datetime.now(),
                        'ip': ip,
                        'group': 'guest'
                    })
                    flash(u'注册成功，3 秒钟内将转到登陆页面……')
                    return render_template('flash.html', target=url_for('login'))
        return render_template('register.html', error=error)
       
    
    # 获取验证码
    @app.route('/captcha/')
    def get_captcha():
        #把strs发给前端,或者在后台使用session保存
        code_img, strs = create_captcha(size=(100, 24), img_type="PNG")
        buf = StringIO.StringIO()
        code_img.save(buf,'PNG')

        buf_str = buf.getvalue()
        session['captcha'] = strs
        response = app.make_response(buf_str)
        response.headers['Content-Type'] = 'image/png'
        return response
    
    
    # 查看留言页面
    @app.route('/guestbook/', defaults={'page': 1}, methods=['GET'])
    @app.route('/guestbook/page/<int:page>/', methods=['GET'])
    def show_message(page):
        messages = []
        total_pages = 0
        # 分页
        messages_per_page = 5
        offset = (page - 1) * messages_per_page
        
        db = connect_db()
        if not g.user.is_authenticated():
            # 若未登录，则显示 visible 为 public 的留言
            messages = db.message.find({'visible': 'public'}).sort([('date', -1)]).skip(offset).limit(messages_per_page)
        elif g.user.is_admin():
            # 若为超级用户，则显示所有留言
            messages = db.message.find().sort([('date', -1)]).skip(offset).limit(messages_per_page)
        else:
            # 若为普通用户，则显示 visible 为 public 的留言和自己的留言
            messages = db.message.find({'$or': [{'visible': 'public'}, {'name': g.user.get_username()}]}).sort([('date', -1)]).skip(offset).limit(messages_per_page)
            
        total_messages = messages.count(with_limit_and_skip=False)
        cur_messages = messages.count(with_limit_and_skip=True)
        
        total_pages = int(ceil(total_messages / messages_per_page)) # from __future__ import division
            
        if page != 1 and not cur_messages:
            abort(404)
                    
        return render_template('guestbook.html', messages=messages, cur_page=page, total_pages=total_pages)
        
    # 联系我们页面 
    @app.route('/contact/', methods=['GET', 'POST'])
    def leave_message():
        error = None
        if request.method == 'POST':
            if not request.form['name']:
                error = u'姓名不能为空'
            elif not request.form['content']:
                error = u'留言内容不能为空'
            elif request.form['captcha'].upper() != session['captcha'].upper():
                error = u'验证码不正确'
            else:
                id = g.user.get_id() if g.user.is_authenticated() else None

                db = connect_db()
                # ip = request.headers.get('x-forwarded-for', request.remote_addr)
                if 'x-forwarded-for' in request.headers:
                    ip = request.headers['x-forwarded-for'].split(', ')[0]
                else:
                    ip = request.remote_addr
                # dbref
                db.message.insert({'uid': id, 'name': request.form['name'], 'email': request.form['email'], 'content': request.form['content'], 'date': datetime.datetime.now(), 'ip': ip, 'visible': 'protected'})
                
                flash(u'留言成功，3 秒钟内将返回留言页面……')
                return render_template('flash.html', target=url_for('show_message'))
        return render_template('contact.html', error=error)
        
    @app.route('/guestbook/delete/<id>/', methods=['GET'])
    @login_required
    def delete_message(id):
        if not g.user.is_admin():
            flash(u'权限不足，3 秒钟内将返回留言页面……')
            return render_template('flash.html', target=url_for('show_message'))
        else:
            db = connect_db()
            db.message.remove({'_id': ObjectId(id)})
            # flash(u'删除成功，3 秒钟内将返回留言页面……')
            # return render_template('flash.html', target=url_for('show_message'))
            return redirect(url_for('show_message'))

    @app.route('/guestbook/hide/<id>/', methods=['GET'])
    @login_required
    def hide_message(id):
        if not g.user.is_admin():
            flash(u'权限不足，3 秒钟内将返回留言页面……')
            return render_template('flash.html', target=url_for('show_message'))
        else:
            db = connect_db()
            db.message.update({'_id': ObjectId(id)}, {'$set': {'visible': 'protected'}})
            return redirect(url_for('show_message'))
        
    @app.route('/guestbook/unhide/<id>/', methods=['GET'])
    @login_required
    def unhide_message(id):
        if not g.user.is_admin():
            flash(u'权限不足，3 秒钟内将返回留言页面……')
            return render_template('flash.html', target=url_for('show_message'))
        else:
            db = connect_db()
            db.message.update({'_id': ObjectId(id)}, {'$set': {'visible': 'public'}})
            return redirect(url_for('show_message'))
    
    # 个人信息页面
    @app.route('/profile/', methods=['GET', 'POST'])
    @login_required
    def show_profile():
        error = None
        # user = db.user.find_one({'_id': ObjectId(id)}, {'username': 1, 'email': 1, 'date': 1})
        user = g.user
        id = user.get_id()
        avatar_url = get_avatar(user.get_email(), 170)
        if request.method == 'POST':
            db = connect_db()
            # 邮箱重复验证
            email_conflict = db.user.find_one({'_id': {'$ne': ObjectId(id)}, 'email': request.form['email']})
            if request.form['email'] and email_conflict:
                error = u'邮箱已存在'
            else:
                # 密码字段不为空，更新密码和邮箱
                if request.form['password']:
                    db.user.update({'_id': ObjectId(id)}, {'$set': {'password': hashlib.md5(request.form['password']).hexdigest(), 'email': request.form['email']}})
                    flash(u'密码更改成功，请重新登录……')
                    return render_template('flash.html', target=url_for('logout'))
                # 密码字段为空，只更新邮箱
                else: 
                    db.user.update({'_id': ObjectId(id)}, {'$set': {'email': request.form['email']}})
                    flash(u'更改成功，3 秒钟内将转到个人页面……')
                    return render_template('flash.html', target=url_for('show_profile'))
                    
        return render_template('profile.html', error=error, avatar_url=avatar_url)

    @app.route('/about/', methods=['GET'])
    def show_about():
        return render_template('about.html')
        
        
    # 错误处理   
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route('/404/')
    def test_404():
        abort(404)

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @app.route('/500/')
    def test_500():
        abort(500)

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.route('/403/')
    def test_403():
        abort(403)
        
        
def configure_blueprints(app):
    from anime import anime
    app.register_blueprint(anime, url_prefix='/anime')
    from admin import admin
    app.register_blueprint(admin, url_prefix='/admin')

def configure_flasklogin(app):
    login_manager = LoginManager()
    login_manager.setup_app(app)

    @login_manager.user_loader
    def load_user(_id):
        db = connect_db()
        cur = db.user.find_one({'_id': ObjectId(_id)})
        user = User(cur)
        return user

    @login_manager.unauthorized_handler
    def unauthorized():
        flash(u'请先登录，3 秒钟内将转到登录页面……')
        return render_template('flash.html', target=url_for('login'))

def config_before_request(app):
    @app.before_request
    def before_request():
        g.user = current_user
            

# 获取头像
def get_avatar(email, size):
    default = 'http://www.gravatar.com/avatar/00000000000000000000000000000000/?size=170'
    gravatar_url = 'http://www.gravatar.com/avatar/' + hashlib.md5(email.lower()).hexdigest() + "?"
    gravatar_url += urlencode({'d': default, 's': str(size)})
    return gravatar_url


