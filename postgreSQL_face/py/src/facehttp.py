# 这是一个_非常简单_的网络服务示例，可以识别上传图像中的人脸。
# 上传一个图片文件，它会检查图片中是否包含奥巴马的照片。
# 结果以json形式返回。例如：
#
# $ curl -XPOST -F "file=@obama2.jpg" http://127.0.0.1:5001
#
# 返回：
#
# {
# “face_found_in_image”：是的，
# "is_picture_of_obama": 真
# }
#
# 本示例基于 Flask 文件上传示例：http://flask.pocoo.org/docs/0.12/patterns/fileuploads/

# 注意：此示例需要安装烧瓶！您可以使用 pip 安装它：
# $ pip3 安装烧瓶
import io

from flask_cors import *
import ast
import json
from io import BytesIO
import base64
import numpy as np
import face_recognition
import psycopg2
from flask import Flask, jsonify, request, redirect
import logging
# 您可以将其更改为系统上的任何文件夹
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": "POST, GET", "expose_headers": "Content-Type"}})  # 允许所有域名跨域

dbdatabase = 
dbuser = 
dbpassword = 
dbhost = 
dbport = "5432"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 人脸注册
@app.route('/face/registration', methods=['GET', 'POST'])
def upload_image_registration():
    # 文件
    img = ""
    formData = ""
    try:
        trysss = request.files['file']
        print("try")
    except Exception:
        logging.warning('抛出')
        # 将结果作为json返回
        result = {
            "code": 500,
            "face_found_in_image": False,
            "is_picture_of_obama": False
        }
        return jsonify(result)
    else:
        # 检查是否上传了有效的图片文件
        if request.method == 'POST':
            if 'file' not in request.files:
                return redirect(request.url)

            file = request.files['file']
            if file.filename == '':
                return redirect(request.url)

            if file and allowed_file(file.filename):
                # 获取上传图像中任何人脸的人脸编码
                # 加载上载的图像文件
                img = face_recognition.load_image_file(file)
                formData = request.form.to_dict()

    encodings = face_recognition.face_encodings(img)
    conn = psycopg2.connect(database=dbdatabase, user=dbuser, password=dbpassword, host=dbhost,
                            port=dbport)
    db = conn.cursor()

    if len(encodings) > 0:
        isnot = detect_faces_in_image(encodings)
        if isnot[1]:
            result = {
                "code": "500",
                "face_encodings": "该人脸已经注册"
            }
            # 已经注册。
            return jsonify(result)

        query = "INSERT INTO vectors (username,phone,mail, vec_data) VALUES ('{}','{}','{}', CUBE(array[{}]))".format(
            formData.get("username"), formData.get("phone"), formData.get("mail"),
            ','.join(str(s) for s in encodings[0][0:128]),

        )
        db.execute(query)
        conn.commit()

    # 将结果作为json返回
    conn.close()
    result = {
        "code": "200",
        "face_encodings": "成功"
    }
    # 图像文件似乎有效！返回人脸编码。
    return jsonify(result)


# 人脸验证
@app.route('/face/verification', methods=['POST'])
def upload_image():
    try:
        trysss = request.files['file']
        logging.warning('try')
    except Exception:
        logging.warning('抛出')
        # 将结果作为json返回
        result = {
            "code": 500,
            "face_found_in_image": False,
            "is_picture_of_obama": False
        }
        return jsonify(result)
    else:
        logging.warning('未抛出')
        if request.method == 'POST':
            if 'file' not in request.files:
                return redirect(request.url)

            file = request.files['file']
            if file.filename == '':
                return redirect(request.url)

            if file and allowed_file(file.filename):
                print(file)

                encodingsimg = face_recognition.load_image_file(file)
                if request.form.get('type') == None:
                    # 抛出则是没有发type，PC端
                    encodings = face_recognition.face_encodings(encodingsimg)
                else:
                    face_locations = face_recognition.face_locations(encodingsimg, model='cnn')
                    encodings = face_recognition.face_encodings(encodingsimg, face_locations)

                # 加载上载的图像文件
                isnot = detect_faces_in_image(encodings)
                # 将结果作为json返回
                result = {
                    "code": 200,
                    "face_found_in_image": isnot[0],
                    "is_picture_of_obama": isnot[1],
                    "username": isnot[1] if isnot[1] == False else isnot[2]
                }
                return jsonify(result)

            # 将结果作为json返回
        result = {
            "code": 500,
            "face_found_in_image": False,
            "is_picture_of_obama": False
        }
        return jsonify(result)


# 判断人脸是否存在
def detect_faces_in_image(encodings):

    conn = psycopg2.connect(database=dbdatabase, user=dbuser, password=dbpassword, host=dbhost,
                            port=dbport)
    db = conn.cursor()
    username = ""
    # 是否匹配
    is_obama = False
    if len(encodings) > 0:
        query = "SELECT * FROM vectors  " + \
                "ORDER BY vec_data <-> '{}' ::cube ASC LIMIT 3".format(
                    ','.join(str(s) for s in encodings[0][0:128]),
                )
        db.execute(query)
        # 获取结果集的每一行
        while True:
            rows = db.fetchmany(2000)
            if not rows:
                break
            for row in rows:
                id, name, phone, mail, vecdata = row
                username = name
                known_face_encoding = ast.literal_eval(vecdata)
                # 查看上传图像中的第一张面孔是否与数据库的已知面孔匹配
                match_results = face_recognition.compare_faces([known_face_encoding], encodings[0], tolerance=0.50)
                print(match_results)
                if match_results[0]:
                    is_obama = True
                    break

    else:
        logging.warning('No encodings')
    # 使用 face_recognition.face_encodings(img) 生成的预先计算的人脸编码
    # 查出来为空则数据库没有注册此人人脸数据
    conn.close()
    face_found = False

    if len(encodings) > 0:
        face_found = True

    return face_found, is_obama, username


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

