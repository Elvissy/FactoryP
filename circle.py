import cv2
import numpy as np
class Circle:
    def __init__(self):
        self.num = 0

    def single_detect(self, image_path):
        # 读取图像
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        # 高斯模糊以减少噪声
        blurred = cv2.GaussianBlur(image, (5, 5), 0)

        # 使用Canny边缘检测
        edges = cv2.Canny(blurred, 50, 150)

        # 使用形态学操作增强边缘
        kernel = np.ones((3, 3), np.uint8)
        dilated_edges = cv2.dilate(edges, kernel, iterations=1)

        # Hough圆检测
        circles = cv2.HoughCircles(
            dilated_edges,
            cv2.HOUGH_GRADIENT_ALT,
            dp=1,
            minDist=28,
            param1=50,
            param2=0.8,
            minRadius=0,
            maxRadius=0
        )

        # 如果找到圆，画出圆并显示结果
        if circles is not None:
            circles = np.uint16(np.around(circles))
            self.num = len(circles[0])

            for i in circles[0, :]:
                # 画出圆心
                cv2.circle(image, (i[0], i[1]), 2, (0, 255, 0), 3)
                # 画出圆
                cv2.circle(image, (i[0], i[1]), i[2], (0, 0, 255), 3)

            # 在图像上显示圆的数量
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image, f'Number of Circles: {self.num}', (10, 30), font, 1, (0, 0, 0), 2, cv2.LINE_AA)

            # cv2.imshow('Detected Circles', image)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
        else:
            print("No circles found.")
        return {
            "circle": self.num
        }
