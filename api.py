import time

import  huahen
import  angle
import circle
import lenth
from flask import Flask, jsonify, render_template
from flask_cors import *
from flask import request

huahen=huahen.Huahen()
angle=angle.Angle()
circle=circle.Circle()
lenth=lenth.Lenth()

app = Flask(__name__)

from .flaskr import db
db.init_app(app)


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
    print("image_path:", path)
    info = huahen.single_detect(image_path=path)
    info['address'] = path
    info['yuwu'] = -1
    info['angle'] = -1
    info['circle'] = -1
    info['lenth'] = -1
    info['hege'] = -1
    info['create'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(info, type(info))
    return jsonify(info)

@app.route('/angle', methods=["POST", "GET"])
def detect_angle():
    print(request.json)
    path = request.json.get('image_path')
    print("image_path:", path)
    info = angle.single_detect(image_path=path)
    info['address'] = path
    info['yuwu'] = -1
    info['huahen'] = -1
    info['circle'] = -1
    info['lenth'] = -1
    info['hege'] = -1
    info['create'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    return jsonify(info)

@app.route('/circle', methods=["POST", "GET"])
def detect_circle():
    print(request.json)
    path = request.json.get('image_path')
    print("image_path:", path)
    info = circle.single_detect(image_path=path)
    return jsonify(info)

@app.route('/lenth', methods=["POST", "GET"])
def detect_lenth():
    print(request.json)
    path = request.json.get('image_path')
    print("image_path:", path)
    info = lenth.single_detect(image_path=path)
    return jsonify(info)

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

if __name__ == '__main__':
    CORS(app, supports_credentials=True)
    app.run(host='0.0.0.0', threaded=True)