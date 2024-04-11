from flask import Flask, request, jsonify, session, redirect
import os

app = Flask(__name__)

#批处理
@app.route('/BatchProcessing', methods=["POST"])
def Process_Pic():
    # 用POST方式获取JSON数据
    get_data = request.get_json()
    # 获取文件夹地址
    folder_path=get_data.get("folder_path")

    # 初始化一个列表存储图片文件名
    image_path=[]

    # 检查文件夹路径是否存在
    if folder_path and os.path.isdir(folder_path):
        # 遍历文件夹中的文件
        for filename in os.listdir(folder_path):
            # 简单通过文件扩展名判断是否是图片文件
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_path.append(filename)

                # 或者添加的是文件的绝对地址
                # file_path = os.path.join(folder_path, filename)
                # image_path.append(file_path)

    else:
        return jsonify({"msg": "地址不正确"})


    #逐个遍历image_path中的图片路径，并作出对应的操作
    for path in image_path:
        # 根据要检测的功能，逐个对图片的路径path进行操作
        pass


if __name__ == '__main__':
    app.run()
