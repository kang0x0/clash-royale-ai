# main.py
import os
import glob
from core.adb_manager import capture_screen

def clear_directory(directory):
    """
    清空指定目录中的所有文件。
    """
    files = glob.glob(os.path.join(directory, '*'))
    for f in files:
        os.remove(f)

def main():
    # 创建结果文件夹
    result_dir = 'modle_result'
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    else:
        # 清空结果文件夹
        clear_directory(result_dir)

    # 删除之前的截屏和结果图片
    for file in ['screen.png', 'result.png']:
        if os.path.exists(file):
            os.remove(file)

    # 截取屏幕并保存到当前目录
    print("开始截取模拟器界面...")
    capture_screen()
    
    # 检查截图是否成功保存
    if os.path.exists('screen.png'):
        print("截图已成功保存为 screen.png")
    else:
        print("截图保存失败")

if __name__ == "__main__":
    main()

