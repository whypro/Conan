# -*- coding: utf-8 -*-
from pymongo import MongoClient
import json
from bson import json_util
import os, shutil
from flask import current_app


def connect_db():
    client = MongoClient(current_app.config['DB_HOST'], current_app.config['DB_PORT'])
    db = client[current_app.config['DB_DATABASE']]
    #db.authenticate(current_app.config['DB_USERNAME'], current_app.config['DB_PASSWORD'])
    return db
    
    
def connect_backup_db(db_name):
    client = MongoClient(current_app.config['DB_HOST'], current_app.config['DB_PORT'])
    db = client[db_name]
    #db.authenticate(current_app.config['DB_USERNAME'], current_app.config['DB_PASSWORD'])
    return db


def drop_db(db_name):
    client = MongoClient(current_app.config['DB_HOST'], current_app.config['DB_PORT'])
    if db_name in client.database_names():
        client.drop_database(db_name)


def clear_db(db):
    collections = db.collection_names()
    if 'system.indexes' in collections:
        collections.remove('system.indexes')
    if 'system.users' in collections:
        collections.remove('system.users')
    for collection in collections:
        db[collection].drop()


def backup_db():
    '''
    将 MongoDB 中的数据备份至文件
    '''
    db = connect_db()
    collections = db.collection_names()
    # 排除两个 system collections
    if 'system.indexes' in collections:
        collections.remove('system.indexes')
    if 'system.users' in collections:
        collections.remove('system.users')
    
    temp_dir = os.path.join(current_app.config['TEMP_DIR'], 'backup')
    # 创建目录
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    # 清空目录
    files = os.listdir(temp_dir)
    for file in files:
        temp_filename = os.path.join(temp_dir, file)
        os.remove(temp_filename)
    
    # 将 collections 存入临时目录
    for collection in collections:
        # back_filename = collection + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        temp_filename = os.path.join(temp_dir, collection)
        f = open(temp_filename, 'w+')

        # 防止 cursor 超时的一种替代方案
        batch_size = 30
        start = 0
        while True:
            results = db[collection].find().skip(start).limit(batch_size)
            if not results.count(with_limit_and_skip=True):
                break
            start += batch_size

            for result in results:
                str = json.dumps(result, ensure_ascii=False, default=json_util.default)
                f.write(str.encode('utf-8'))
                f.write('\n')
        f.close()

        # 存入本地 backup 目录
        dirname = 'backup'
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        filename = os.path.join(dirname, collection)
        shutil.copyfile(temp_filename, filename)
    return 0    # No error


def restore_db():
    '''
    将文件中的数据恢复到 MongoDB
    '''
    temp_dir = os.path.join(current_app.config['TEMP_DIR'], 'backup')
    
    db = connect_db()
    # db = connect_backup_db(db_name)
    # db = connect_backup_db('ai')

    # 本地环境
    # 将 backup 目录下的文件复制到临时目录下
    dirname = 'backup'
    # 如果不存在该目录
    if not os.path.exists(dirname):
        return 1    # 找不到备份文件
        # raise
    else:
        files = os.listdir(dirname)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    for file in files:
        filename = os.path.join(dirname, file)
        temp_file = os.path.join(temp_dir, file)
        shutil.copy(filename, temp_file)
        
    collections = os.listdir(temp_dir)
    # 清空数据库
    clear_db(db)
    for collection in collections:
        filename = os.path.join(temp_dir, collection)
        f = open(filename, 'r')
        for line in f:
            obj = json.loads(line, object_hook=json_util.object_hook)
            db[collection].insert(obj)
        f.close()
    return 0    # No error

if __name__ == '__main__':
    # clear_bucket()
    pass
