from app.routes import app 
# 入口是哪个文件,就导入哪个文件(文件夹名.入口文件名)

if __name__ == '__main__':
    
    # 启动 Flask 应用，监听 5000 端口
    
    app.run(host='0.0.0.0',port=5000, debug=True)