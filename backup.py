# -*- encoding: utf-8 -*-
from pymongo import MongoClient
import json
from bson import json_util
import os
from database import connect_db, connect_backup_db, drop_db


def backup_db():
    '''
    将 MongoDB 中的数据备份至文件
    '''
    dirname = 'backup'
    db = connect_db()
    collections = db.collection_names()
    collections.remove('system.indexes')
    collections.remove('system.users')
    
    # 创建目录
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    # 清空目录
    files = os.listdir(dirname)
    for file in files:
        filename = os.path.join(dirname, file)
        os.remove(filename)
        
    for collection in collections:
        filename = os.path.join(dirname, collection)
        f = open(filename, 'w')
        results = db[collection].find()
        for result in results:
            str = json.dumps(result, ensure_ascii=False, default=json_util.default)
            f.write(str.encode('utf-8'))
            f.write('\n')
        f.close()

def restore_db(db_name):
    '''
    将文件中的数据恢复到 MongoDB
    '''
    dirname = 'backup'
    db = connect_backup_db(db_name)
    drop_db(db_name)
    collections = os.listdir(dirname)
    for collection in collections:
        filename = os.path.join(dirname, collection)
        f = open(filename, 'r')
        for line in f:
            obj = json.loads(line, object_hook=json_util.object_hook)
            db[collection].insert(obj)

            
if __name__ == '__main__':
    backup()
    restore()