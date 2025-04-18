import math
from PIL import Image, ImageDraw
from PyQt6.QtCore import QPointF

def draw_rectangle_magnifier(
    source_image, 
    capture_center, 
    capture_size, 
    magnifier_size, 
    border_color=(255, 0, 0, 255),
    border_width=2
):
    """
    在图像上绘制矩形捕获框，并创建一个放大后的图像
    
    参数:
    source_image: PIL.Image - 源图像
    capture_center: QPointF - 捕获中心点
    capture_size: int - 捕获区域大小
    magnifier_size: int - 放大后的图像大小
    border_color: tuple - 边框颜色 (R, G, B, A)
    border_width: int - 边框宽度
    
    返回:
    tuple: (带有矩形框的图像, 放大后的图像)
    """
    if not isinstance(source_image, Image.Image):
        print("draw_rectangle_magnifier: 无效的源图像")
        return None, None
    
    # 创建源图像的副本
    result_image = source_image.copy()
    draw = ImageDraw.Draw(result_image)
    
    # 获取图像尺寸
    img_width, img_height = source_image.size
    
    # 计算捕获区域
    half_size = capture_size // 2
    left = max(0, int(capture_center.x() - half_size))
    top = max(0, int(capture_center.y() - half_size))
    right = min(img_width - 1, int(capture_center.x() + half_size))
    bottom = min(img_height - 1, int(capture_center.y() + half_size))
    
    # 绘制矩形框
    draw.rectangle(
        [left, top, right, bottom],
        outline=border_color,
        width=border_width
    )
    
    # 裁剪捕获区域
    try:
        captured_area = source_image.crop((left, top, right, bottom))
    except Exception as e:
        print(f"裁剪捕获区域时出错: {e}")
        return result_image, None
    
    # 调整捕获区域大小
    try:
        magnified_image = captured_area.resize(
            (magnifier_size, magnifier_size),
            Image.Resampling.LANCZOS
        )
    except Exception as e:
        print(f"调整捕获区域大小时出错: {e}")
        return result_image, None
    
    return result_image, magnified_image

def create_combined_image(original_image, magnified_image, spacing=10):
    """
    创建原始图像和放大图像的组合图像，放大图像位于原始图像下方
    
    参数:
    original_image: PIL.Image - 原始图像
    magnified_image: PIL.Image - 放大后的图像
    spacing: int - 图像之间的间距
    
    返回:
    PIL.Image - 组合后的图像
    """
    if original_image is None or magnified_image is None:
        return original_image
    
    # 获取图像尺寸
    orig_width, orig_height = original_image.size
    mag_width, mag_height = magnified_image.size
    
    # 计算组合图像的尺寸
    combined_width = orig_width
    combined_height = orig_height + spacing + mag_height
    
    # 创建新图像
    combined_image = Image.new('RGBA', (combined_width, combined_height), (0, 0, 0, 0))
    
    # 粘贴原始图像
    combined_image.paste(original_image, (0, 0))
    
    # 计算放大图像的位置（居中）
    mag_x = (orig_width - mag_width) // 2
    mag_y = orig_height + spacing
    
    # 粘贴放大图像
    combined_image.paste(magnified_image, (mag_x, mag_y))
    
    # 绘制放大图像的边框
    draw = ImageDraw.Draw(combined_image)
    draw.rectangle(
        [mag_x, mag_y, mag_x + mag_width - 1, mag_y + mag_height - 1],
        outline=(255, 255, 255, 255),
        width=2
    )
    
    return combined_image
