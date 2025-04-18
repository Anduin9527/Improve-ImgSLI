import math
from PIL import Image, ImageDraw
from PyQt6.QtCore import QPointF, QRectF

# 放大图像位置枚举
POSITION_TOP_LEFT = 0
POSITION_TOP_RIGHT = 1
POSITION_BOTTOM_LEFT = 2
POSITION_BOTTOM_RIGHT = 3

# 位置名称映射
POSITION_NAMES = {
    POSITION_TOP_LEFT: "左上角",
    POSITION_TOP_RIGHT: "右上角",
    POSITION_BOTTOM_LEFT: "左下角",
    POSITION_BOTTOM_RIGHT: "右下角"
}

def draw_stretchable_rectangle_magnifier(
    source_image,
    rect,
    magnifier_size,
    border_color=(255, 0, 0, 255),
    border_width=2
):
    """
    在图像上绘制可拉伸的矩形捕获框，并创建一个放大后的图像

    参数:
    source_image: PIL.Image - 源图像
    rect: QRectF - 捕获矩形区域
    magnifier_size: int - 放大后的图像大小
    border_color: tuple - 边框颜色 (R, G, B, A)
    border_width: int - 边框宽度

    返回:
    tuple: (带有矩形框的图像, 放大后的图像)
    """
    if not isinstance(source_image, Image.Image):
        print("draw_stretchable_rectangle_magnifier: 无效的源图像")
        return None, None

    # 创建源图像的副本
    result_image = source_image.copy()
    draw = ImageDraw.Draw(result_image)

    # 获取图像尺寸
    img_width, img_height = source_image.size

    # 计算捕获区域（确保在图像范围内）
    left = max(0, int(rect.left()))
    top = max(0, int(rect.top()))
    right = min(img_width - 1, int(rect.right()))
    bottom = min(img_height - 1, int(rect.bottom()))

    # 确保矩形有效（宽高大于0）
    if right <= left or bottom <= top:
        return result_image, None

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
        # 保持宽高比
        capture_width = right - left
        capture_height = bottom - top
        aspect_ratio = capture_width / capture_height

        if aspect_ratio > 1:
            # 宽大于高
            mag_width = magnifier_size
            mag_height = int(magnifier_size / aspect_ratio)
        else:
            # 高大于宽
            mag_height = magnifier_size
            mag_width = int(magnifier_size * aspect_ratio)

        magnified_image = captured_area.resize(
            (mag_width, mag_height),
            Image.Resampling.LANCZOS
        )
    except Exception as e:
        print(f"调整捕获区域大小时出错: {e}")
        return result_image, None

    return result_image, magnified_image

def create_corner_image(
    original_image,
    magnified_image,
    position=POSITION_TOP_LEFT,
    spacing=10,
    border_color=(255, 0, 0, 255),
    border_width=2
):
    """
    创建原始图像和放大图像的组合图像，放大图像位于原始图像的指定角落

    参数:
    original_image: PIL.Image - 原始图像
    magnified_image: PIL.Image - 放大后的图像
    position: int - 放大图像的位置（0:左上, 1:右上, 2:左下, 3:右下）
    spacing: int - 图像边缘的间距
    border_color: tuple - 边框颜色 (R, G, B, A)
    border_width: int - 边框宽度

    返回:
    PIL.Image - 组合后的图像
    """
    if original_image is None or magnified_image is None:
        return original_image

    # 获取图像尺寸
    orig_width, orig_height = original_image.size
    mag_width, mag_height = magnified_image.size

    # 创建新图像（与原图大小相同）
    combined_image = original_image.copy()

    # 计算放大图像的位置，紧贴图片边缘
    if position == POSITION_TOP_LEFT:
        mag_x = 0
        mag_y = 0
    elif position == POSITION_TOP_RIGHT:
        mag_x = orig_width - mag_width
        mag_y = 0
    elif position == POSITION_BOTTOM_LEFT:
        mag_x = 0
        mag_y = orig_height - mag_height
    elif position == POSITION_BOTTOM_RIGHT:
        mag_x = orig_width - mag_width
        mag_y = orig_height - mag_height
    else:
        # 默认左上角
        mag_x = 0
        mag_y = 0

    # 粘贴放大图像
    combined_image.paste(magnified_image, (mag_x, mag_y))

    # 绘制放大图像的边框
    draw = ImageDraw.Draw(combined_image)
    draw.rectangle(
        [mag_x, mag_y, mag_x + mag_width - 1, mag_y + mag_height - 1],
        outline=border_color,
        width=border_width
    )

    return combined_image
