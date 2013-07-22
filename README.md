# Conan #

* ## 功能 ##

    1. 列表展示柯南 TV 和 OVA 的番号、中文标题、英文标题和个人评分（星级）。

    2. 提供添加、编辑、删除等功能。

* ## 运行环境 ##

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

    * ### virtualenv ###

    virtualenv 用来创建隔离的 python 环境，它可以处理 python 多版本和模块依赖的问题。详见[【这里】][4]

        * #### 安装 virtualenv ####

            1. 使用包管理器 pip 或者 easy_install 安装

            2. 下载 Source 包通过 setup.py 安装 [1]
        
            3. 下载 virtualenv.py 直接执行 [2]

        * #### 创建隔离环境 ####
    
                ### 建议添加选项--no-site-packages(令隔离环境不能访问系统全局的site-packages目录)
                ~$ virtualenv --no-site-packages ENV 
                ### 或者 
                ~$ python virtualenv.py --no-site-packages ENV
                ~$ source ENV/bin/activate
                (ENV)~$
    
        * #### 利用 virtualenv 处理依赖 ####
    
        命令行提示符前出现一个(ENV)前缀，说明已经处在了 python 隔离环境中。下面我们以一个示例来说明如何在这个虚拟环境中处理 python 环境中的第三方库依赖问题。  
    
        例如有一个 BAE python 应用名为 appA，它依赖一个第三方库 pyX。首先需要将 appA 的代码通过 SVN 取到本地，假设已经 checkout 到本地目录 /home/duapp/dir_appA，并在该目录下创建了一个存放依赖模块的目录 deps。
    
        接着在(ENV)虚拟环境中下载安装 pyX，由于 virtualenv 中已经包含了 pip 包管理器，我们直接使用 pip install 来处理。然后将已经安装好的 pyX 包拷贝到应用目录的 deps 下。
    
                (ENV)~$ pip install pyX
                (ENV)~$ cd ENV/lib/pythonX.X/site-packages
                (ENV)~$ cp -r pyX/ /home/duapp/dir_appA/deps/
    
        现在修改 index.py 文件，在 module 搜索路径 sys.path 中添加依赖模块目录，如下：
    
                import sys, os.path
                deps_path = os.path.join(os.path.split(os.path.realpath(__file__))[0],'deps')
                sys.path.insert(0, deps_path)
    
        此时，pyX 已经成功导入到 appA 中，应用中可以使用该第三方库的所有功能，依赖问题得到解决。


[1]: http://www.python.org/ "Python"
[2]: http://flask.pocoo.org/ "Flask"
[3]: http://www.mongodb.org/ "MongoDB"
[4]: http://www.virtualenv.org/en/latest/index.html "virtualenv"
