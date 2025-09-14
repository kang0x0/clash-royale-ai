# config/settings.py
# ADB配置
adb_path = 'D:/Project/platform-tools-latest-windows/platform-tools/adb.exe'
device_name = "emulator-5554"  # 模拟器的设备名称
device_vm_size = 2  # 1:[720,1280] 0:[1080, 2400]

DEVICE_PROFILES = {
    0: {'name': '1080P', 'size': (1080, 2400)},
    1: {'name': '720P',  'size': (720, 1280)},
    2: {'name': '540P',  'size': (960, 540)}
}