import os
import time

from flask import Flask, jsonify, render_template
from flask_cors import *
from flask import request
import angle
import huahen
import circle
import lenth

huahen = huahen.Huahen()
angle = angle.Angle()
circle=circle.Circle()
lenth=lenth.Lenth()

def create_app(test_config=None):
    # create and configure the app

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    from . import db
    db.init_app(app)

    def query_db(query, args=(), one=False):
        cur = db.get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # 将字典数据导入数据库中：file需要存入数据库的字典，table是需要存入数据库的表格，数据库默认存入
    def dict2sqlite(file,table):
        connection=db.get_db()
        # 建立数据库及数据表person
        # conn = sqlite3.connect('data.db')
        c = connection.cursor()
        c.execute('create table if not exists {table} (id INTEGER PRIMARY KEY ASC)'.format(table = table))
 
 
        # 查询如果表中没有JSON文件里面含有的字段，则增加数据库中的相应列
        keys = ""
        values = ""
        for i in file:
            keys = keys + "," + str(i)
            values = values +'","' + str(file[i])
            # try:
            #     c.execute('ALTER TABLE {table} ADD COLUMN {i} TEXT'.format(table=table, i=i))
            # except:
            #     pass
        keys =keys[1:]
        values = values[2:] + '"'
        sql = 'insert into {table} ({keys}) values ({values})'.format(table=table,keys=keys,values=values)
        # print(sql)
        # try:
        c.execute(sql)
        # print(c)
        # except:
            # print("信息未插入")
            # pass
        id=c.lastrowid

        # 提交数据库更改
        connection.commit()
        # 关闭数据库连接
        connection.close()
        return id

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"

    @app.route('/huahen', methods=["POST", "GET"])
    def detect_huahen():
        print(request.json)
        path = request.json.get('image_path')
        info = huahen.single_detect(image_path=path)
        info['address']=path
        info['youwu'] = -1
        info['angle'] = -1
        info['circle'] = -1
        info['lenth'] = -1
        info['hege'] = -1
        info['created']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        # connection=db.get_db()
        # query="INSERT INTO gongjian (huahen,youwu,angle,circle,lenth,address,create,hege) values{}"
        id=dict2sqlite(info,"gongjian")
        info['id'] = id
        # print(info,type(info))
        return jsonify(info)

    @app.route('/angle', methods=["POST", "GET"])
    def detect_angle():
        path = request.json.get('image_path')
        info = angle.single_detect(image_path=path)
        info['address'] = path
        info['youwu'] = -1
        info['huahen'] = -1
        info['circle'] = -1
        info['lenth'] = -1
        info['hege'] = -1
        info['created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        id=dict2sqlite(info,"gongjian")
        info['id'] = id
        return jsonify(info)

    @app.route('/circle', methods=["POST", "GET"])
    def detect_circle():
        path = request.json.get('image_path')
        info = circle.single_detect(image_path=path)
        info['address'] = path
        info['youwu'] = -1
        info['angle'] = -1
        info['huahen'] = -1
        info['lenth'] = -1
        info['hege'] = -1
        info['created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        id=dict2sqlite(info,"gongjian")
        info['id'] = id
        return jsonify(info)

    @app.route('/lenth', methods=["POST", "GET"])
    def detect_lenth():
        path = request.json.get('image_path')
        info = lenth.single_detect(image_path=path)
        info['address'] = path
        info['youwu'] = -1
        info['angle'] = -1
        info['circle'] = -1
        info['huahen'] = -1
        info['hege'] = -1
        info['created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        id=dict2sqlite(info,"gongjian")
        info['id'] = id
        return jsonify(info)
    
    # @app.route('/getinfo', methods=["POST", "GET"])
    # def getinfo():
    #     path=request.json.get('image_path')
    #     query="SELECT * FROM gongjian WHERE address='{}'".format(path)
    #     print(query)
    #     result=query_db(query)
    #     print(result)
    #     return '1'
    
    @app.route('/getAll', methods=["POST", "GET"])
    def getAll():
        connection=db.get_db()
        cursor=connection.cursor()
        query="SELECT * FROM gongjian"
        cursor.execute(query)
        # print(query)
        # query_db(query)
        # 获取查询结果并转化为字典
        columns = [column[0] for column in cursor.description]
        result = []
        for row in cursor.fetchall():
            result.append(dict(zip(columns, row)))
        # 打印结果
        # for row in result:
        #     print(row)
        return result

    return app