# encoding = utf-8
import cv2
import numpy as np

filepath = '14.jpg'

def Filter():
    # """
    # 色彩窗的半径
    # 图像将呈现类似于磨皮的效果
    # """
    # image：输入图像，可以是Mat类型，
    #       图像必须是8位或浮点型单通道、三通道的图像
    # 0：表示在过滤过程中每个像素邻域的直径范围，一般为0
    # 后面两个数字：空间高斯函数标准差，灰度值相似性标准差
    image = cv2.imread(filepath)
    remove = cv2.bilateralFilter(image,0,0,10)
    cv2.imwrite('Buffing.jpg', remove)
    cv2.imshow('Buffing', remove)

if __name__ == "__main__":

    Filter()

    cv2.waitKey(0)
    cv2.destroyAllWindows()
