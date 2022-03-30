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
from flask_cors import *
import ast
import json
import pymysql
from io import BytesIO
import base64
import numpy as np
import face_recognition
from flask import Flask, jsonify, request, redirect

dbhost = ''
dbport = 3306
dbuser = ''
dbpass = ''
dbname = 'face'

# 数据库信息
# 您可以将其更改为系统上的任何文件夹
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": "POST, GET", "expose_headers": "Content-Type"}})  # 允许所有域名跨域


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 人脸注册
@app.route('/face/registration', methods=['GET', 'POST'])
def upload_image_registration():
    try:
        trysss = request.files['file']
    except Exception:
        formData = request.form.to_dict()
        # 检查是否上传了有效的图片文件
        if request.method == 'POST':
            file = formData.get("file")
            img = face_recognition.load_image_file(BytesIO(base64.urlsafe_b64decode(file)))
            unknown_face_encodings = face_recognition.face_encodings(img)
            face_encoding = np.array(unknown_face_encodings).tolist()

            py_mysql_insert(formData.get("username"), formData.get("phone"), formData.get("mail"),
                            face_encoding)
            # 将结果作为json返回
            result = {
                "code": "200",
                "face_encodings": np.array(unknown_face_encodings).tolist()
            }
            # 图像文件似乎有效！返回人脸编码。
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
                unknown_face_encodings = face_recognition.face_encodings(img)
                formData = request.form.to_dict()
                face_encoding = np.array(unknown_face_encodings).tolist()
                py_mysql_insert(formData.get("username"), formData.get("phone"), formData.get("mail"),
                                face_encoding)
                # 将结果作为json返回
                result = {
                    "code": "200",
                    "face_encodings": np.array(unknown_face_encodings).tolist()
                }
                # 图像文件似乎有效！返回人脸编码。
                return jsonify(result)


# 人脸验证
@app.route('/face/verification', methods=['POST'])
def upload_image():
    try:
        trysss = request.files['file']
    except Exception:
        formData = request.form.to_dict()
        # 检查是否上传了有效的图片文件
        if request.method == 'POST':
            file = formData.get("file")
            mail = formData.get("mail")
            # 图像文件似乎有效！检测人脸并返回结果。
            # 加载上载的图像文件
            return detect_faces_in_image(BytesIO(base64.urlsafe_b64decode(file)), mail)

        # 如果没有上传有效的图片文件，显示文件上传表单：
        # 将结果作为json返回
        result = {
            "code": 500,
            "face_found_in_image": False,
            "is_picture_of_obama": False
        }
        return jsonify(result), 200
    else:

        if request.method == 'POST':
            if 'file' not in request.files:
                return redirect(request.url)

            file = request.files['file']

            if file.filename == '':
                return redirect(request.url)

            if file and allowed_file(file.filename):
                # 图像文件似乎有效！检测人脸并返回结果。
                # 加载上载的图像文件
                formData = request.form.to_dict()

                return detect_faces_in_image(file, formData.get("mail"))

            # 如果没有上传有效的图片文件，显示文件上传表单：
            # 将结果作为json返回
        result = {
            "code": 500,
            "face_found_in_image": False,
            "is_picture_of_obama": False
        }
        return jsonify(result), 200


# 判断人脸是否存在
def detect_faces_in_image(file_stream, mail):
    # 使用 face_recognition.face_encodings(img) 生成的预先计算的人脸编码
    mysqldata = py_mysql_select(mail)
    facial_information = mysqldata[0]
    # 查出来为空则数据库没有注册此人人脸数据
    if facial_information == "":
        # 将结果作为json返回
        result = {
            "code": 200,
            "face_found_in_image": False,
            "is_picture_of_obama": False
        }
        return jsonify(result), 200
    known_face_encoding = ast.literal_eval(facial_information)

    # 加载上载的图像文件
    img = face_recognition.load_image_file(file_stream)
    # 获取上传图像中任何人脸的人脸编码
    unknown_face_encodings = face_recognition.face_encodings(img)

    face_found = False
    is_obama = False

    if len(unknown_face_encodings) > 0:
        face_found = True
        # 查看上传图像中的第一张面孔是否与奥巴马的已知面孔匹配
        match_results = face_recognition.compare_faces([known_face_encoding], unknown_face_encodings[0], tolerance=0.55)
        if match_results[0]:
            is_obama = True

    # 将结果作为json返回
    result = {
        "code": 200,
        "face_found_in_image": face_found,
        "is_picture_of_obama": is_obama,
        "username": is_obama if is_obama == False else mysqldata[1]
    }
    return jsonify(result), 200


# 识别信息插入数据库
def py_mysql_insert(username, phone, mail, facial_information):
    try:
        db = pymysql.connect(host=dbhost, port=dbport, user=dbuser, password=dbpass, database=dbname, charset='utf8')
        print('数据库连接成功!')

        cur = db.cursor()
        sql = 'insert into face_data(username,phone,mail,facial_information) Value (%s,%s,%s,%s)'
        value = (username, phone, mail, json.dumps(facial_information[0]))
        cur.execute(sql, value)
        db.commit()
        print('数据插入成功')
    except pymysql.Error as e:
        print("数据插入失败" + str(e))
        db.rollback()
    db.close()


# 根据邮箱信息查询数据库得到人脸信息
def py_mysql_select(mail):
    print(mail)
    try:
        db = pymysql.connect(host=dbhost, port=dbport, user=dbuser, password=dbpass, database=dbname, charset='utf8')
        print('数据库连接成功!')
        cur = db.cursor()
        sql = 'SELECT * FROM face_data WHERE mail = %s'
        cur.execute(sql, mail)
        results = cur.fetchall()
        facial_information = "";
        username = "";
        for row in results:
            username = row[2]
            facial_information = row[5]

    except pymysql.Error as e:
        print("数据查询失败" + str(e))
        db.rollback()
    db.close()
    return facial_information, username


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

