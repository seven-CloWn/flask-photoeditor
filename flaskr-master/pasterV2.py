# coding = utf-8
# 绘制面部轮廓
import face_recognition
from PIL import Image, ImageDraw
from scipy import optimize
from math import atan,sin,cos
import numpy as np
# 将图片文件加载到numpy 数组中
# 直线方程函数
def f_1(x, A, B):
    return A*x + B

image = face_recognition.load_image_file("1.jpg") #yiqi.png
map = Image.open('圣诞帽.png') #贴图

map = map.convert("RGBA")  #代表Red（红色） Green（绿色） Blue（蓝色）和 Alpha的色彩空间
datas = map.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255: #背景色为黑色 的像素点
        newData.append((0, 0, 0, 0))  # 把A值设置为0
    else:
        newData.append(item)

map.putdata(newData)
#map.save("img_new.png", "PNG")  # 保存下来

map_w,map_h = map.size

#查找图像中所有面部的所有面部特征
face_landmarks_list = face_recognition.face_landmarks(image) #人脸关键点信息
face_locations = face_recognition.face_locations(image) #人脸位置

pil_image = Image.fromarray(image)
for face_landmarks,(top, right, bottom, left),i in zip(face_landmarks_list,face_locations,range(len(face_landmarks_list))):
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
    # left top 是人脸位置 左上角的坐标  right bottom是人脸位置 右下角的坐标
    d = ImageDraw.Draw(pil_image)

    sum_height = 0
    low_chin = face_landmarks['chin'][0][1]
    nose_x = []
    nose_y = []
    for height1,height2 in zip(face_landmarks['left_eyebrow'],face_landmarks['right_eyebrow']):
        sum_height = height1[1] +height2[1] +sum_height

    # 计算出眉毛 在竖直方向的 中间点
    average_height = sum_height/(len(face_landmarks['left_eyebrow'])+len(face_landmarks['right_eyebrow']))
    for bottom_chin in face_landmarks['chin']: #获取到下巴的最低点
        if low_chin < bottom_chin[1] :
            low_chin = bottom_chin[1]
    for nose in face_landmarks['nose_bridge']:
        nose_x.append(nose[0])
        nose_y.append(nose[1])
    A1, B1 = optimize.curve_fit(f_1, nose_x, nose_y)[0]  #拟合出鼻梁所在的直线 A1为斜率 B1为截距

    #print(A1,B1)
    radian = atan(A1)  # 利用反三角函数 计算出角度的弧度制
    angele =  radian*180/(3.14)  # 计算出角度
   # print('第',i,'个人倾斜原始角度',angele)
   # print('斜率为',A1,'截距为',B1)
    if angele >0:
        angele = 90-angele  # 脸没有倾斜的时候 鼻梁与水平线夹角接近90度， 根据这个计算出脸的倾斜角度
        #print('角度>0')
    else:
        angele = -(angele+90)
   # print('转换后角度为',angele)
    face_w = right-left  #人脸宽度
    face_h = bottom-top   #人脸长度
    map_location = int((low_chin - average_height)/2)  #根据人脸比例 人脸横着分为三份 眉毛上占三分之一
                                                        # map_location 就是眉毛到头顶的竖直位置 也就是额头的长度
    forehead_y = low_chin - map_location*3

    map_setsize_h = int(map_h/map_w)*face_w

    map_set = map.resize((face_w,map_setsize_h)) #设定logo大小  宽， 高

    map_setsize_w = map_set.size[0]
    map_setsize_h = map_set.size[1]  #获取到旋转后图片的尺寸

    map_set = map_set.rotate(angele,expand = 1)  #旋转图片


    if angele<0:
        angele = - angele
    radian_angele = angele*3.14/180

    forehead_x = (forehead_y - B1)/A1

    map_setx =int(forehead_x-map_setsize_w*(cos(radian_angele)/2+sin(radian_angele)))
    map_sety =int(forehead_y-map_setsize_h*(sin(radian_angele)/2+cos(radian_angele)))

    pil_image.paste(map_set,(map_setx,map_sety),mask= map_set)  #mask 能够去掉掩码

pil_image.show()
image_pil2arr = np.array(pil_image)  # 转成ndarray
image_arr2pil = Image.fromarray(image_pil2arr)  # 矩阵再转为图像
image_arr2pil.save('贴纸完成.jpg')  # PIL保存图像