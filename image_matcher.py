# image_matcher.py
import os
import cv2
import numpy as np
from utils.image_utils import find_template_position

def setup_result_directory():
    """
    创建结果文件夹（如果不存在）
    """
    result_dir = 'modle_result'
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    return result_dir

def match_images(source_image_path, template_image_path, result_save_name=None, 
                 threshold=0.75, min_scale=0.75, max_scale=2.0):
    """
    通用图像匹配函数，用于测试目标图像和源图像的匹配情况
    
    Args:
        source_image_path (str): 源图像路径（大图）
        template_image_path (str): 模板图像路径（小图）
        result_save_name (str): 结果图像保存名称，如果为None则自动生成
        threshold (float): 匹配置信度阈值
        min_scale (float): 最小缩放比例
        max_scale (float): 最大缩放比例
    
    Returns:
        dict: 匹配结果字典，包含位置信息和匹配状态
    """
    # 检查源图像和模板图像是否存在
    if not os.path.exists(source_image_path):
        print(f"错误：源图像 {source_image_path} 不存在")
        return {"success": False, "error": "源图像不存在"}
    
    if not os.path.exists(template_image_path):
        print(f"错误：模板图像 {template_image_path} 不存在")
        return {"success": False, "error": "模板图像不存在"}
    
    # 创建结果目录
    setup_result_directory()
    
    # 获取模板文件名（不含路径和扩展名）
    template_name = os.path.splitext(os.path.basename(template_image_path))[0]
    
    # 如果没有指定结果保存名称，则自动生成
    if result_save_name is None:
        result_save_name = f"{template_name}_result.png"
    
    result_path = os.path.join('modle_result', result_save_name)
    
    print(f"正在匹配模板 '{template_name}'...")
    print(f"源图像: {source_image_path}")
    print(f"模板图像: {template_image_path}")
    
    try:
        # 调用图像匹配函数
        result = find_template_position(
            large_image_path=source_image_path,
            template_image_path=template_image_path,
            output_path=result_path,
            threshold=threshold,
            min_scale=min_scale,
            max_scale=max_scale
        )
        
        # 读取源图像用于绘制结果
        source_image = cv2.imread(source_image_path)
        if source_image is None:
            print("无法读取源图像")
            return {"success": False, "error": "无法读取源图像"}
        
        if result:
            x, y, w, h = result
            print(f"匹配成功！位置: ({x}, {y}), 宽度: {w}, 高度: {h}")
            
            # 在源图像上绘制矩形框
            cv2.rectangle(source_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 保存结果图像
            cv2.imwrite(result_path, source_image)
            print(f"结果图像已保存到: {result_path}")
            
            return {
                "success": True,
                "position": (x, y),
                "size": (w, h),
                "result_path": result_path
            }
        else:
            print("未找到匹配")
            return {"success": False, "error": "未找到匹配"}
            
    except Exception as e:
        print(f"匹配过程中发生错误: {e}")
        return {"success": False, "error": str(e)}

def batch_match_images(source_image_path, template_paths, threshold=0.75, 
                       min_scale=0.75, max_scale=2.0):
    """
    批量匹配多个模板图像
    
    Args:
        source_image_path (str): 源图像路径
        template_paths (list): 模板图像路径列表
        threshold (float): 匹配置信度阈值
        min_scale (float): 最小缩放比例
        max_scale (float): 最大缩放比例
    
    Returns:
        dict: 所有匹配结果的字典
    """
    results = {}
    
    print(f"开始批量匹配，源图像: {source_image_path}")
    print(f"模板数量: {len(template_paths)}")
    
    for i, template_path in enumerate(template_paths):
        print(f"\n--- 处理第 {i+1}/{len(template_paths)} 个模板 ---")
        
        # 生成结果保存名称
        template_name = os.path.splitext(os.path.basename(template_path))[0]
        result_name = f"{template_name}_result.png"
        
        # 执行匹配
        result = match_images(
            source_image_path=source_image_path,
            template_image_path=template_path,
            result_save_name=result_name,
            threshold=threshold,
            min_scale=min_scale,
            max_scale=max_scale
        )
        
        results[template_name] = result
    
    # 输出摘要
    print("\n=== 匹配结果摘要 ===")
    for template_name, result in results.items():
        status = "成功" if result["success"] else "失败"
        print(f"{template_name}: {status}")
        if result["success"]:
            pos = result["position"]
            size = result["size"]
            print(f"  位置: ({pos[0]}, {pos[1]}), 大小: {size[0]}x{size[1]}")
    
    return results

# 示例用法
if __name__ == "__main__":
    # 单个图像匹配示例
    result = match_images(
        source_image_path="screen.png",
        template_image_path="modle/Combat.png"
    )
    
    # 批量图像匹配示例
    # template_list = [
    #     "modle/attack.png",
    #     "modle/look_for_rivals.png",
    #     "modle/search_now.png"
    # ]
    # results = batch_match_images("screen.png", template_list)
    pass