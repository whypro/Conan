# -*- encoding: utf-8 -*-
from pymongo import MongoClient
import json
from bson import json_util
import os, shutil
from database import connect_db, connect_backup_db, drop_db
from flask import current_app

def backup_db():
    '''
    将 MongoDB 中的数据备份至文件
    '''
    db = connect_db()
    collections = db.collection_names()
    collections.remove('system.indexes')
    collections.remove('system.users')
    
    temp_dir = current_app.config['TEMP_DIR']
    # 创建目录
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    # 清空目录
    files = os.listdir(temp_dir)
    for file in files:
        temp_filename = os.path.join(temp_dir, file)
        os.remove(temp_filename)
        
    for collection in collections:
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
            baebcs.put_object(BUCKET_NAME, os.path.join(dirname, 'dummy'), '0')
        # 存入本地 backup 目录
        else:
            dirname = 'backup'
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            filename = os.path.join(dirname, collection)
            shutil.copyfile(temp_filename, filename)

# For BAE
if 'SERVER_SOFTWARE' in os.environ:
    from bae.core import const
    from bae.api import bcs
    def save_to_bucket(filename, data):
        baebcs = create_bcs()
        BUCKET_NAME = 'whypro'
        baebcs.put_object(BUCKET_NAME, filename, data)
        
    def create_bcs():
        BCS_ADDR = const.BCS_ADDR
        ACCESS_KEY = const.ACCESS_KEY
        SECRET_KEY = const.SECRET_KEY
        baebcs = bcs.BaeBCS(BCS_ADDR, ACCESS_KEY, SECRET_KEY)
        return baebcs
    
def restore_db(db_name):
    '''
    将文件中的数据恢复到 MongoDB
    '''
    temp_dir = current_app.config['TEMP_DIR']
    
    dirname = 'backup'
    # db = connect_backup_db(db_name)
    db = connect_backup_db('ai')
    # drop_db(db_name)
    # BAE 生产环境
    if 'SERVER_SOFTWARE' in os.environ:
        baebcs = create_bcs()
        BUCKET_NAME = 'whypro'
        (e, objects) = baebcs.list_objects(BUCKET_NAME, prefix='/backup')
        # 将 objects 保存到临时目录下
        for object in objects:
            temp_filename = os.path.join(temp_dir, object.split('/')[-1])
            baebcs.get_to_file(BUCKET_NAME, object, temp_filename)
        
        # TODO: 临时文件夹应该加前缀：temp/backup/
        
    # 本地环境
    else:
        # 将 backup 目录下的文件复制到临时目录下
        dirname = 'backup'
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        files = os.listdir(dirname)
        for file in files:
            filename = os.path.join(dirname, file)
            temp_file = os.path.join(temp_dir, file)
            shutil.copy(filename, temp_file)
        
    collections = os.listdir(temp_dir)
    for collection in collections:
        filename = os.path.join(temp_dir, collection)
        f = open(filename, 'r')
        for line in f:
            obj = json.loads(line, object_hook=json_util.object_hook)
            db[collection].insert(obj)
        f.close()
            
if __name__ == '__main__':
    backup()
    restore()
    
    
    
    
    
    