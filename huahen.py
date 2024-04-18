import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv


class Huahen:
    def __init__(self):
        self.qualif=0

    def single_detect(self,image_path):

        img=cv.imread(image_path)
        #裁剪
        gongjian = img[:, 550:700, :]

        #灰度化
        gray = cv.cvtColor(gongjian, cv.COLOR_BGR2GRAY)

        kx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
        ky = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
        imgX = cv.filter2D(gray, cv.CV_64F, kx)
        imgclip = np.abs(imgX).clip(0, 255)

        #二值化
        ignore, img_bin = cv.threshold(imgclip, 110, 255, cv.THRESH_BINARY)

        # print(img_bin.dtype)
        # 查找轮廓
        contours, hierarchy = cv.findContours(img_bin.astype(np.uint8), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        # 输出轮廓个数
        # print(len(contours))
        for i in range(0, len(contours)):
            length = cv.arcLength(contours[i], True)
            # print(length)
            # 通过轮廓长度筛选
            if length > 35:
                cv.drawContours(gongjian, contours[i], -1, (0, 0, 255), 2)
                self.qualif=1
        # plt.imshow(gongjian)
        # return{
        #     "huahen":self.qualif
        # }
        return self.qualif

def cvtColor(image):
    if len(np.shape(image)) == 3 and np.shape(image)[2] == 3:
        return image
    else:
        image = image.convert('RGB')
        return image

