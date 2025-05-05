# Chess Helper - 中国象棋AI助手

一个基于计算机视觉和AI的中国象棋助手，可以帮助你分析棋局并提供最佳走法建议；支持天天象棋和JJ象棋。

## 功能特点

- 🎯 实时棋局识别：通过手机截图自动识别棋盘和棋子位置
- 🤖 AI分析：使用强大的Pikafish引擎进行棋局分析
- 🔄 自动检测：自动识别棋局变化，及时提供建议
- 📱 中文输出：将AI建议转换为易于理解的中文描述
- ⚡ 快速响应：优化算法确保快速准确的识别和分析
- 🎯后续更新：将支持更多设备使用，加入更多强大的象棋引擎

## 技术栈

- Python
- OpenCV - 图像处理和计算机视觉
- Pikafish - 中国象棋AI引擎
- Flask - Web服务框架

## 安装说明

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/chess-helper.git
cd chess-helper
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 确保Pikafish引擎可执行：
   > Pikafish编译及用法可参考：https://github.com/official-pikafish/Pikafish
```bash
chmod +x ./app/Pikafish/src/pikafish
```

4. 运行应用：
```bash
python app/main.py
```

## 使用说明

1. 在iPhone手机上创建快捷指令，添加截图操作
2. 上传截图（可在手机辅助功能中设置悬浮球按钮，触发快捷指令）
3. 系统会自动识别棋局并分析
4. AI计算得出最佳走法，通过快捷指令的通知功能接收走法（例: 兵三进一）

## 项目结构

```
chess-helper/
├── app/
│   ├── main.py          # 主程序入口
│   ├── recognition.py   # 图像识别模块
│   ├── engine.py        # AI引擎接口
│   ├── utils.py         # 工具函数
│   ├── routes.py        # Web路由
│   ├── json/            # 配置文件
│   └── images/          # 图像资源
└── README.md
```

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。在提交PR之前，请确保：

1. 代码符合PEP 8规范
2. 添加必要的测试
3. 更新相关文档

## 许可证

MulanPSL-2.0 license

## 致谢

- Pikafish引擎开发团队
- OpenCV社区
- 所有贡献者 
- VTEXS
- www.vtexs.com