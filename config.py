# -*- coding:utf-8 -*-
import os

if 'SERVER_SOFTWARE' in os.environ:
    # 生产服务器配置
    from bae.core import const
    # 数据库配置
    DB_HOST = 'localhost'
    DB_DATABASE = 'book_manager'
    DB_USERNAME = 'admin'
    DB_PASSWORD = 'admin'
    DB_PORT = 27017
else:
    # 测试服务器配置
    # 数据库配置
    DB_HOST = 'localhost'
    DB_DATABASE = 'book_manager'
    DB_USERNAME = 'admin'
    DB_PASSWORD = 'admin'
    DB_PORT = 27017