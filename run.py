# -*- coding: utf-8 -*-
# 将依赖模块文件夹加入系统路径
import sys, os
deps_path = os.path.join(os.path.split(os.path.realpath(__file__))[0],'dependency')
sys.path.insert(0, deps_path)

from conan import create_app
app = create_app('config')

if 'SERVER_SOFTWARE' in os.environ:
    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)
elif __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, app,
               use_reloader=True, use_debugger=True, use_evalex=True)