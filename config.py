# -*- coding:utf-8 -*-
import os

if 'SERVER_SOFTWARE' in os.environ:
    # 生产服务器配置
    from bae.core import const
    # 数据库配置
    DB_HOST = const.MONGO_HOST
    DB_DATABASE = 'iioiQWverQQwevpzNbeX'
    DB_USERNAME = const.MONGO_USER
    DB_PASSWORD = const.MONGO_PASS
    DB_PORT = int(const.MONGO_PORT)
else:
    # 测试服务器配置
    # 数据库配置
    DB_HOST = 'localhost'
    DB_DATABASE = 'conan'
    DB_USERNAME = 'whypro'
    DB_PASSWORD = 'whypro'
    DB_PORT = 27017