from. import recognition
from. import utils
from. import engine
from. import routes

last_position = None

def main(img_path, param):  
    # 棋局图像  
    # img_path = './app/uploads/图像.jpeg' 

    # 预处理 : 把共同的图像处理操作抽出来,当前只有灰度化是共用的
    image, gray = recognition.pre_processing_image(img_path)

    # 识别棋盘
    x_array, y_array = recognition.board_recognition(image, gray)

    # 识别棋子 
    pieces = recognition.pieces_recognition(image, gray, param)

    # 棋子位置
    position, is_red = recognition.calculate_pieces_position(x_array, y_array, pieces) # 按原始位置排列的二维数组

    # 检查局面是否变化
    global last_position
    if param['autoModel'] == 'true':
        if utils.check_repeat_position(position, last_position, is_red):
            return 'repeat'
    last_position = position

    # 转成 FEN字符串
    fen_str, board_array = utils.switch_to_fen(position, is_red)
    for i, row in enumerate(board_array):  
        print(row)

    # 向引擎发送命令
    move, fen = engine.get_best_move(fen_str, is_red, param)
    print(f'{fen}\n{move}')

    # 发送通知
    info = utils.convert_move_to_chinese(move, board_array, is_red)
    # routes.bark_notification(info)
    return info


    
  