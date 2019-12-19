# encoding = utf-8
import cv2
import numpy as np

filepath = 'photo/0.jpg'

def WhiteBeauty():
    whi = 1.2
    image = cv2.imread(filepath)
    white = np.uint8(np.clip((whi * image + 10), 0, 255))
    cv2.imwrite('photo/White.jpg', white)
    cv2.imshow('White', white)

if __name__ == "__main__":

    WhiteBeauty()

    #cv2.waitKey(0)
   # cv2.destroyAllWindows()
