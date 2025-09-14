# core/adb_manager.py
import subprocess
import time
import os
from config.settings import adb_path, device_name

def adb_command(command):
    """
    执行ADB命令。
    """
    full_command = f"{adb_path} -s {device_name} {command}"
    print(f"Executing: {full_command}")
    result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ADB command failed: {result.stderr}")
    return result

def capture_screen():
    """
    截取设备屏幕并保存为screen.png。
    """
    adb_command("shell screencap -p /sdcard/screen.png")
    adb_command("pull /sdcard/screen.png .")

# 将adb_swipe_utils.py中的所有函数也移到这个文件中
# 包括swipe_up, swipe_down, swipe_left, swipe_right, pinch_in, pinch_out等函数