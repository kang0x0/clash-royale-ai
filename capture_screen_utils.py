# capture_screen_utils.py
import os
from core.adb_manager import capture_screen

def capture_emulator_screen():
    """
    截取当前模拟器界面并保存为screen.png
    
    Returns:
        bool: 截图是否成功
    """
    try:
        # 删除之前的截图
        if os.path.exists('screen.png'):
            os.remove('screen.png')
        
        # 截取屏幕并保存到当前目录
        print("开始截取模拟器界面...")
        capture_screen()
        
        # 检查截图是否成功保存
        if os.path.exists('screen.png'):
            print("截图已成功保存为 screen.png")
            return True
        else:
            print("截图保存失败")
            return False
    except Exception as e:
        print(f"截图过程中发生错误: {e}")
        return False

# 示例调用
if __name__ == "__main__":
    capture_emulator_screen()