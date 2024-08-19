import cv2
import numpy as np
import os
from. import utils
import json

def show_image(name, image):
    # 显示结果  
    cv2.imshow(name, image)  
    cv2.waitKey(0)  
    cv2.destroyAllWindows()

def pre_processing_image(img_path):
    img = cv2.imread(img_path)  
    if img is None:  
        print("Error: Image not found.")  
        return  
    # print(f"图片宽高是:{img.shape[1]} x {img.shape[0]}")
    # 灰度化  
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

    return img, gray

# 获取本地棋盘数据
def get_board_data():
    x_array = []
    y_array = []
    error = ''
    try:
        # 尝试读取 JSON 文件
        with open('./app/json/board.json', 'r') as file:
            data = json.load(file)

        # 提取横坐标和纵坐标
        x_array = data["x"]
        y_array = data["y"]

        # print("读取的横坐标：", x_array)
        # print("读取的纵坐标：", y_array)
    except FileNotFoundError:
        error = '文件未找到'
        print(error)
    return x_array, y_array, error
# 识别棋盘
def board_recognition(img, gray):
    x_arr, y_arr, error = get_board_data()
    if not error: return x_arr, y_arr

    # 高斯模糊  
    gaus = cv2.GaussianBlur(gray, (5, 5), 0)  
    # 边缘检测  
    edges = cv2.Canny(gaus, 20, 120, apertureSize=3)  
    # show_image('Edges', edges)
    
    # 膨胀操作以合并相邻线条  
    # kernel = np.ones((3, 3), np.uint8)  # 定义膨胀核的大小，可以根据需要调整  
    # dilated_edges = cv2.dilate(edges, kernel, iterations=1) 
    
    # 腐蚀操作以恢复线条宽度  
    # eroded_edges = cv2.erode(dilated_edges, kernel, iterations=1) 
    
    # 可选：再次膨胀以调整线条宽度  
    # final_edges = cv2.dilate(eroded_edges, kernel, iterations=1)
    # show_image('Edges', final_edges)

    # 霍夫线变换  
    lines = cv2.HoughLinesP(edges, 0.5, np.pi/180, threshold=80, minLineLength=100, maxLineGap=5)  
    
    # 创建一张新图
    # black_img = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
    # black_img.fill(0) # 使用黑色填充图片区域

    # 过滤线段并在新图上绘制
    # 竖线 (x1 == x2)
    x_array = []
    vlines, yMin, yMax = utils.filter_vertical_lines(lines, img.shape[1])
    for line in vlines:  
        for x1, y1, x2, y2 in line:
            # cv2.line(black_img, (x1, yMin), (x2, yMax), (0, 255, 0), 1)
            x_array.append(int(x1))

    # 横线 (y1 == y2)
    y_array = []
    hlines, xMin, xMax = utils.filter_horizontal_lines(lines, img.shape[1])
    for line in hlines:  
        for x1, y1, x2, y2 in line:  
            # cv2.line(black_img, (xMin, y1), (xMax, y2), (0, 255, 0), 1)
            y_array.append(int(y1))
    
    
    # 显示结果 
    # show_image('Detected Lines', black_img) 
    # print(f"横坐标:{x_array}\n 纵坐标:{y_array}")
    # 将数组组合成一个字典
    data = {
        "x": x_array,
        "y": y_array
    }

    # 写入 JSON 文件
    with open('./app/json/board.json', 'w') as file:
        json.dump(data, file)

    return x_array, y_array

# 识别棋子
def pieces_recognition(img, gray):

    # 模糊处理，不管是用mediaBlur还是GaussianBlur, 实际发现这不是必要的。用霍夫圆检测，直接使用灰度图也一样能找出来，可能棋子的圆相对规范的原因？
    #blur = cv2.medianBlur(gray, 5)
    #gaus = cv2.GaussianBlur(gray,(3,3),0)

    width = img.shape[1]
    maxRadius=int(width/9/2) # 棋盘宽度除以9 （横向最多就放9个棋子, 再除2 就是半径啦）
    minRadius=int(0.8* width/9/2)
    minDist = int(0.8 * width/9)  # 棋子与棋子间距，最小就是2个半径也就是直径。考虑误差，X0.8放宽一下条件
    
    # 检测圆形. 参数的设置很重要。它决定了哪些圆命中出来。参数设置有最小最大半径，以及各圆心间距等
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, minDist, param1=50, param2=30, minRadius=minRadius, maxRadius=maxRadius)
    
    # 绘制圆形
    pieces = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        # print("Total circles", len(circles))
        
        for idx, (x, y, r) in enumerate(circles):  # index 用来后面存图片比对用的
            # 在图像上画圆
            # cv2.circle(img, (x, y), r, (0, 255, 0), 2)

            x1,y1,x2,y2= x-r, y-r, x+r, y+r

            if x1 < 0: x1 = 0  
            if y1 < 0: y1 = 0  
            if x2 >= img.shape[1]: x2 = img.shape[1] - 1  
            if y2 >= img.shape[0]: y2 = img.shape[0] - 1

            # cv2.imwrite(f"chess{idx}.jpg",img[y1:y2,x1:x2]) # 切割棋子保存到本地
            # print(f"slice coordinates ({x1}, {y1}) to ({x2}, {y2}) shape {img[y1:y2+1,x1:x2+1].shape}") 
            color = check_chess_piece_color_v2(img[y1:y2+1,x1:x2+1])
            if color is None:  
                print("Failed to determine color for this slice.")  
            # else:  
                # print(f"Determined color for slice: {color}")
            # print(f"棋子颜色为{idx}: {color}")

            # 根据游戏平台选择对比图片
            platform = ''
            path_str = ''
            with open('./app/json/platform.json', 'r') as file:
                data = json.load(file)
                platform = data["platform"]
            if platform == 'JJ':
                path_str = './app/images/jj'
            else:
                path_str = './app/images/tiantian'
            best_match, best_score = find_best_match(img[y1:y2+1,x1:x2+1], path_str)  
            pieces.append((x, y, r, utils.cut_substring(best_match)))
            # print(f"棋子圆心与半径:({x},{y}), {r},Best match: {utils.cut_substring(best_match)} score {best_score}")

            # show_image('Pieces', img[y1:y2,x1:x2])
    # show_image('Circles',img)
    return pieces

#比较两张图片的特征点,返回相似度
def compare_feature(img1,img2):
    sift=cv2.SIFT_create()
    kp1,des1=sift.detectAndCompute(img1,None)
    kp2,des2=sift.detectAndCompute(img2,None)
    bf=cv2.BFMatcher()
    matches=bf.knnMatch(des1,des2,k=2)
    good=[]
    for m,n in matches:
        if m.distance<0.75*n.distance:
            good.append([m])
    return len(good)

# 判断棋子红色与黑色  (未使用)
def check_chess_piece_color_v2(img):
    if img is None or img.size == 0:  
        print(f"Error: img is None or empty (shape: {img.shape if img is not None else 'None'})")  
        return None  # 或者你可以返回一个表示错误的特殊值或抛出异常  

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  
    if hsv is None or hsv.size == 0:  
        print(f"Error: Failed to convert image to HSV (shape before: {img.shape})")  
        return None  # 同样，返回特殊值或抛出异常 
    
    # 定义多个红色的HSV阈值范围  
    red_ranges = [  
        ([0, 50, 50], [10, 255, 255]),  # 浅红色  
        ([160, 50, 50], [180, 255, 255]),  # 深红色（跨越了180度的边界）  
        ([0, 100, 100], [10, 255, 255])  # 中等红色  
    ]  
  
    # 初始化红色掩码  
    red_mask = np.zeros_like(hsv[:, :, 0])  
  
    # 遍历每个红色范围并更新掩码  
    for lower, upper in red_ranges:  
        lower = np.array(lower, dtype=np.uint8)  
        upper = np.array(upper, dtype=np.uint8)  
        red_mask_temp = cv2.inRange(hsv, lower, upper)  
        red_mask = cv2.bitwise_or(red_mask, red_mask_temp)  
  
    # 假设黑色通过亮度检测（在灰度图中）  
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  
    _, black_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)  # 假设亮度低于50的为黑色  
  
    # 形态学操作去除噪点  
    kernel = np.ones((5, 5), np.uint8)  
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)  
    black_mask = cv2.morphologyEx(black_mask, cv2.MORPH_OPEN, kernel)  
  
    # 计算红色和黑色区域的面积  
    red_area = cv2.countNonZero(red_mask)  
    black_area = cv2.countNonZero(black_mask)  
  
    # 返回颜色判断结果  
    return "red" if red_area > black_area else 'black' 


# 判断棋子红黑
def check_chess_piece_color_v1(img):
    # 将图像从BGR转换到HSV  
    hsv_roi = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  
    hsv_values = hsv_roi.reshape((-1, 3))
    v_min, _ = np.min(hsv_values[:, 2]), np.max(hsv_values[:, 2])
      
    # 通过measure_color_range()函数逐个打印发现低于这个值的为黑色，高于这个值的为红色
    # 临时办法: 不确定是否稳定,以及对其他棋盘图像是否有效   
    threshold = 12   
      
    if v_min > threshold:  
        return "red"  
    else:  
        return "black" 

def find_best_match(img, images_folder):  
    # 首先判断棋子的颜色  
    color = check_chess_piece_color_v2(img)  
      
    # 初始化最高分和最佳匹配  
    best_score = 0  
    best_match = None  
      
    # 遍历images_folder中的所有图片  
    for filename in os.listdir(images_folder):  
        if filename.endswith('.jpg'): 
            # 检查文件名是否与目标棋子颜色匹配  
            if (color == 'red' and filename.startswith('red_')) or (color == 'black' and filename.startswith('black_')):  
                local_img_path = os.path.join(images_folder, filename)  
                local_img = cv2.imread(local_img_path)  
                if local_img is not None:  
                    # 计算两张图片的相似度  
                    score = compare_feature(img, local_img)  
                    # 更新最高分和最佳匹配  
                    if score > best_score:  
                        best_score = score  
                        best_match = filename  
      
    return best_match, best_score

# 计算棋子坐标
def find_nearest_index(point, points):  
    distances = [abs(point - p) for p in points]  # 计算点到所有竖线x坐标的绝对值差异  
    return distances.index(min(distances))  # 返回最接近的竖线的索引 
  
def calculate_pieces_position(x_array, y_array, circles):  
    # 处理circles，计算每个圆心到最近的竖线和横线的索引，并更新pieceArray  
    
    # 初始化pieceArray  
    pieceArray = [["-"] * len(x_array) for _ in range(len(y_array))]  
      
    for cx, cy, radius, name in circles:  
        # 找到最接近的竖线和横线的索引  
        nearest_x_index = find_nearest_index(cx, x_array)  
        nearest_y_index = find_nearest_index(cy, y_array)  
          
        # 可选：检查圆心是否“足够接近”某条竖线或横线（使用半径作为阈值）  
        # 这里我们简单地标记最近的竖线和横线，不考虑阈值  
          
        # 在pieceArray中标记圆心位置  
        # 注意：这里我们假设要在一个“单元格”中标记圆心，即一个特定的(x, y)索引  
        pieceArray[nearest_y_index][nearest_x_index] = name  # 或者使用其他标记方式  
          
        # 如果想要表示圆心的范围（例如，使用半径画圆），则需要更复杂的逻辑  
        # 这通常涉及到在pieceArray中设置多个单元格，可能还需要额外的数据结构或算法  
    
    # 判断本方是红棋还是黑棋
    # 寻找 "K" 的位置以判断是红方还是黑方
    is_red = False
    for row in pieceArray[:3]: # 老将只会在9宫,所以只看前3行
        for cell in row:
            if 'k' in cell:
                is_red = True
                break
        if is_red:
            break

    return pieceArray, is_red   
  
# 测试棋子的HVS范围并打印
# def measure_color_range(roi):  
 
#     # 转换到HSV颜色空间  
#     hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)  
        
#     # 计算并显示颜色范围（这里只是简单地显示所有HSV值）  
#     # 在实际应用中，你可能需要分析这些值来确定合适的范围  
#     hsv_values = hsv_roi.reshape((-1, 3))  # 将图像转换为一维数组，每三个元素为一个HSV值  
        
#     # 打印或分析HSV值  
#     # 例如，你可以找到H、S、V通道的最小值和最大值  
#     h_min, h_max = np.min(hsv_values[:, 0]), np.max(hsv_values[:, 0])  
#     s_min, s_max = np.min(hsv_values[:, 1]), np.max(hsv_values[:, 1])  
#     v_min, v_max = np.min(hsv_values[:, 2]), np.max(hsv_values[:, 2])  
        
#     print(f"H range: {h_min} to {h_max}")  
#     print(f"S range: {s_min} to {s_max}")  
#     print(f"V range: {v_min} to {v_max}")  