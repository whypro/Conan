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
    
    
# import time
# import os
# from bae.core import const
# from bae.api import bcs

# HOST = const.BCS_ADDR
# AK = const.ACCESS_KEY
# SK = const.SECRET_KEY
# NAME = 'whypro'
# def test_bcs():
    # # 创建BCS管理对象
    # baebcs = bcs.BaeBCS(HOST, AK, SK)

    # # 读取一个测试文件的内容
    # filename = os.path.dirname(__file__) + "/favicon.ico"
    # with open(filename) as fd:
        # data = fd.read()

    # ### 将文件内容上传到 '/obj1' 下
    # o1 = '/upload/201303/obj1'
    # e, d = baebcs.put_object(bname, o1, data)
    # assert e == 0

    # ### 上传文件有一定的延迟
    # time.sleep(1)

    # ### 从 '/obj1' 获取数据
    # e, d = baebcs.get_object(bname, o1)
    # assert e == 0
    # assert d == data

    # ### 也可以直接上传文件
    # o2 = '/obj2'
    # e, d = baebcs.put_file(bname, o2, filename)

    # ### 将object内容保存到临时目录下
    # tmpdir = (const.APP_TMPDIR if const.APP_TMPDIR else "/tmp")
    # filename2 = tmpdir + "/favicon.ico"
    # e, d = baebcs.get_to_file(bname, o2, filename2)
    # assert e == 0

    # ### 列出所有的object
    # e, d = baebcs.list_objects(bname)
    # assert e == 0
    
    
    
    
    
    
    
    
    