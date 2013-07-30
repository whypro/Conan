# -*- encoding: utf-8 -*-
from pymongo import MongoClient
import json
from bson import json_util
import os, shutil
from flask import current_app
import datetime

def connect_db():
    client = MongoClient(current_app.config['DB_HOST'], current_app.config['DB_PORT'])
    db = client[current_app.config['DB_DATABASE']]
    db.authenticate(current_app.config['DB_USERNAME'], current_app.config['DB_PASSWORD'])
    return db
    
    
def connect_backup_db(db_name):
    client = MongoClient(current_app.config['DB_HOST'], current_app.config['DB_PORT'])
    db = client[db_name]
    db.authenticate(current_app.config['DB_USERNAME'], current_app.config['DB_PASSWORD'])
    return db
    
def drop_db(db_name):
    client = MongoClient(current_app.config['DB_HOST'], current_app.config['DB_PORT'])
    if db_name in client.database_names():
        client.drop_database(db_name)

def clear_db(db):
    collections = db.collection_names()
    collections.remove('system.indexes')
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
    collections.remove('system.indexes')
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
        
    for collection in collections:
        # back_filename = collection + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        temp_filename = os.path.join(temp_dir, collection)
        f = open(temp_filename, 'w+')
        results = db[collection].find()
        for result in results:
            str = json.dumps(result, ensure_ascii=False, default=json_util.default)
            f.write(str.encode('utf-8'))
            f.write('\n')
        f.close()

        # 存入 BAE Bucket
        if 'SERVER_SOFTWARE' in os.environ:
            dirname = '/backup'
            bucket_object = os.path.join(dirname, collection)
            baebcs = create_bcs()
            BUCKET_NAME = 'whypro'
            
            baebcs.put_file(BUCKET_NAME, bucket_object, temp_filename)
            # 如果不加下面这句，就无法在 bucket 中正常显示 backup 目录与文件，BAE bucket 的 BUG？
            # baebcs.put_object(BUCKET_NAME, os.path.join(dirname, 'dummy'), '0')
        # 存入本地 backup 目录
        else:
            dirname = 'backup'
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            filename = os.path.join(dirname, collection)
            shutil.copyfile(temp_filename, filename)
    return 0    # No error

# For BAE
if 'SERVER_SOFTWARE' in os.environ:
    from bae.core import const
    from bae.api import bcs 
    def create_bcs():
        BCS_ADDR = const.BCS_ADDR
        ACCESS_KEY = const.ACCESS_KEY
        SECRET_KEY = const.SECRET_KEY
        baebcs = bcs.BaeBCS(BCS_ADDR, ACCESS_KEY, SECRET_KEY)
        return baebcs
else:
    def create_bcs():
        BCS_ADDR = 'bcs.duapp.com'
        ACCESS_KEY = 'AF28c466e7dd74686195abc876d4849b'
        SECRET_KEY = '2b2f8ac70616dbea89fc2ac2312de1a9'
        import pybcs
        bcs = pybcs.BCS(BCS_ADDR, ACCESS_KEY, SECRET_KEY, pybcs.HttplibHTTPC)
        return bcs

def restore_db():
    '''
    将文件中的数据恢复到 MongoDB
    '''
    temp_dir = os.path.join(current_app.config['TEMP_DIR'], 'backup')
    
    db = connect_db()
    # db = connect_backup_db(db_name)
    # db = connect_backup_db('ai')
    
    # BAE 生产环境
    if 'SERVER_SOFTWARE' in os.environ:
        baebcs = create_bcs()
        BUCKET_NAME = 'whypro'
        (e, objects) = baebcs.list_objects(BUCKET_NAME, prefix='/backup')
        # 将 objects 保存到临时目录下
        objects.remove('/backup/dummy')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        for object in objects:
            temp_filename = os.path.join(temp_dir, object.split('/')[-1])
            baebcs.get_to_file(BUCKET_NAME, object, temp_filename)
        
    # 本地环境
    else:
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



# backup/ => $bucket/backup/
# local only
def local_to_bucket():
    if 'SERVER_SOFTWARE' in os.environ:
        return 1    # Error 1
    local_dirname = 'backup'
    if not os.path.exists(local_dirname):
        return 1    # Error 1
    files = os.listdir(local_dirname)
    bucket_dirname = '/backup'
    bcs = create_bcs()
    BUCKET_NAME = 'whypro'
    b = bcs.bucket(BUCKET_NAME)

    for file in files:
        # 存入 BAE Bucket
        bucket_object = bucket_dirname + '/' + file
        local_file = os.path.join(local_dirname, file)
        obj = b.object(bucket_object)
        obj.put_file(local_file)
        print bucket_object
        print local_file
    # 如果不加下面这句，就无法在 bucket 中正常显示 backup 目录与文件，BAE bucket 的 BUG？
    # obj = b.object(bucket_dirname + '/' + 'dummy')
    # obj.put('0')
    return 0    # No error 

# $bucket/backup/ => backup/
# local only
def bucket_to_local():
    if 'SERVER_SOFTWARE' in os.environ:
        return 1    # Error 1
    # 存入本地 backup 目录
    local_dirname = 'backup'
    bucket_dirname = '/backup'
    if not os.path.exists(local_dirname):
        os.makedirs(local_dirname)
    bcs = create_bcs()
    BUCKET_NAME = 'whypro'
    b = bcs.bucket(BUCKET_NAME)
    objects = b.list_objects(prefix=bucket_dirname)

    # objects.remove('/backup/dummy')
    for object in objects:
        obj_name = object.object_name
        local_file = os.path.join(local_dirname, obj_name.split('/')[-1])
        object.get_to_file(local_file)
    return 0    # No error

def clear_bucket():
    bcs = create_bcs()
    BUCKET_NAME = 'whypro'
    b = bcs.bucket(BUCKET_NAME)
    objects = b.list_objects()
    for obj in objects:
        obj.delete()
        # print obj.object_name


if __name__ == '__main__':
    # clear_bucket()
    pass
