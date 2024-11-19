import cv2
import numpy as np
from tkinter import Tk, filedialog
import csv
import os

# 初始化全局变量
drawing = False  # 是否正在绘制
ix, iy = -1, -1  # 初始化绘制起点
output_file = "brightness_density_results.csv"  # 结果保存的文件名


def calculate_brightness_density_and_contour(region):
    """
    计算选定区域的亮区密度，并返回最外层轮廓
    """
    # 转换为灰度图像
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

    # 二值化：亮度大于150的像素视为亮区
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # 查找所有轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 如果没有亮区，返回密度为0，轮廓为空
    if len(contours) == 0:
        return 0, None

    # 将所有轮廓点整合为一个集合
    all_points = np.vstack(contours)

    # 计算最外层轮廓（凸包）
    outermost_contour = cv2.convexHull(all_points)

    # 计算亮区的像素数量
    bright_pixels = cv2.countNonZero(binary)

    # 计算最外层轮廓的面积
    contour_area = cv2.contourArea(outermost_contour)

    # 避免除以零
    if contour_area == 0:
        return 0, outermost_contour

    # 计算密度
    density = bright_pixels / contour_area

    return density, outermost_contour


# 定义鼠标回调函数
def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, img

    if event == cv2.EVENT_LBUTTONDOWN:  # 鼠标按下，开始绘制
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:  # 鼠标移动，动态显示矩形
        if drawing:
            img_copy = img.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('image', img_copy)

    elif event == cv2.EVENT_LBUTTONUP:  # 鼠标松开，绘制完成
        drawing = False

        # 确保选区的起始和终止坐标正确
        x1, y1 = min(ix, x), min(iy, y)
        x2, y2 = max(ix, x), max(iy, y)

        # 绘制最终的矩形
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # 提取选区
        selected_region = img[y1:y2, x1:x2]

        # 计算亮区密度和最外层轮廓
        density, outermost_contour = calculate_brightness_density_and_contour(selected_region)

        # 保存结果到 CSV 文件
        save_result_to_csv((x1, y1, x2, y2), density)

        # 绘制选区内的最外层轮廓
        if outermost_contour is not None:
            # 在选区中绘制轮廓（局部绘制，不影响全图）
            cv2.drawContours(img[y1:y2, x1:x2], [outermost_contour], -1, (0, 0, 255), 2)
            print(f"选定区域的亮区密度: {density:.2f}")
        else:
            print("选区内没有亮区")

        # 显示最终图像
        cv2.imshow('image', img)


def save_result_to_csv(region_coords, density):
    """
    将结果保存到 CSV 文件
    :param region_coords: 选区的坐标 (x1, y1, x2, y2)
    :param density: 计算的亮区密度
    """
    # 检查文件是否存在，如果不存在则创建并写入表头
    if not os.path.exists(output_file):
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["X1", "Y1", "X2", "Y2", "Brightness Density"])

    # 追加结果到文件
    with open(output_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([*region_coords, density])


# 打开文件选择对话框
def open_image():
    Tk().withdraw()  # 隐藏Tk主窗口
    filepath = filedialog.askopenfilename(
        title="选择图片",
        filetypes=[("图像文件", "*.png;*.jpg;*.jpeg;*.bmp"), ("所有文件", "*.*")]
    )
    if filepath:
        return cv2.imread(filepath)
    return None


# 主函数
if __name__ == "__main__":
    img = open_image()
    if img is None:
        print("未选择图片或图片无法读取")
        exit()

    print(f"计算结果将保存到: {output_file}")

    # 创建窗口并绑定鼠标回调函数
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', draw_rectangle)

    # 持续展示窗口直到用户按下Esc键退出
    while True:
        cv2.imshow('image', img)
        if cv2.waitKey(1) & 0xFF == 27:  # 按下ESC键退出循环
            break

    cv2.destroyAllWindows()
