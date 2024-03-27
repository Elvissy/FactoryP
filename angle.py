import cv2
import numpy as np
import matplotlib.pyplot as plt

class Angle:
    def __init__(self):
        self.angles = []

    def single_detect(self, image_path):
        # 读取照片
        image = cv2.imread(image_path)
        # 灰度化
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 高斯模糊以减少噪声
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # 形态学操作
        kernel = np.ones((5, 5), np.uint8)
        morph_image = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)
        # Canny边缘检测
        # edges = cv2.Canny(blurred, 50, 150)
        edges = cv2.Canny(morph_image, 50, 150, apertureSize=3)
        # 使用霍夫变换检测直线
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=166)
        # print(lines)

        # 计算角度
        slopes = []
        for line in lines:
            for rho, theta in line:
                slope = np.degrees(theta).tolist()
                # slope = np.rad2deg(theta)
                if slope not in slopes:
                    slopes.append(slope)

        for i in range(len(slopes)):
            for j in range(i + 1, len(slopes)):
                angle = abs(slopes[i] - slopes[j])
                if angle not in self.angles and angle > 10:
                    self.angles.append(angle)
        # 返回检测到的角度

        return {
                "angle": self.angles
            }
