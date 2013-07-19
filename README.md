# Conan #

## 功能 ##

1. 列表展示柯南 TV 和 OVA 的番号、中文标题、英文标题和个人评分（星级）。

2. 提供添加、编辑、删除等功能。

## 运行环境 ##

* ### Python ###

    版本：2.7.5
    
    下载地址：[【传送门】][1]
    

* ### Flask ###

    版本：0.9
    
    安装方法：
    
    * 下载地址：[【传送门】][2]
    
    * 使用 easy_install 安装

* ### MongoDB ###

    版本：2.4

    下载地址：[【传送门】][3]

    配置方法：

    * Windows 平台

        1. 将 data 文件夹复制到 MongoDB 目录下

        2. 新建批处理文件，输入以下代码并保存

                start mongod.exe --dbpath data --auth
        
        3. 运行批处理文件，启动数据库

    * Linux 平台

    暂未测试

[1]: http://www.python.org/ "Python"
[2]: http://flask.pocoo.org/ "Flask"
[3]: http://www.mongodb.org/ "MongoDB"
