# -*- coding: utf-8 -*-
from flask import Flask, g, flash, redirect, url_for, session
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

import os, hashlib, StringIO
from bson.objectid import ObjectId

from anime import anime
from anime.views import *

from models import User
from database import connect_db
from captcha import create_captcha


# 应用程序工厂函数
def create_app(config):
    app = Flask(__name__)
    configure_app(app, config)
    configure_views(app)
    configure_blueprints(app)
    config_before_request(app)
    configure_flasklogin(app)
    
    app.debug = True
    app.secret_key = 'I love you.'
    return app

# 配置应用程序
def configure_app(app, config):
    app.config.from_object(config)

# 配置视图
def configure_views(app):
    @app.route('/')
    def index():
        return redirect(url_for('anime.show_all'))

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
                encrypted_password = hashlib.new('md5', request.form['password']).hexdigest()
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
                cur = db.user.find_one({'username': request.form['username']})
                if not cur:
                    # 将用户写入数据库
                    db.user.insert({
                        'username': request.form['username'],
                        'password': hashlib.new('md5', request.form['password']).hexdigest(),
                        'email': request.form['email']
                    })
                    flash(u'注册成功，3 秒钟内将转到登陆页面……')
                    return render_template('flash.html', target=url_for('login'))
                else:
                    error = u'用户名已存在'
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
        
def configure_blueprints(app):
    from anime import anime
    app.register_blueprint(anime, url_prefix='/anime')

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

