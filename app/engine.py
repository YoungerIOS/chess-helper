import time
import json
import subprocess

def init_engine():
    global pikafish # 全局变量
    # 开辟一个子进程, 运行引擎
    pikafish_command = './app/Pikafish/src/pikafish'
    pikafish = subprocess.Popen(pikafish_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    global parameter
    try:
        with open('./app/json/params.json', 'r') as file:
            data = json.load(file)
        parameter = data
    except FileNotFoundError:
        print('文件未找到')
        parameter = {'current': 'depth', 'value': {'depth': '20', 'movetime': '3000'}}
        save_parameters()

    # 准备
    uci(pikafish) # 可以用全局变量,也可以用传参
    isready()

def save_parameters():
    with open('./app/json/params.json', 'w') as file:
        json.dump(parameter, file)

def get_best_move(fen, side):
    fen_string = fen + ' ' + ('w' if side else 'b')

    lines, best_move = go(fen_string, parameter['current'], parameter['value'][parameter['current']])

    if not lines:  
        best_move = "No output received within 40 seconds. code:408"  # 使用408 Request Timeout作为HTTP状态码  
    else:
        if not best_move:
            best_move = ' '.join(lines)
        else:
            # 截取4个字符
            start_index = best_move.find('bestmove') + len('bestmove') + 1
            best_move = best_move[start_index:start_index + 4]

    return best_move, fen_string

def uci(engine):
    command = 'uci'
    engine.stdin.write(f'{command}\n')    
    engine.stdin.flush() 
    lines = []
    start_time = time.time()
    while True:  
        # 读取一行输出（包括换行符），然后去除换行符  
        output = engine.stdout.readline().strip()  
        if (time.time() - start_time > 1):  # 如果超过1秒，则退出循环  
            break  
        if output:  
            lines.append(output)  # 将非空输出添加到列表中  
            if 'uciok' in output:  # 如果找到 'uciok'，则立即退出循环  
                break  
    return lines

def isready():
    command = 'isready'
    pikafish.stdin.write(f'{command}\n')    
    pikafish.stdin.flush() 
    time.sleep(0.5)
    output = pikafish.stdout.readline().strip()
    return output

def ucinewgame():
    """
    发送ucinewgame之后应该总是发送isready命令,然后等待readyok
    """
    newgame_command = 'ucinewgame\n'
    isready_command = 'isready\n'
    pikafish.stdin.write(newgame_command)
    pikafish.stdin.write(isready_command)
    pikafish.stdin.flush() 
    start_time = time.time()
    while True:  
        output = pikafish.stdout.readline().strip()  
        if (time.time() - start_time > 3):  # 如果超过3秒，则退出循环 
            break  
        if output:  
            if 'readyok' in output:  
                break  
    return output

def go(fen_string, param, value):
    start_position1 = 'rnbakabnr/9/1c5c1/p1p1p1p1p'
    start_position2 = 'P1P1P1P1P/1C5C1/9/RNBAKABNR'
    if start_position1 in fen_string or start_position2 in fen_string:
        ucinewgame()
        pos_command1 = "position startpos\n"
        pikafish.stdin.write(pos_command1)

    pos_command2 = "position fen " + fen_string + "\n"  
    go_command = "go " + param + " " + value + "\n" 
    # 发送命令  
    pikafish.stdin.write(pos_command2)  
    pikafish.stdin.write(go_command)  
    pikafish.stdin.flush() 
    # 读取数据
    lines, best_move = read_output_with_timeout(pikafish, 50)

    return lines, best_move

def read_output_with_timeout(process, timeout=1):  
    lines = []
    best_move = ''
    start_time = time.time()  
    
    while True:  
        # 读取一行输出（包括换行符），然后去除换行符  
        output = process.stdout.readline().strip()  
        # 控制读取时间,超时不再读取 
        if time.time() - start_time > timeout:  
            break
        if output: 
            lines.append(output)
            if "bestmove" in output:
                best_move = output  # 获取包含"bestmove"的输出行
                break
    
    # 返回: 所有输出以及包含bestmove的行            
    return lines, best_move 
