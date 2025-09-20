# robot.py
import os
import cv2
import time
import random
from core.adb_manager import adb_command, capture_screen
from utils.image_utils import find_template_position, randomize_coordinate

class Robot:
    def __init__(self, default_threshold=0.75, default_min_scale=0.75, default_max_scale=2.0,
                 battle_mode="single", wait_time=10, max_cards=60):
        """
        初始化机器人
        
        Args:
            default_threshold (float): 默认匹配阈值
            default_min_scale (float): 默认最小缩放比例
            default_max_scale (float): 默认最大缩放比例
            battle_mode (str): 对战模式，"single" 为单人模式，"double" 为双人模式，"defense" 为保卫模式
            wait_time (int): 等待对战开始的时间（秒）
            max_cards (int): 最大释放卡牌次数
        """
        self.default_threshold = default_threshold
        self.default_min_scale = default_min_scale
        self.default_max_scale = default_max_scale
        self.battle_mode = battle_mode
        self.wait_time = wait_time
        self.max_cards = max_cards
        self.screenshot_path = "screen.png"
        self.result_dir = "modle_result"
        self.cards_played_in_battle = 0  # 添加这一行，用于统计每场对战释放的卡牌数

        self.battle_count = 1  # 对战次数
        self.start_time = time.time()  # 开始时间
        self.total_cards_played = 0  # 总卡牌释放数
        self.successful_battles = 0  # 成功对战次数
        
        # 定义4个卡牌的位置 (x, y)
        # 这些坐标需要根据实际游戏界面进行调整
        self.card_positions = [
            (170, 890),   # 卡牌1位置
            (266, 890),   # 卡牌2位置
            (373, 890),   # 卡牌3位置
            (476, 890)    # 卡牌4位置
        ]
        
        # 根据不同模式设置不同的放置区域
        self.drop_areas = {
            "single": (51, 458, 495, 594),      # 中间区域
            "double": (51, 458, 495, 594),       # 中间长条区域
            "defense": (246, 570, 296, 607)       # 上方长条区域（保卫模式专用）
        }
        
        # 设置默认放置区域
        self.drop_area = self.drop_areas.get(self.battle_mode, self.drop_areas["single"])

        # 定义卡牌释放的目标区域 (x1, y1, x2, y2)
        # 这是一个矩形区域，卡牌将在该区域内随机释放
        # self.drop_area = (246, 570, 296, 607)  # 中间区域
    
        # self.drop_area = (59, 547, 490, 493) # 中间长条区域

        # self.drop_area = (47, 456, 451, 488) # 上方长条区域

        # self.drop_area = (51, 458, 495, 594) # 上半区域
        # 确保结果目录存在
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
    
    def capture_screen(self):
        """
        截取屏幕截图
        
        Returns:
            bool: 截图是否成功
        """
        try:
            capture_screen()
            return os.path.exists(self.screenshot_path)
        except Exception as e:
            print(f"截图失败: {e}")
            return False
    
    def match_template(self, template_path, screenshot_path=None, threshold=None, 
                       min_scale=None, max_scale=None, save_result=False):
        """
        匹配模板图像
        
        Args:
            template_path (str): 模板图像路径
            screenshot_path (str): 截图路径，默认使用screen.png
            threshold (float): 匹配置信度阈值
            min_scale (float): 最小缩放比例
            max_scale (float): 最大缩放比例
            save_result (bool): 是否保存结果图像
            
        Returns:
            tuple: (x, y, width, height) 如果匹配成功，否则返回None
        """
        if screenshot_path is None:
            screenshot_path = self.screenshot_path
            
        if threshold is None:
            threshold = self.default_threshold
            
        if min_scale is None:
            min_scale = self.default_min_scale
            
        if max_scale is None:
            max_scale = self.default_max_scale
            
        # 检查文件是否存在
        if not os.path.exists(screenshot_path):
            print(f"截图文件不存在: {screenshot_path}")
            return None
            
        if not os.path.exists(template_path):
            print(f"模板文件不存在: {template_path}")
            return None
        
        try:
            # 调用图像匹配函数
            result = find_template_position(
                large_image_path=screenshot_path,
                template_image_path=template_path,
                threshold=threshold,
                min_scale=min_scale,
                max_scale=max_scale
            )
            
            if result and save_result:
                # 读取截图并在上面绘制匹配结果
                screenshot = cv2.imread(screenshot_path)
                if screenshot is not None:
                    x, y, w, h = result
                    cv2.rectangle(screenshot, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    # 保存结果图像
                    template_name = os.path.splitext(os.path.basename(template_path))[0]
                    result_path = os.path.join(self.result_dir, f"{template_name}_result.png")
                    cv2.imwrite(result_path, screenshot)
                    print(f"结果图像已保存到: {result_path}")
            
            return result
        except Exception as e:
            print(f"匹配模板时出错: {e}")
            return None
    
    def click_position(self, x, y, radius=5, delay_before=0, delay_after=0, click_count=1):
        """
        点击指定位置
        
        Args:
            x (int): x坐标
            y (int): y坐标
            radius (int): 随机偏移半径
            delay_before (float): 点击前延迟（秒）
            delay_after (float): 点击后延迟（秒）
            click_count (int): 点击次数
            
        Returns:
            bool: 点击是否成功
        """
        try:
            if delay_before > 0:
                time.sleep(delay_before)
            
            # 添加随机偏移避免机器人检测
            click_x, click_y = randomize_coordinate(x, y, radius)
            
            # 执行点击操作
            for i in range(click_count):
                adb_command(f"shell input tap {click_x} {click_y}")
                print(f"点击位置: ({click_x}, {click_y}) 第{i+1}次")
                if i < click_count - 1:  # 如果不是最后一次点击，则添加小延迟
                    time.sleep(delay_after)
            
            if delay_after > 0:
                time.sleep(delay_after)
                
            return True
        except Exception as e:
            print(f"点击操作失败: {e}")
            return False
    
    def click_template(self, template_path, offset_x=0, offset_y=0, radius=5,
                       threshold=None, min_scale=None, max_scale=None,
                       delay_before=0, delay_after=0, retry_count=1, click_count=1,
                       need_capture=True):
        """
        匹配模板并点击其中心位置
        
        Args:
            template_path (str): 模板图像路径
            offset_x (int): x坐标偏移量
            offset_y (int): y坐标偏移量
            radius (int): 随机偏移半径
            threshold (float): 匹配置信度阈值
            min_scale (float): 最小缩放比例
            max_scale (float): 最大缩放比例
            delay_before (float): 点击前延迟（秒）
            delay_after (float): 点击后延迟（秒）
            retry_count (int): 重试次数
            click_count (int): 点击次数
            need_capture (bool): 是否需要重新截图，默认为True
            
        Returns:
            bool: 是否成功匹配并点击
        """
        for attempt in range(retry_count):
            if attempt > 0:
                print(f"重试第 {attempt + 1} 次...")
                time.sleep(1)
            
            # 根据need_capture参数决定是否截取屏幕
            if need_capture and not self.capture_screen():
                continue
            
            # 匹配模板
            result = self.match_template(
                template_path=template_path,
                threshold=threshold,
                min_scale=min_scale,
                max_scale=max_scale
            )
            
            if result:
                x, y, w, h = result
                # 计算中心点并应用偏移
                center_x = x + w // 2 + offset_x
                center_y = y + h // 2 + offset_y
                
                # 执行点击
                return self.click_position(
                    center_x, center_y, radius,
                    delay_before, delay_after, click_count
                )
        
        print(f"无法匹配模板: {template_path}")
        return False
    
    def select_random_card(self):
        """
        随机选择一张卡牌
        
        Returns:
            tuple: (x, y) 选中卡牌的位置
        """
        selected_card = random.choice(self.card_positions)
        print(f"随机选择卡牌位置: {selected_card}")
        return selected_card
    
    def get_random_drop_position(self):
        """
        在指定区域内获取随机释放位置
        
        Returns:
            tuple: (x, y) 随机释放位置
        """
        x1, y1, x2, y2 = self.drop_area
        drop_x = random.randint(x1, x2)
        drop_y = random.randint(y1, y2)
        print(f"随机释放位置: ({drop_x}, {drop_y})")
        return drop_x, drop_y
    
    def play_random_card(self, card_radius=2, drop_radius=5):
        """
        随机选择一张卡牌并在指定区域释放
        
        Args:
            card_radius (int): 卡牌点击位置的随机偏移半径
            drop_radius (int): 释放位置的随机偏移半径
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 随机选择一张卡牌
            card_x, card_y = self.select_random_card()
            
            # 点击选中的卡牌
            if not self.click_position(card_x, card_y, radius=card_radius, delay_after=0.5):
                print("点击卡牌失败")
                return False
            
            # 在指定区域获取随机释放位置
            drop_x, drop_y = self.get_random_drop_position()
            
            # 点击释放位置
            if not self.click_position(drop_x, drop_y, radius=card_radius):
                print("释放卡牌失败")
                return False
            
            print(f"成功释放卡牌: 从位置({card_x}, {card_y})到位置({drop_x}, {drop_y})")
            return True
        except Exception as e:
            print(f"释放卡牌时出错: {e}")
            return False
        
    def wait_for_battle_start(self):
        """
        等待对战开始
            
        Returns:
            bool: 是否等待成功
        """
        print(f"等待 {self.wait_time} 秒让对战开始...")
        time.sleep(self.wait_time)
        return True
    
    def check_battle_end(self):
        """
        检查对战是否结束
          
        Returns:
            bool: 对战是否结束
        """
        print("检查对战是否结束...")
        
        # 根据模式选择不同的结束按钮
        if self.battle_mode == "double":
            # 双人模式检查是否有exit按钮
            result = self.click_template("modle/exit.png") or self.click_template("modle/confirm2.png", need_capture=False)
        else:
            # 单人模式检查是否有确认按钮
            result = self.click_template("modle/confirm.png")
        
        return result
    
    def battle_loop(self, check_end_after=5):
        """
        对战主循环
        
        Args:
            check_end_after (int): 在释放多少张卡牌后开始检查对战结束
            
        Returns:
            bool: 对战是否成功完成
        """
        print("开始对战循环...")
        self.cards_played_in_battle = 0  # 重置计数器
        
        for i in range(self.max_cards):

            # 在指定次数后开始检查对战是否结束
            if i >= check_end_after:
                # 检查是否出现确认按钮（对战结束标志）
                if self.check_battle_end():
                    if self.battle_mode == "double":
                        print("检测到exit按钮，双人对战已结束")
                    else:
                        print("检测到确认按钮，对战已结束")
                    return True
            
            print(f"释放第 {i+1} 张卡牌")
            
            # 释放随机卡牌
            if not self.play_random_card():
                print("释放卡牌失败")
                continue

            self.cards_played_in_battle = i + 1  # 更新已释放卡牌数
            
            # 卡牌释放间隔
            if self.battle_mode == "double":
                time.sleep(6)
            elif self.battle_mode == "defense":
                # 保卫模式使用固定较短的间隔时间
                time.sleep(2)
            else:
                # 单人模式使用1-10秒的正态分布随机等待时间
                # 使用均值为5.5，标准差为1.5的正态分布，然后限制在1-10范围内
                wait_time = max(1, min(10, int(random.normalvariate(4, 1.5))))
                print(f"单人模式等待 {wait_time} 秒")
                time.sleep(wait_time)
            
        
        print(f"已释放 {self.max_cards} 张卡牌，对战循环结束")
        return True

    def auto_battle(self, check_end_after=5):
        """
        自动对战流程
        
        Args:
            check_end_after (int): 在释放多少张卡牌后开始检查对战结束
        
        Returns:
            bool: 是否成功完成整个对战流程
        """
        print("开始自动对战流程...")
        
        # 点击对战按钮
        if not self.click_template("modle/Combat.png"):
            print("无法点击对战按钮")
            return False
        
        print("已点击对战按钮")

        # 如果是双人模式，需要匹配并点击快速匹配按钮
        if self.battle_mode == "double":
            print("双人模式：正在寻找快速匹配按钮...")
            if not self.click_template("modle/Quick_matching.png"):
                print("无法找到或点击快速匹配按钮")
                return False
            print("已点击快速匹配按钮")
            # 等待匹配界面稳定
            time.sleep(2)
        
        # 等待对战开始
        if not self.wait_for_battle_start():
            print("等待对战开始失败")
            return False
        
        # 进入对战循环
        battle_ended = self.battle_loop(check_end_after)
        
        if battle_ended:
            print("对战已结束，准备开始新的对战...")
            # 等待一下确保界面稳定
            time.sleep(3)
            return True
        else:
            print("对战循环完成")
            return True
        
    def switch_deck(self, deck_index):
        """
        切换到指定索引的卡组
        假设5个卡组的位置是固定的像素坐标
        
        Args:
            deck_index (int): 卡组索引 (0-4)
        """

        # 定义5个卡组的位置坐标 (x, y)
        # 这些坐标需要根据实际游戏界面进行调整
        deck_positions = [
            (105, 143),  # 卡组1位置
            (172, 143),  # 卡组2位置
            (238, 143),  # 卡组3位置
            (303, 143),  # 卡组4位置
            (369, 143)   # 卡组5位置
        ]
        
        if deck_index < 0 or deck_index >= len(deck_positions):
            print(f"无效的卡组索引: {deck_index}，应为0-4之间")
            return False
        
        # 获取目标卡组位置
        x, y = deck_positions[deck_index]
        print(f"切换到卡组 {deck_index + 1}，位置: ({x}, {y})")
        

        # 点击卡组位置
        return self.click_position(x, y, radius=2, delay_after=2)
    
    def auto_battle_with_deck_switch(self, battles_per_deck=3, check_end_after=5):
        """
        带卡组切换功能的自动对战流程
        
        Args:
            battles_per_deck (int): 每个卡组对战次数
            check_end_after (int): 在释放多少张卡牌后开始检查对战结束
        
        Returns:
            bool: 是否成功完成整个对战流程
        """
        print("开始带卡组切换功能的自动对战流程...")
        
        # 初始化卡组索引和对战计数器
        current_deck_index = 0
        battles_with_current_deck = 0
        
        # 主循环
        try:
            while True:
                # 检查是否需要切换卡组
                if battles_with_current_deck >= battles_per_deck:
                    print(f"当前卡组已对战 {battles_with_current_deck} 次，需要切换卡组")
                    
                    # 进入卡组选择界面的步骤
                    # 1. 点击卡组按钮 (假设在某个固定位置)
                    self.click_position(129, 750, radius=2, delay_after=2.0)  # 假设卡组按钮位置
                    
                    time.sleep(2)  # 等待界面切换
                    
                    # 2. 切换到下一个卡组
                    current_deck_index = (current_deck_index + 1) % 5  # 循环切换卡组
                    if not self.switch_deck(current_deck_index):
                        print(f"切换到卡组 {current_deck_index + 1} 失败")
                        return False
                    
                    time.sleep(2)  # 等待卡组切换
                    
                    # 3. 点击确认或返回按钮 (假设在某个固定位置)
                    self.click_position(270, 73, radius=2, delay_after=3.0)  # 假设确认按钮位置
                    
                    # 重置对战计数器
                    battles_with_current_deck = 0
                
                print(f"\n{'='*50}")
                print(f"使用卡组 {current_deck_index + 1} 开始第 {battles_with_current_deck + 1} 次对战")
                print(f"{'='*50}")
                
                if self.battle_mode == "single":
                    # 点击主界面
                    self.click_template("modle/Battle_Interface3.png")
                    time.sleep(3)

                # 计算动态 check_end_after 值（基于历史平均值）
                if self.successful_battles > 0:
                    avg_cards = self.total_cards_played / self.successful_battles
                    check_end_after = max(5, int(avg_cards * 0.7))  # 使用平均值的70%作为检查点
                    print(f"基于历史数据，check_end_after 设置为: {check_end_after}")
                else:
                    check_end_after = 10  # 默认值

                if self.auto_battle(check_end_after=check_end_after):
                    self.battle_count += 1
                    self.successful_battles += 1
                    self.total_cards_played += self.cards_played_in_battle  # 紫色累加卡牌数
                    battles_with_current_deck += 1
                    avg_cards = self.total_cards_played / self.successful_battles
                    print(f"完成一次对战，本次释放 {self.cards_played_in_battle} 张卡牌")
                    print(f"平均释放卡牌数: {avg_cards:.2f}")
                    print("8秒后开始新的对战...")
                    time.sleep(8)
                else:
                    print("对战失败，尝试返回主界面...")
                    # 对战按钮识别失败后，识别并点击Battle_Interface图像返回主界面
                    if self.click_template("modle/Battle_Interface.png"):
                        print("已点击Battle_Interface图像，返回主界面")
                        continue
                    
                    if self.click_template("modle/Battle_Interface2.png", need_capture=False):
                        print("已点击Battle_Interface2图像，返回主界面")  
                        continue
                    
                    if self.click_template("modle/Reward.png", delay_after=4, click_count=6, need_capture=False):
                        print("已点击Reward图像，返回主界面")
                        continue

                    if self.click_template("modle/Return_to_game.png", delay_after=4, need_capture=False):
                        print("已点击Return_to_game图像，返回主界面")
                        continue

                    if self.click_template("modle/close.png", need_capture=False):
                        print("已点击close图像，返回主界面")
                        continue

                    if self.click_template("modle/confirm2.png", need_capture=False):
                        print("已点击confirm2图像，返回主界面")
                        continue
                    else:
                        break  # 如果都无法返回主界面，则退出循环

            return True
        except KeyboardInterrupt:
            print("程序已手动终止")
            return False

# 使用示例
if __name__ == "__main__":


    # 设置对战模式，"single" 为单人模式，"double" 为双人模式，"defense" 为保卫模式
    battle_mode = "defense"  # 可以根据需要修改为 "single"、"double" 或 "defense"
    
    # 根据模式设置不同的参数
    if battle_mode == "double":
        wait_time = 20
        max_cards = 60
    elif battle_mode == "defense":
        wait_time = 10
        max_cards = 60
    else:  # single mode
        wait_time = 10
        max_cards = 60

    # 创建机器人实例
    robot = Robot(battle_mode=battle_mode, wait_time=wait_time, max_cards=max_cards)

    # 添加统计信息初始化
    robot.battle_count = 1  # 对战次数
    robot.start_time = time.time()  # 开始时间
    robot.total_cards_played = 0  # 总卡牌释放数
    robot.successful_battles = 0  # 成功对战次数

    # 自动对战循环（带卡组切换功能）
    try:
        # 每个卡组对战3次后切换
        robot.auto_battle_with_deck_switch(battles_per_deck=1000)
    except KeyboardInterrupt:
        print("程序已手动终止")
    finally:
        # 输出最终统计信息
        elapsed_time = time.time() - robot.start_time
        avg_cards_final = robot.total_cards_played / robot.successful_battles if robot.successful_battles > 0 else 0
        print(f"\n{'='*50}")
        print(f"程序运行结束，最终统计信息:")
        print(f"总对战次数: {robot.battle_count}")
        print(f"成功对战次数: {robot.successful_battles}")
        print(f"总卡牌释放数: {robot.total_cards_played}")
        print(f"平均每次对战释放卡牌数: {avg_cards_final:.2f}")
        print(f"总运行时间: {int(elapsed_time//3600)}小时 {int((elapsed_time%3600)//60)}分钟 {int(elapsed_time%60)}秒")
        print(f"{'='*50}")

    pass