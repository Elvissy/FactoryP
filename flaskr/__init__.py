'''
    -1表示：没有数据
    huahen=1表示：有划痕
    huahen=0表示：没有划痕
    hege=1表示：工件合格
    hege=0表示：工件不合格
'''


import os
import sqlite3
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

    CORS(app, supports_credentials=True)

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
    def dict2sqlite(file,table,closed):
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
        if closed:
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
            cur.execute("SELECT COUNT(*) FROM users WHERE username=?", (username, ))
            result = cur.fetchone()  # 查询结果的元组
            count = result[0]  # 获取元组值
            if count<=0: # 不存在该用户
                return jsonify(msg="该用户不存在，请先注册")
            else: # 存在该用户

                # 查询用户登录是否正确
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

    @app.route('/getsession',methods=["POST"])
    def getsession():
        # 检查'status'是否在session中
        if 'status' in session:
            # 如果存在，返回status的值
            username=session.get('username')
            status=session.get('status')
            # 或者使用session['username']方法获取值
            # print("get_status:" + str(session['username']))

            return jsonify(username=username,status=status)
        else:
            # 如果不存在，返回错误信息
            return jsonify(username=None,status=None)

    # @app.route('/getAllUsers', methods=["POST"])
    # def getAllUsers():
    #     with db.get_db() as conn:
    #         cur = conn.cursor()
    #
    #         # 查询是否存在该用户
    #         cur.execute("SELECT id,username,phone,status FROM users")
    #         users = cur.fetchall()  # 查询结果的元组
    #         print(users)
    #         # 创建JSON结构
    #         json_data = [{
    #             "id": user[0],
    #             "username": user[1],
    #             "phone": user[2],
    #             "status": user[3]
    #         } for user in users]
    #         return jsonify({'users': json_data})
    @app.route('/getAllUsers', methods=["POST"])
    def getAllUsers():

        get_data = request.get_json()

        param = {}
        param['username'] = get_data.get("username")
        param['status'] = get_data.get("status")
        param['number'] = get_data.get("number")

        if param['username'] == '':
            if param['number'] == '':
                if param['status'] == '':
                    query = "SELECT id,username,phone,status FROM users"
                elif param['status'] == '0':
                    query = "SELECT id,username,phone,status FROM users where status=0"
                elif param['status'] == '1':
                    query = "SELECT id,username,phone,status FROM users where status=1"
                elif param['status'] == '2':
                    query = "SELECT id,username,phone,status FROM users where status=2"
            else:
                if param['status'] == '':
                    query = "SELECT id,username,phone,status FROM users where phone='{0}'".format(param['number'])
                elif param['status'] == '0':
                    query = "SELECT id,username,phone,status FROM users where status=0 and phone='{0}'".format(
                        param['number'])
                elif param['status'] == '1':
                    query = "SELECT id,username,phone,status FROM users where status=1 and phone='{0}'".format(
                        param['number'])
                elif param['status'] == '2':
                    query = "SELECT id,username,phone,status FROM users where status=2 and phone='{0}'".format(
                        param['number'])
        else:
            if param['number'] == '':
                if param['status'] == '':
                    query = "SELECT id,username,phone,status FROM users where username='{0}'".format(
                        param['username'])
                elif param['status'] == '0':
                    query = "SELECT id,username,phone,status FROM users where status=0 and username='{0}'".format(
                        param['username'])
                elif param['status'] == '1':
                    query = "SELECT id,username,phone,status FROM users where status=1 and username='{0}'".format(
                        param['username'])
                elif param['status'] == '2':
                    query = "SELECT id,username,phone,status FROM users where status=2 and username='{0}'".format(
                        param['username'])
            else:
                if param['status'] == '':
                    query = "SELECT id,username,phone,status FROM users where phone='{0}' and username='{1}'".format(
                        param['number'], param['username'])
                elif param['status'] == '0':
                    query = "SELECT id,username,phone,status FROM users where status=0 and phone='{0}' and username='{1}'".format(
                        param['number'], param['username'])
                elif param['status'] == '1':
                    query = "SELECT id,username,phone,status FROM users where status=1 and phone='{0}' and username='{1}'".format(
                        param['number'], param['username'])
                elif param['status'] == '2':
                    query = "SELECT id,username,phone,status FROM users where status=2 and phone='{0}' and username='{1}'".format(
                        param['number'], param['username'])

        print(query)

        with db.get_db() as conn:
            cur = conn.cursor()

            # 查询是否存在该用户
            cur.execute(query)
            users = cur.fetchall()  # 查询结果的元组
            # print(users)
            # 创建JSON结构
            json_data = [{
                "id": user[0],
                "username": user[1],
                "phone": user[2],
                "status": user[3]
            } for user in users]
            return jsonify({'users': json_data})

    # getUserMsg改为getUserByName
    @app.route('/getUserByName', methods=["POST"])
    def getUserMsg():
        # 用POST方式获取JSON数据
        get_data = request.get_json()
        # 获取数据
        username = get_data.get("username")

        # 链接数据库查询
        conn = db.get_db()
        with db.get_db() as conn:
            cur = conn.cursor()

            # 查询是否存在该用户
            cur.execute("SELECT * FROM users WHERE username=?", (username,))
            user_records = cur.fetchall()  # 查询结果的元组
            # count = result[0]  # 获取元组值
            # print(user_records)

            if user_records:
                user = user_records[0]
                id = user[0]
                username = user[1]
                phone = user[3]
                status = user[4]
                return jsonify(id=id, username=username, phone=phone, status=status)
            else:
                return jsonify({'msg': '不存在该用户'})


    @app.route('/setUserMsg',methods=["POST"])
    def setUserMsg():
        # 用POST方式获取JSON数据
        get_data = request.get_json()
        #获取数据
        id = get_data.get("id")
        username = get_data.get("username")
        phone = get_data.get("phone")
        status = get_data.get("status")

        with db.get_db() as conn:
            cur = conn.cursor()
            # 更新数据库
            cur.execute("UPDATE users SET username = ?, phone = ?, status = ? WHERE id = ?", (username, phone, status, id))
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({'msg': '不存在该用户'})
            else:
                return jsonify({'msg': '修改成功'})


    
    @app.route('/huahen', methods=["POST", "GET"])
    def detect_huahen():
        print(request.json)
        path = request.json.get('image_path')
        result = huahen.single_detect(image_path=path)
        info={}
        info['huahen']=result
        info['address']=path
        info['youwu'] = -1
        info['angle'] = -1
        info['circle'] = -1
        info['lenth'] = -1
        info['hege'] = -1
        info['created']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        # connection=db.get_db()
        # query="INSERT INTO gongjian (huahen,youwu,angle,circle,lenth,address,create,hege) values{}"
        id=dict2sqlite(info,"gongjian",True)
        info['id'] = id
        # print(info,type(info))
        return jsonify(info)

    @app.route('/angle', methods=["POST", "GET"])
    def detect_angle():
        path = request.json.get('image_path')
        result = angle.single_detect(image_path=path)
        info={}
        info['angle']=result
        info['address'] = path
        info['youwu'] = -1
        info['huahen'] = -1
        info['circle'] = -1
        info['lenth'] = -1
        info['hege'] = -1
        info['created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        id=dict2sqlite(info,"gongjian",True)
        info['id'] = id
        return jsonify(info)

    @app.route('/circle', methods=["POST", "GET"])
    def detect_circle():
        path = request.json.get('image_path')
        res = circle.single_detect(image_path=path)
        info={}
        info['circle']=res
        info['address'] = path
        info['youwu'] = -1
        info['angle'] = -1
        info['huahen'] = -1
        info['lenth'] = -1
        info['hege'] = -1
        info['created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        id=dict2sqlite(info,"gongjian",True)
        info['id'] = id
        return jsonify(info)

    @app.route('/lenth', methods=["POST", "GET"])
    def detect_lenth():
        path = request.json.get('image_path')
        res = lenth.single_detect(image_path=path)
        info={}
        info['lenth']=res
        info['address'] = path
        info['youwu'] = -1
        info['angle'] = -1
        info['circle'] = -1
        info['huahen'] = -1
        info['hege'] = -1
        info['created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        id=dict2sqlite(info,"gongjian",True)
        info['id'] = id
        return jsonify(info)
    
    #逐个遍历image_path中的图片路径，并作出对应的操作
    def iteratePic(image_path):
        i=1
        for path in image_path:
            # 根据要检测的功能，逐个对图片的路径path进行操作
            if i==1:
                reshuahen=huahen.single_detect(image_path=path)
            elif i==2:
                resangle=angle.single_detect(image_path=path)
            elif i==3:
                rescircle=circle.single_detect(image_path=path)
            elif i==4:
                reslenth=lenth.single_detect(image_path=path)
            i+=1
        info={}
        info['huahen']=reshuahen
        info['youwu'] = reshuahen
        info['angle'] = resangle
        info['circle'] = rescircle
        info['lenth'] = reslenth
        info['hege'] = -1
        if not(reshuahen==0 and (45 in resangle) and rescircle==4 and reslenth==100):
            info['hege'] = -1
        else:
            info['hege'] = 1
        info['created']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        return info
    
    #批处理
    # @app.route('/BatchProcessingPic', methods=["POST"])
    # def Process_Pic():
    #     # 用POST方式获取JSON数据
    #     get_data = request.get_json()
    #     #判断标准参数是否改动，若改动则添加到数据库中
    #     param={}
    #     param['length']=get_data.get("length")
    #     param['lengthError']=get_data.get("lengthError")
    #     param['circles']=get_data.get("circles")
    #     param['angleParam']=get_data.get("angleParam")
    #     param['angleError']=get_data.get("angleError")
    #     isChanged=get_data.get("isChanged")
    #     if isChanged:
    #         id_param=dict2sqlite(param,"StandardParameters",False)
    #     else:
    #         connection=db.get_db()
    #         cur = connection.cursor()
    #         cur.execute("SELECT standardid FROM StandardParameters WHERE length=? AND lengthError=? AND circles=? AND angleParam=? AND angleError=?", (param['length'], param['lengthError'],param['circles'],param['angleParam'],param['angleError']))
    #         id_param = cur.fetchone()[0]
    #     # 获取文件夹地址
    #     folder_path=get_data.get("folder_path")
    #
    #     # 初始化一个列表存储图片文件名
    #     image_path=[]
    #
    #     # 检测结果
    #     info={}
    #     info['huahen']=-1
    #     info['angle'] = -1
    #     info['circle'] = -1
    #     info['lenth'] = -1
    #     info['hege'] = 1
    #
    #     # 检查文件夹路径是否存在
    #     if folder_path and os.path.isdir(folder_path):
    #         # 遍历文件夹中的文件
    #         os.listdir(folder_path).sort(key=lambda x: int(x[0:-4]))
    #         for filename in os.listdir(folder_path):
    #             # 简单通过文件扩展名判断是否是图片文件
    #             if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
    #                 # image_path.append(filename)
    #
    #                 # 或者添加的是文件的绝对地址
    #                 file_path = os.path.join(folder_path, filename)
    #                 # image_path.append(file_path)
    #                 pername=int(filename.split('.')[0])
    #                 if pername==1 and get_data.get("scratchSwitch"):
    #                     info['huahen']=huahen.single_detect(image_path=file_path)
    #                     if info['huahen']==1:
    #                         info['hege']=0
    #                 elif pername==2 and get_data.get("angleSwitch"):
    #                     info['angle'] = angle.single_detect(image_path=file_path)
    #                     if info['angle']>param['angleParam']+param['angleError'] or info['angle']<param['angleParam']-param['angleError']:
    #                         info['hege']=0
    #                 elif pername==3 and get_data.get("circlesSwitch"):
    #                     info['circle']=circle.single_detect(image_path=file_path)
    #                     if info['circle']!=param['circles']:
    #                         info['hege']=0
    #                 elif pername==4 and get_data.get("lengthSwitch"):
    #                     info['lenth']=lenth.single_detect(image_path=file_path)
    #                     if info['lenth']>param['length']+param['lengthError'] or info['lenth']<param['length']-param['lengthError']:
    #                         info['hege']=0
    #
    #     else:
    #         return jsonify({"msg": "地址不正确"})
    #
    #     info['address']=folder_path
    #     info['standardid']=id_param
    #     info['created']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    #     id=dict2sqlite(info,"gongjian",True)
    #     info['id'] = id
    #     return jsonify(info)
    @app.route('/BatchProcessingPic', methods=["POST"])
    def Process_Pic():
        # 用POST方式获取JSON数据
        get_data = request.get_json()
        # 判断标准参数是否改动，若改动则添加到数据库中
        param = {}
        param['length'] = get_data.get("length")
        param['lengthError'] = get_data.get("lengthError")
        param['circles'] = get_data.get("circles")
        param['angleParam'] = get_data.get("angleParam")
        param['angleError'] = get_data.get("angleError")
        # isChanged=get_data.get("isChanged")
        connection = db.get_db()
        cur = connection.cursor()
        cur.execute(
            "SELECT standardid FROM StandardParameters WHERE length=? AND lengthError=? AND circles=? AND angleParam=? AND angleError=?",
            (param['length'], param['lengthError'], param['circles'], param['angleParam'], param['angleError']))
        param_data = cur.fetchone()
        if param_data == None:
            id_param = dict2sqlite(param, "StandardParameters", False)
        else:
            id_param = param_data[0]

        # 获取文件夹地址
        number = get_data.get("number") * 4 + 1

        # 检测结果
        info = {}
        info['huahen'] = -1
        info['angle'] = -1
        info['circle'] = -1
        info['lenth'] = -1
        info['hege'] = 1

        # 初始化一个列表存储图片文件名
        folders_path = []

        # 使用固定绝对地址
        base_path = os.path.join(os.getcwd(), 'data')
        # 检查文件夹路径是否存在
        if base_path and os.path.isdir(base_path):
            # 遍历父文件夹中的文件子文件夹
            for foldersname in os.listdir(base_path):
                folderpath = os.path.join(base_path, foldersname)
                folders_path.append(folderpath)
        else:
            return jsonify({"msg": "地址不正确"})

        # 检测角度
        if get_data.get("angleSwitch"):
            angles = []
            angle_path1 = base_path + "\\1\\" + f"{number}.bmp"
            angle_path2 = base_path + "\\7\\" + f"{number}.bmp"
            angle1 = angle.single_detect(image_path=angle_path1)
            angle2 = angle.single_detect(image_path=angle_path2)
            if angle1 > param['angleParam'] + param['angleError'] or angle1 < param['angleParam'] - \
                    param['angleError']:
                info['hege'] = 0
            if angle2 > param['angleParam'] + param['angleError'] or angle2 < param['angleParam'] - \
                    param['angleError']:
                info['hege'] = 0
            angles.append(angle1)
            angles.append(angle2)
            info['angle'] = angles

        # 检测宽度
        if get_data.get("lengthSwitch"):
            length_path = base_path + "\\1\\" + f"{number}.bmp"
            info['lenth'] = lenth.single_detect(image_path=length_path)
            if (info['lenth']) > (param['length'] + param['lengthError']) or (info['lenth']) < (
                    param['length'] - param['lengthError']):
                info['hege'] = 0

        # 检测划痕，圆孔
        if get_data.get("scratchSwitch") or get_data.get("circlesSwitch"):
            scratch = 0
            circles = 0
            for forder in folders_path:
                for i in range(4):
                    pic_path = forder + f"\\{number + i}.bmp"
                    # print(pic_path)
                    # print("--------------------------------------------"+str(circle.single_detect(image_path=pic_path)))
                    c = circle.single_detect(image_path=pic_path)
                    s = huahen.single_detect(image_path=pic_path, degree=get_data.get("degree"))
                    circles += c
                    scratch += s


            if scratch > 0:
                info['huahen'] = 1
            info['circle'] = circles

            if get_data.get("scratchSwitch") and scratch > 0:
                info['hege'] = 0
            if get_data.get("circlesSwitch") and circles != param['circles']:
                info['hege'] = 0

        info['address'] = base_path
        info['standardid'] = id_param
        info['created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        id = dict2sqlite(info, "gongjian", True)
        info['id'] = id
        return jsonify(info)


    #批处理(一次处理多个工件)
    @app.route('/BatchProcessing', methods=["POST"])
    def Process_Folder():
        # 用POST方式获取JSON数据
        get_data = request.get_json()

        #判断标准参数是否改动，若改动则添加到数据库中
        param={}
        param['length']=get_data.get("length")
        param['lengthError']=get_data.get("lengthError")
        param['circles']=get_data.get("circles")
        param['angleParam']=get_data.get("angleParam")
        param['angleError']=get_data.get("angleError")
        # isChanged=get_data.get("isChanged")
        # if isChanged:
        #     id_param=dict2sqlite(param,"StandardParameters",False)
        # else:
        #     connection=db.get_db()
        #     cur = connection.cursor()
        #     cur.execute("SELECT standardid FROM StandardParameters WHERE length=? AND lengthError=? AND circles=? AND angleParam=? AND angleError=?", (param['length'], param['lengthError'],param['circles'],param['angleParam'],param['angleError']))
        #     id_param = cur.fetchone()[0]

        connection=db.get_db()
        cur = connection.cursor()
        cur.execute("SELECT standardid FROM StandardParameters WHERE length=? AND lengthError=? AND circles=? AND angleParam=? AND angleError=?", (param['length'], param['lengthError'],param['circles'],param['angleParam'],param['angleError']))
        param_data=cur.fetchone()
        if param_data==None:
            id_param=dict2sqlite(param,"StandardParameters",False)
        else:
            id_param = param_data[0]

        # 获取文件夹地址
        folder_path=get_data.get("folder_path")

        # 初始化一个列表存储图片文件名
        image_path=[]

        # 初始化一个列表存储子文件夹名
        folders_path=[]

        # 初始化一个列表存储检测结果
        res=[]

        # 检查文件夹路径是否存在
        if folder_path and os.path.isdir(folder_path):
            # 遍历父文件夹中的文件子文件夹
            for foldersname in os.listdir(folder_path):
                folderpath=os.path.join(folder_path, foldersname)
                folders_path.append(folderpath)

            times=1 # 记录此时是第几个工件，当遍历到最后一个工件时，将数据库连接关闭
            close=False
            path_lenth=len(folders_path)

            for path in folders_path:
                # 遍历子文件夹中的文件
                print(path)
                info={}
                info['huahen']=-1
                info['angle'] = -1
                info['circle'] = -1
                info['lenth'] = -1
                info['hege'] = 1
                for filename in os.listdir(path):
                    # 简单通过文件扩展名判断是否是图片文件
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        # image_path.append(filename)

                        # 或者添加的是文件的绝对地址
                        file_path = os.path.join(path, filename)
                        # image_path.append(file_path)
                        pername=int(filename.split('.')[0])
                        if pername==1 and get_data.get("scratchSwitch"):
                            info['huahen']=huahen.single_detect(image_path=file_path)
                            if info['huahen']==1:
                                info['hege']=0
                        elif pername==2 and get_data.get("angleSwitch"):
                            info['angle']=angle.single_detect(image_path=file_path)
                            if (info['angle'][0]) > (param['angleParam']+param['angleError']) or (info['angle'][0]) < (param['angleParam']-param['angleError']):
                                info['hege']=0
                        elif pername==3 and get_data.get("circlesSwitch"):
                            info['circle']=circle.single_detect(image_path=file_path)
                            if info['circle']!=param['circles']:
                                info['hege']=0
                        elif pername==4 and get_data.get("lengthSwitch"):
                            info['lenth']=lenth.single_detect(image_path=file_path)
                            if (info['lenth']) > (param['length']+param['lengthError']) or (info['lenth']) < (param['length']-param['lengthError']):
                                info['hege']=0
                info['address']=path
                if times==path_lenth:
                    close=True
                info['standardid']=id_param
                info['created']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                id=dict2sqlite(info,"gongjian",close)
                info['id'] = id
                times+=1
                res.append(info)

        else:
            return jsonify({"msg": "地址不正确"})
        
        return jsonify(res)
    
    
    # @app.route('/getinfo', methods=["POST", "GET"])
    # def getinfo():
    #     path=request.json.get('image_path')
    #     query="SELECT * FROM gongjian WHERE address='{}'".format(path)
    #     print(query)
    #     result=query_db(query)
    #     print(result)
    #     return '1'
    
    # @app.route('/getAll', methods=["POST", "GET"])
    # def getAll():
    #     connection=db.get_db()
    #     cursor=connection.cursor()
    #     query="SELECT * FROM gongjian"
    #     cursor.execute(query)
    #     # print(query)
    #     # query_db(query)
    #     # 获取查询结果并转化为字典
    #     print("-------",cursor.description)
    #     columns = [column[0] for column in cursor.description]
    #     print(columns)
    #     result = []
    #     for row in cursor.fetchall():
    #         detectRes=dict(zip(columns, row))
    #         paramId=detectRes['standardid']
    #         # query="SELECT * FROM StandardParameters WHERE standardid=?", (paramId, )
    #         cursor.execute("SELECT * FROM StandardParameters WHERE standardid=?", (paramId, ))
    #         columnsParam = [column[0] for column in cursor.description]
    #         param=cursor.fetchone()
    #         paramRes=dict(zip(columnsParam, param))
    #         res=dict(detectRes,**paramRes)
    #         result.append(res)
    #     # 打印结果
    #     # for row in result:
    #     #     print(row)
    #     # print(type(result))
    #     return result
    @app.route('/getAll', methods=["POST", "GET"])
    def getAll():
        get_data = request.get_json()

        param = {}
        param['id'] = get_data.get("id")
        param['file'] = get_data.get("file")
        param['status'] = get_data.get("status")
        param['date'] = get_data.get("date")
        if param['id'] == '':
            if param['file'] == '':
                if param['status'] == '':
                    if param['date'] == ';':
                        query = "SELECT * FROM gongjian"
                    else:
                        param['start'] = param['date'].split(';')[0]
                        param['end'] = param['date'].split(';')[1]
                        query = "SELECT * FROM gongjian  WHERE created BETWEEN '{0}' and '{1}' ORDER BY id_g DESC".format(
                            param['start'], param['end'])
                else:
                    if param['date'] == '':
                        query = "SELECT * FROM gongjian where hege='{0}'".format(param['status'])
                    else:
                        param['start'] = param['date'].split(';')[0]
                        param['end'] = param['date'].split(';')[1]
                        query = "SELECT * FROM gongjian  WHERE hege='{0}' and created BETWEEN '{1}' and '{2}' ORDER BY id_g DESC".format(
                            param['status'], param['start'], param['end'])
            else:
                if param['status'] == '':
                    if param['date'] == '':
                        query = "SELECT * FROM gongjian where address='{0}'".format(param['file'])
                    else:
                        param['start'] = param['date'].split(';')[0]
                        param['end'] = param['date'].split(';')[1]
                        query = "SELECT * FROM gongjian  WHERE address='{0}' and created BETWEEN '{1}' and '{2}' ORDER BY id_g DESC".format(
                            param['file'], param['start'], param['end'])
                else:
                    if param['date'] == '':
                        query = "SELECT * FROM gongjian where address='{0}' and hege='{1}'".format(param['file'],
                                                                                                   param['status'])
                    else:
                        param['start'] = param['date'].split(';')[0]
                        param['end'] = param['date'].split(';')[1]
                        query = "SELECT * FROM gongjian  WHERE address='{0}' and hege='{1}' and created BETWEEN '{2}' and '{3}' ORDER BY id_g DESC".format(
                            param['file'], param['status'], param['start'], param['end'])
        else:
            print(1)
            query = "SELECT * FROM gongjian where id_g='{0}'".format(param['id'])
        print(query)
        connection = db.get_db()
        cursor = connection.cursor()
        # if param['all'] == 1 and param['qualify']==0 and param['time']==0:
        #     query="SELECT * FROM gongjian"
        # elif param['qualify'] == 1 and param['all']==0 and param['time']==0:
        #     query="SELECT * FROM gongjian where hege=1"
        # elif param['qualify'] == 2 and param['all']==0 and param['time']==0:
        #     query="SELECT * FROM gongjian where hege=0"
        # elif param['time'] ==1 and param['all']==0 and param['qualify']==0:
        #     query="SELECT * FROM gongjian WHERE cratedate BETWEEN ? and ? ORDER BY id DESC",(param['start'],param['end'])

        cursor.execute(query)
        # query_db(query)
        # 获取查询结果并转化为字典
        # print("-------",cursor.description)
        columns = [column[0] for column in cursor.description]
        print(columns)
        result = []
        for row in cursor.fetchall():
            detectRes = dict(zip(columns, row))
            paramId = detectRes['standardid']
            # query="SELECT * FROM StandardParameters WHERE standardid=?", (paramId, )
            cursor.execute("SELECT * FROM StandardParameters WHERE standardid=?", (paramId,))
            columnsParam = [column[0] for column in cursor.description]
            param = cursor.fetchone()
            paramRes = dict(zip(columnsParam, param))
            res = dict(detectRes, **paramRes)
            result.append(res)
        # 打印结果
        # for row in result:
        #     print(row)
        # print(type(result))
        return result

    return app