# -*- coding: utf-8 -*-
# 将依赖模块文件夹加入系统路径
import sys
import os
from conan import create_app

deps_path = os.path.join(os.path.split(os.path.realpath(__file__))[0],'dependency')
sys.path.insert(0, deps_path)

app = create_app('config')

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, app, use_reloader=True, use_debugger=True, use_evalex=True)
