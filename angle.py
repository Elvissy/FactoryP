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
        # lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=166)
        lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength=100,maxLineGap=50)
        # print(lines)

        # 计算角度
        # slopes = []
        # for line in lines:
        #     for rho, theta in line:
        #         slope = np.degrees(theta).tolist()
        #         # slope = np.rad2deg(theta)
        #         if slope not in slopes:
        #             slopes.append(slope)

        # for i in range(len(slopes)):
        #     for j in range(i + 1, len(slopes)):
        #         angle = abs(slopes[i] - slopes[j])
        #         if angle not in self.angles and angle > 10:
        #             self.angles.append(angle)
        # # 返回检测到的角度

        # return {
        #         "angle": self.angles
        #     }
        # return self.angles

        # 计算角度
        slopes = []
        def angle_between_lines(m1, m2):
            if m1 * m2 == -1:  # 当两条线垂直时
                return 90
            else:
                theta_rad = math.atan(abs((m2 - m1) / (1 + m1 * m2)))
                theta_deg = math.degrees(theta_rad)
                return theta_deg
            
        angles = []
        # 计算所有线对之间的夹角
        for i in range(len(slopes)):
            for j in range(i + 1, len(slopes)):
                angle = angle_between_lines(slopes[i], slopes[j])
                if angle not in angles and angle > 10:
                    angles.append(angle)
        # 保留两位小数，并取平均值
        rounded_numbers = [round(num, 2) for num in angles]
        average = sum(rounded_numbers) / len(rounded_numbers)
        return average

        
