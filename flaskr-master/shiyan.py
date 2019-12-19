# -*- coding: UTF-8 -*-
import base64
import importlib,sys
import face_recognition
from PIL import Image, ImageDraw
from scipy import optimize
from math import atan,sin,cos
importlib.reload(sys)
import dlib
#sys.setdefaultencoding( "utf-8" )
from PIL import ImageDraw
from PIL import ImageFilter
import random,sys
import cv2
import numpy as np
import sqlite3
from contextlib import closing
from flask import session, g, redirect, url_for, \
	abort, render_template, flash
import os
from flask import Flask, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
#设置上传文件夹地址、允许的文件扩展名、限制文件大小
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config.update(dict(
DATABASE = os.path.join(app.root_path, 'flaskr.db'),
DEBUG = True,
SECRET_KEY = 'HeLLoWORld',
USERNAME = 'admin',
PASSWORD = 'default',
))
app.config['UPLOAD_FOLDER'] = 'D:/360MoveData/Users/鸿哥/Desktop/flaskr-master/flaskr-master/photo'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


#数据库
def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()

def f_1(x, A, B):
	return A*x + B

@app.before_request
def before_request():
	g.db=connect_db()

@app.teardown_request
def teardown_request(exception):
	g.db.close()

#主页
@app.route('/')
def index():
	return render_template('1.html')

#说明
@app.route('/dh')
def sm():
	return render_template('dh.html')

#关于
@app.route('/关于我们')
def gy():
	return render_template('关于我们.html')

#登录
@app.route('/login', methods=['GET', 'POST'])
def  login():
	error = None
	message = None
	if request.method=='POST':
		cur=g.db.cursor().execute('select username from users')
		usernameList = [str(row[0]) for row in cur.fetchall()]
		if request.form['username'] not in usernameList:
			error =  '账号错误'
		else:
			cur=g.db.cursor().execute('select password from users where username=(?)',
				[request.form['username']])
			usernameList = [str(row[0]) for row in cur.fetchall()]
			if request.form['password'] not in usernameList:
				error = '密码错误'
			else:
				session['logged_in']=True
				return render_template('上传.html',message='登陆成功') #改成新写的html，原本layout.html
	return render_template('login.html',error=error)

#检查文件后缀
def allowed_file(filename):
	return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#配置一个函数来获取上传文件的url
@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/up_photo', methods=['GET', 'POST'])
def upload_file():
	message = None
	error = '上传数据有误，请重新上传'
	if request.method == 'POST':
		file = request.files['file']#当按下提交键后，通过request对象上的files获取文件
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))#使用save()方法保存文件
			file_url = url_for('uploaded_file',filename=filename)
			im = cv2.imread('photo/1.jpg')
			message = '上传成功'
			return render_template('up_photo.html',message=message) + '<br><img src=' + file_url + ' width ="200" height = "200">'
		else:
			return render_template('up_photo.html', error=error)
	return render_template('up_photo.html',message=message)


#注销
@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	return render_template('1.html')

#注册
@app.route('/register',methods=['GET','POST'])
def register():
	error=None
	msg=None
	if request.method == 'POST':
		if request.form['username'] =='':
			error = '请输入用户ID'
		elif request.form['password'] == '':
			error = '请输入密码'
		elif request.form['password1'] == '':
			error = '请再次确认密码'
		elif request.form['password'] != request.form['password1']:
			error = '两次输入的密码不一致'
		else:
			cur = g.db.cursor().execute('select username from users')
			usernameList = [str(row[0]) for row in cur.fetchall()]
			if request.form['username'] in usernameList:
				error = '用户名已经被注册'
			elif len(request.form['password'])<6 or len(request.form['password'])>16:
				error='密码长度范围为6到16'
			else:
				g.db.cursor().execute('insert into users(username,password)  values(?,?)',
                		[request.form['username'],request.form['password']])
	if error is None:
		g.db.commit()
		return render_template('register.html',msg = '注册成功，请登录')
	return render_template('register.html',error = error)

#美颜
@app.route('/white', methods=['GET', 'POST'])
def WhiteBeauty():
	whi = 1.2
	image = cv2.imread('photo/1.jpg')
	white = np.uint8(np.clip((whi * image + 10), 0, 255))
	cv2.imwrite('photo/White1.jpg', white)
	file_urla = url_for('uploaded_file',filename='White1.jpg')
	file_urlb = url_for('uploaded_file', filename='1.jpg')
	return render_template('white.html') + '<br>原图<br><img src=' + file_urlb + ' width ="200" height = "200">' \
											+ '<br>处理后<br><img src=' + file_urla + ' width ="200" height = "200">'

#滤镜
@app.route('/filter', methods=['GET', 'POST'])
def filter():
	img = Image.open("photo/1.jpg")
	img = img.convert("RGB")
	imgfilted_em = img.filter(ImageFilter.EMBOSS)
	imgfilted_b = img.filter(ImageFilter.BLUR)
	imgfilted_em.save("photo/filtera.jpg")
	imgfilted_b.save("photo/filterb.jpg")
	file_urla = url_for('uploaded_file',filename='filtera.jpg')
	file_urlb = url_for('uploaded_file', filename='filterb.jpg')
	return render_template('filter.html') + '<br>浮雕滤镜<br><img src=' + file_urla + ' width ="200" height = "200">' \
		   + '<br>模糊滤镜<br><img src=' + file_urlb + ' width ="200" height = "200">'

#磨皮
@app.route('/mopi', methods=['GET', 'POST'])
def mopi():
	image = cv2.imread('photo/1.jpg')
	Remove = cv2.bilateralFilter(image,0,0,10)
	cv2.imwrite('photo/Remove.jpg', Remove)
	file_urla = url_for('uploaded_file',filename='Remove.jpg')
	file_urlb = url_for('uploaded_file', filename='1.jpg')
	return render_template('mopi.html') + '<br>原图<br><img src=' + file_urlb + ' width ="200" height = "200">' \
											+ '<br>处理后<br><img src=' + file_urla + ' width ="200" height = "200">'

#人脸检测
@app.route('/facedetect', methods=['GET', 'POST'])
def face():
	detector = dlib.get_frontal_face_detector()
	predictor = dlib.shape_predictor('D:/test/shape_predictor_68_face_landmarks.dat')
	image = cv2.imread('photo/1.jpg')
	dets = detector(image, 1)
	for k, d in enumerate(dets):
		shape = predictor(image, d)
		for index, pt in enumerate(shape.parts()):
			pt_pos = (pt.x, pt.y)
			cv2.circle(image, pt_pos, 1, (255, 0, 0), 2)
			# 利用cv2.putText输出1-68
			font = cv2.FONT_HERSHEY_SIMPLEX
			cv2.putText(image, str(index + 1), pt_pos, font, 0.3, (0, 0, 255), 1, cv2.LINE_AA)
	cv2.imwrite('photo/face.jpg', image)
	file_urla = url_for('uploaded_file',filename='face.jpg')
	file_urlb = url_for('uploaded_file', filename='1.jpg')
	return render_template('facedetect.html') + '<br>原图<br><img src=' + file_urlb + ' width ="200" height = "200">' \
											+ '<br>处理后<br><img src=' + file_urla + ' width ="200" height = "200">'


#贴纸
@app.route('/paste', methods=['GET', 'POST'])
def paste():
	image = face_recognition.load_image_file("photo/1.jpg")
	map = Image.open('圣诞帽.png')
	map = map.convert("RGBA")
	datas = map.getdata()
	newData = []
	for item in datas:
		if item[0] == 255 and item[1] == 255 and item[2] == 255:  # 背景色为黑色 的像素点
			newData.append((0, 0, 0, 0))  # 把A值设置为0
		else:
			newData.append(item)
	map.putdata(newData)
	map_w, map_h = map.size
	face_landmarks_list = face_recognition.face_landmarks(image)
	face_locations = face_recognition.face_locations(image)
	pil_image = Image.fromarray(image)
	for face_landmarks, (top, right, bottom, left), i in zip(face_landmarks_list, face_locations,
															 range(len(face_landmarks_list))):
		facial_features = [
			'chin',  # 下巴
			'left_eyebrow',  # 左眉毛
			'right_eyebrow',  # 右眉毛
			'nose_bridge',  # 鼻樑
			'nose_tip',  # 鼻尖
			'left_eye',  # 左眼
			'right_eye',  # 右眼
			'top_lip',  # 上嘴唇
			'bottom_lip'  # 下嘴唇
		]
		d = ImageDraw.Draw(pil_image)
		sum_height = 0
		low_chin = face_landmarks['chin'][0][1]
		nose_x = []
		nose_y = []
		for height1, height2 in zip(face_landmarks['left_eyebrow'], face_landmarks['right_eyebrow']):
			sum_height = height1[1] + height2[1] + sum_height
		average_height = sum_height / (len(face_landmarks['left_eyebrow']) + len(face_landmarks['right_eyebrow']))
		for bottom_chin in face_landmarks['chin']:  # 获取到下巴的最低点
			if low_chin < bottom_chin[1]:
				low_chin = bottom_chin[1]
		for nose in face_landmarks['nose_bridge']:
			nose_x.append(nose[0])
			nose_y.append(nose[1])
		A1, B1 = optimize.curve_fit(f_1, nose_x, nose_y)[0]
		radian = atan(A1)
		angele = radian * 180 / (3.14)
		if angele > 0:
			angele = 90 - angele
		else:
			angele = -(angele + 90)
		face_w = right - left
		face_h = bottom - top
		map_location = int((low_chin - average_height) / 2)
		forehead_y = low_chin - map_location * 3
		map_setsize_h = int(map_h / map_w) * face_w
		map_set = map.resize((face_w, map_setsize_h))
		map_setsize_w = map_set.size[0]
		map_setsize_h = map_set.size[1]
		map_set = map_set.rotate(angele, expand=1)
		if angele < 0:
			angele = - angele
		radian_angele = angele * 3.14 / 180
		forehead_x = (forehead_y - B1) / A1
		map_setx = int(forehead_x - map_setsize_w * (cos(radian_angele) / 2 + sin(radian_angele)))
		map_sety = int(forehead_y - map_setsize_h * (sin(radian_angele) / 2 + cos(radian_angele)))
		pil_image.paste(map_set, (map_setx, map_sety), mask=map_set)
		image_pil2arr = np.array(pil_image)
		image_arr2pil = Image.fromarray(image_pil2arr)
		image_arr2pil.save('photo/paste.jpg')
	file_urla = url_for('uploaded_file',filename='paste.jpg')
	file_urlb = url_for('uploaded_file', filename='1.jpg')
	return render_template('paste.html') + '<br>原图<br><img src=' + file_urlb + ' width ="200" height = "200">' \
											+ '<br>处理后<br><img src=' + file_urla + ' width ="200" height = "200">'


if __name__ == '__main__':
	app.run()









