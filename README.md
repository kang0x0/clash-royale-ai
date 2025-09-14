# 皇室战争自动化助手
基于Python计算机视觉和ADB的《皇室战争》自动对战助手，通过模拟器，实现自动对战等功能，用于卡牌大师、奖牌获取。
---------------------------------
🏰 Clash Royale Robot - 皇室战争自动对战助手    
[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![ADB Required](https://img.shields.io/badge/ADB-34.0.5+-orange.svg)](https://developer.android.com/studio/releases/platform-tools)


---------------------------------
**🌟 核心功能：**
| 功能模块         | 支持特性                                                                 |
|------------------|-------------------------------------------------------------------------|
| 🤖 自动对战       | 支持单人和双人对战模式，自动匹配、自动释放卡牌                           |
| 🎴 智能卡牌释放   | 随机选择卡牌并在指定区域智能释放                                        |
| 🖥️ 多分辨率适配   | 动态适配 540P 设备                                             |
| 🚨 异常处理       | 误触情况处理                                       |

---------------------------------
**🚀 快速开始：**
****环境要求****
- Windows 10/11 64位
- 雷电模拟器 9.0+ ([下载地址](https://www.ldmnq.com))
- Python 3.9+ ([下载地址](https://www.python.org/downloads/))

**五分钟部署指南**

1. **配置模拟器**
   - 安装雷电模拟器
   
2. **创建新实例**
   - 分辨率: 540x960
   - DPI: 440
   - 开启: USB调试/ROOT权限

3. **安装依赖**
   
    https://dl.google.com/android/repository/platform-tools-latest-windows.zip
   
    unzip platform-tools-latest-windows.zip
   
   将ADB工具添加至系统环境变量
   在终端运行以下命令查看是否成功连接设备
    
    ```bash
    adb devices
    ```
    将连接到的设备名在[config.py]文件内配置

    使用Git克隆本仓库
    ```bash
    git clone https://github.com/kang0x0/clash-royale-ai.git
    cd clash-royale-ai
    pip install -r requirements.txt
    ```

    使用VS code中的conda创建虚拟Python环境

4. **首次运行**
   ```bash
   python robot.py
   ```
---------------------------------
**⚙️ 核心配置：**
**设备配置文件 (config.py)**
**ADB 路径配置**

    adb_path = 'C:/platform-tools/adb.exe'  # ← 修改为实际路径

    
**设备分辨率模式**

    DEVICE_PROFILES = {
        0: {'name': '1080P', 'size': (1080, 2400)},
        1: {'name': '720P',  'size': (720, 1280)},
        2: {'name': '540P',  'size': (960, 540)}
    }

    
**模板管理系统**

    modle/
    ├── Combat.png        # 对战按钮
    ├── Quick_matching.png # 快速匹配按钮
    ├── Battle_Interface.png # 主界面元素
    ├── Battle_Interface2.png 
    ├── Battle_Interface3.png
    ├── confirm.png       # 确认按钮
    ├── confirm2.png
    └── exit.png          # 退出按钮
---------------------------------
**🛠️ 高级使用：**

**截取模拟器图片**

    python capture_screen_utils.py

**测试图像匹配**

    python image_matcher.py

**自定义手势操作**
****在robot.py中调整对战参数****

    def __init__(self, default_threshold=0.75, default_min_scale=0.75, default_max_scale=2.0,
                battle_mode="single", wait_time=10, max_cards=60):
        """
        battle_mode: 对战模式 ("single" 单人模式, "double" 双人模式)
        wait_time: 等待对战开始的时间（秒）
        max_cards: 最大释放卡牌次数
        """

---------------------------------
**🚨 故障排查：**

    Q: ADB设备未连接
    A: adb kill-server && adb start-server
        检查模拟器USB调试开关

    Q: ADB连接不稳定
    A: 1. adb kill-server && adb start-server
       1. 重启模拟器
