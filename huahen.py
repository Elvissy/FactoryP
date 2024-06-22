import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv


class Huahen:
    def __init__(self):
        self.qualif=0

    def single_detect(self,image_path,degree):

        img=cv.imread(image_path)

        #灰度化
        gray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)

        kx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
        ky = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
        imgX=cv.filter2D(gray,cv.CV_64F,kx)
        imgY=cv.filter2D(gray,cv.CV_64F,ky)
        imgXY=np.sqrt(imgX**2+imgY**2)
        imgXY2=np.abs(imgX)+np.abs(imgY)
        imgclipX=np.abs(imgX).clip(0,255)
        imgclipY=np.abs(imgY).clip(0,255)

        # 形态学操作
        kernel = np.ones((3,3), np.uint8)
        morph_image = cv.morphologyEx(imgXY2, cv.MORPH_CLOSE, kernel)

        #二值化
        _, binary_image = cv.threshold(morph_image, degree, 255, cv.THRESH_BINARY)

        # print(img_bin.dtype)
        # 查找轮廓
        contours, hierarchy = cv.findContours(binary_image.astype(np.uint8), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        # 输出轮廓个数
        # print(len(contours))

        binary_image_color = cv.cvtColor(binary_image.astype(np.uint8), cv.COLOR_GRAY2BGR)
        for i in range(0, len(contours)):
            length = cv.arcLength(contours[i], True)
            # print(length)
            # 通过轮廓长度筛选
            if 10<length<3000 :
                cv.drawContours(binary_image_color, contours[i], -1, (0, 0, 255), 2)
                self.qualif=1
        return self.qualif

def cvtColor(image):
    if len(np.shape(image)) == 3 and np.shape(image)[2] == 3:
        return image
    else:
        image = image.convert('RGB')
        return image


if __name__ == '__main__':
    huahen=Huahen()
    result = huahen.single_detect('./data/1/1.bmp')
    print(result)
