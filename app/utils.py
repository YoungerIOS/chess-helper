import numpy as np

# 筛选水平线
def filter_horizontal_lines(lines, img_width):  
    xMin = float('inf')  # 使用正无穷大作为x坐标最小值的初始值  
    xMax = float('-inf') # 使用负无穷大作为x坐标最大值的初始值  
    horizontal_lines = [] 
    for line in lines: 
        for x1, y1, x2, y2 in line:  
            if y1 == y2:  # 水平线  
                # 找出x坐标最小和最大的  
                xMin = min(xMin, min(x1, x2))  
                xMax = max(xMax, max(x1, x2))  
                # 直接将水平线添加到列表中  
                horizontal_lines.append(line) 
    result = keep_middle_lines(horizontal_lines, img_width, 'y') # 有些离的很近的直线 仅保留中间那条
    return result, xMin, xMax 

# 筛选竖直线
def filter_vertical_lines(lines, img_width):  
    yMin = float('inf')  # 使用正无穷大作为初始值  
    yMax = float('-inf') # 使用负无穷大作为初始值  
    vertical_lines = []  
  
    for line in lines:  
        for x1, y1, x2, y2 in line:  
            if x1 == x2:  # 纵线，竖线  
                # 找出纵坐标最小和最大的  
                yMin = min(yMin, min(y1, y2))  
                yMax = max(yMax, max(y1, y2))  
                # 直接将垂直线添加到列表中  
                vertical_lines.append(line)  
    result = keep_middle_lines(vertical_lines, img_width, 'x')
    return result, yMin, yMax

# 相邻很近的多条直线 取中间那条
def keep_middle_lines(lines, img_width, axis='y'):
    sorted_lines = sorted(lines, key=lambda x: x[0][1] if axis == 'y' else x[0][0])  # 按指定轴坐标排序

    square_side = img_width/9 # 棋盘格子边长取: 棋盘宽度/9
    #删除多余的线
    gap = square_side * 0.6 # 取格子宽度的0.6倍
    result_lines = []
    i = 0
    while i < len(sorted_lines):
        start_index = i
        # 找到间距小于 gap 的连续直线组
        while i < len(sorted_lines) - 1 and abs((sorted_lines[i + 1][0][1] if axis == 'y' else sorted_lines[i + 1][0][0]) - (sorted_lines[i][0][1] if axis == 'y' else sorted_lines[i][0][0])) <= gap:
            i += 1
        end_index = i
        if end_index - start_index + 1 > 1:  # 存在相邻且间距小于 gap 的直线组
            middle_index = (start_index + end_index) // 2
            result_lines.append(sorted_lines[middle_index])
        else:  # 单个直线或间距大于 gap 的直线
            result_lines.append(sorted_lines[i])
        i += 1

    # 补充缺少的横线
    if axis == 'y' and len(result_lines) < 10:
        x1, y1, x2, y2 = result_lines[0][0]
        if y1 > square_side:
            result_lines.insert(0, np.array([[x1, y1 - square_side, x2, y2 - square_side]], dtype=np.int32))
        a1, b1, a2, b2 = result_lines[-1][0]
        if b1 < img_width: # 近似认为img_width = 0.9*img_height 
            result_lines.append(np.array([[a1, b1 + square_side, a2, b2 + square_side]], dtype=np.int32))
     
    return result_lines

# 截取棋子图片名称中的字母代号
def cut_substring(string):
    index_ = string.find('_')
    index_dot = string.find('.')
    if index_!= -1 and index_dot!= -1:
        string = string[index_ + 1:index_dot]
        
    return string

# 判断某一方有没有走子
def check_repeat_position(array1, array2, is_red):
    if not array2:
        return True
    
    letter_change = False
    # upper_case_loss = False
    # 检查小写字母位置是否变化,以确定是不是黑棋走了一步
    for i in range(len(array1)):  # 遍历第一个数组的每一行
        for j in range(len(array1[i])):  # 遍历每一行的每一列
            # 检查哪一方
            letter = array1[i][j].islower() if is_red else array1[i][j].isupper()
            if letter and array1[i][j]!= array2[i][j]:  # 如果是小写(大写)字母且在两个数组中的对应位置字符不同
                letter_change = True  # 标记小写(大写)字母位置发生变化
                break  # 一旦发现有变化，就立即停止当前行的检查
        if letter_change:  # 如果在当前行发现了变化
            break  # 停止整个双层循环        
    # # 检查大写字母是否减少
    # upper_case_count1 = sum(1 for row in array1 for item in row if item.isupper())
    # upper_case_count2 = sum(1 for row in array2 for item in row if item.isupper())
    # if upper_case_count1 > upper_case_count2:
    #     upper_case_loss = True

    return letter_change

# 棋子数组转为FEN棋局字符串(不含轮哪方走棋信息)
def switch_to_fen(array, is_red):
    # 本方是黑方就反向遍历
    if not is_red:
        array = [row[::-1] for row in array[::-1]] 

    rows = []  
    for row in array:  
        # 初始化当前行的字符串和连续短横线计数器 
        row_str = []  
        empty_count = 0  

        # 遍历行中的每个元素  
        for cell in row:  
            if cell == '-':  
                # 如果当前是空位，增加连续空位的计数器  
                empty_count += 1 
            else:  
                # 如果是棋子，先处理之前的连续空位  
                if empty_count > 0:  
                    row_str.append(str(empty_count))  
                    empty_count = 0  
                # 添加非空元素  
                row_str.append(cell)  
  
        # 处理行末尾的连续空位  
        if empty_count > 0:  
            row_str.append(str(empty_count))  
  
        # 将当前行的字符串列表转换为单个字符串，并添加到结果列表中  
        rows.append(''.join(row_str))  

    fen_string = "/".join(rows)
    return fen_string, array

# 着法move转文字描述
def convert_move_to_chinese(move, board_array, is_red): 
    # 棋子代码与中文名称的对应关系  
    PIECE_CODES = {  
        'r': '车',  
        'n': '马',  
        'b': '象',  
        'a': '士',  
        'k': '将',  
        'p': '卒',  
        'c': '炮',  
        'R': '车',  
        'N': '马',  
        'B': '相',  
        'A': '士',  
        'K': '帅',  
        'P': '兵',
        'C': '炮',
        '-': '空'
    }  

    CHINESE_NUM = {  
        0: '零',  
        1: '一',  
        2: '二',  
        3: '三',  
        4: '四',  
        5: '五',  
        6: '六',  
        7: '七',  
        8: '八',  
        9: '九'  
    }
  
    # 解析输入字符串，获取起点和终点坐标  
    start_col_char, start_row_str, end_col_char, end_row_str = move[0], move[1:2], move[2:3], move[-1]
 
    start_row = int(start_row_str) 
    end_row = int(end_row_str) 
    start_col = (ord(start_col_char) - ord('a')) 
    end_col = (ord(end_col_char) - ord('a')) 
    # print(f'起始列{start_col}, 起始行{start_row}, 最终列{end_col}, 最终行{end_row}') 
      
    # 从棋局数组中获取棋子类型  
    piece_type = board_array[9 - start_row][start_col]  # 棋子row索引总是从上到下0到9,而引擎纵坐标是9到0
    piece_name = PIECE_CODES[piece_type]  
  
    # 判断移动类型（进、退、平）和构建棋谱描述
    start_colunm = CHINESE_NUM[(9 - start_col)] if is_red else (start_col + 1) 
    end_colunm   = CHINESE_NUM[(9 - end_col)] if is_red else (end_col + 1)
    crossed_row  = CHINESE_NUM[abs(end_row - start_row)] if is_red else abs(end_row - start_row)

    name = piece_name
    # 特殊情况: 如果同一列上有两个相同的棋子(车车,马马,炮炮,兵兵)(同列有2个以上兵的情况暂不考虑)
    if piece_type in ['r', 'R', 'n', 'N', 'c', 'C', 'p', 'P']:
        # 寻找相同棋子,返回首个找到的元素索引
        col_of_board = [row[start_col] for row in board_array]#遍历出要走的棋子所在的列上的所有棋子
        if col_of_board.count(piece_type) > 1: # 某类棋子数量大于1
            if col_of_board.index(piece_type) == 9 - start_row: 
            # 有2个同名棋子, index返回首次找到的,与目标棋子对比可以确定前后关系
                name = "前" if is_red else "后"
            else:
                name = "后" if is_red else "前"
            # 第二个字改为棋子名称
            start_colunm = piece_name

    # 普通情况
    if start_row == end_row:  
        # 平移  
        direction = "平"  
        # 所有棋子在平移时，末尾数字都表示列数  
        desc = f"{name}{start_colunm}{direction}{end_colunm}"  
    else:  
        # 前进或后退 
        action1 = "进" if is_red else "退"
        action2 = "退" if is_red else "进"
        direction = action1 if start_row < end_row else action2

        # 车、炮、卒、将帅 在描述“进” "退" 时，末尾数字是跨越的行数  
        if piece_type in ['r', 'R', 'c', 'C', 'p', 'P', 'k', 'K']:  
            desc = f"{name}{start_colunm}{direction}{crossed_row}"
        else:  
            # 马、象、士在“进” "退" 时，末尾数字是终点所在列数
            desc = f"{name}{(start_colunm)}{direction}{end_colunm}" 

    return desc