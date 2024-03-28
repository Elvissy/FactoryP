import os
import time

from flask import Flask, jsonify, render_template, session
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

    # 使用session需要设置secret_key
    app.secret_key = b'U9iaIxNzmrE5rbxJ'

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
    
    @app.route('/login',methods=["POST"])
    def login():
        # GET方式直接获取数据
        # username=request.args.get("username")

        # 用POST方式获取JSON数据
        get_data = request.get_json()
        #获取数据
        username=get_data.get("username")
        password=get_data.get("password")

        if not username or not password:
            return jsonify(msg="输入信息不完整")

        # 链接数据库
        with db.get_db() as conn:
            cur = conn.cursor()

            # 查询是否存在该用户
            cur.execute("SELECT COUNT(*) FROM users WHERE username=? AND password=?", (username, password))
            result = cur.fetchone()  # 查询结果的元组
            count = result[0]  # 获取元组值

            if count > 0:#存在该用户

                # 查询该用户名的身份(权限)信息
                cur.execute("SELECT status FROM users WHERE username=?", (username,))
                status = cur.fetchone()[0]
                # 把用户信息写进session中
                session['username'] = username
                session['status'] = status

                return jsonify(msg="登陆成功")
                # return redirect(url_for('index')) #或者直接重定向到系统主页面
            else:
                return jsonify(msg="用户名称或密码错误")
            
    @app.route('/register',methods=["POST"])
    def register():
        # GET方式直接获取数据
        # username=request.args.get("username")

        # 用POST方式获取JSON数据
        get_data = request.get_json()
        #获取数据
        username=get_data.get("username")
        password=get_data.get("password")
        con_password=get_data.get("con_password")
        phone=get_data.get("phone")

        # 如果输入信息不全，返回提醒
        if not username or not password or not con_password or not phone:
            return jsonify(msg="输入信息不完整")
        elif password != con_password:  #密码和确认密码是否相同
            return jsonify(msg="请重新输入密码")

        # 链接数据库
        with db.get_db() as conn:
            cur = conn.cursor()

            # 查询用户是否已经存在
            cur.execute("SELECT COUNT(*) FROM users where username=?",(username,))
            result=cur.fetchone() #查询结果的元组
            count=result[0] #获取元组值

            if count > 0:
                return jsonify(msg="该用户已经存在")
            else:
                #写入数据库
                cur.execute("INSERT INTO users (username, password, phone) VALUES (?, ?, ?)",(username, password, phone))
                conn.commit()
                return jsonify(msg="增加用户成功")
                # return redirect(url_for('login')) #或者直接重定向到登录页面

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