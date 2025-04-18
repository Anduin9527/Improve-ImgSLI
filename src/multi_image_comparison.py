import os
import math
import traceback
from typing import List, Tuple, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtCore import Qt, QSize, QPointF, QTimer, pyqtSignal, QRectF
from PyQt6.QtGui import QIcon, QPixmap, QImage, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy,
    QFileDialog, QMessageBox, QComboBox, QSlider, QCheckBox,
    QGridLayout, QScrollArea, QColorDialog
)

from qfluentwidgets import (
    PushButton, TransparentPushButton, Slider, ComboBox,
    CheckBox, FluentIcon, ToolButton, SpinBox, ScrollArea, LineEdit
)

from translations import tr
from image_processing_rect import draw_rectangle_magnifier
from image_processing_rect_stretch import draw_stretchable_rectangle_magnifier, create_corner_image, POSITION_TOP_LEFT, POSITION_TOP_RIGHT, POSITION_BOTTOM_LEFT, POSITION_BOTTOM_RIGHT, POSITION_NAMES

class ClickableImageLabel(QLabel):
    """可点击的图像标签，用于处理鼠标事件"""
    clicked = pyqtSignal(object)  # 鼠标点击信号
    moved = pyqtSignal(object)    # 鼠标移动信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        self.clicked.emit(event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.moved.emit(event)
        super().mouseMoveEvent(event)

class MultiImageComparisonApp(QWidget):
    """多图对比应用"""

    def __init__(self):
        super().__init__()

        # 设置窗口属性
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        # 初始化状态变量
        self._init_state()

        # 构建UI
        self._build_ui()

        # 连接信号
        self._connect_signals()

    def _init_state(self):
        """初始化状态变量"""
        # 图像列表
        self.images: List[Image.Image] = []
        self.image_paths: List[str] = []

        # 显示设置
        self.rows = 2
        self.cols = 2
        self.use_magnifier = True
        self.magnifier_size_relative = 0.2  # 相对于图像尺寸的放大镜大小
        self.capture_size_relative = 0.1    # 相对于图像尺寸的捕获区域大小

        # 捕获位置 (相对坐标 0.0-1.0)
        self.capture_position_relative = QPointF(0.5, 0.5)

        # 放大镜状态
        self._is_dragging_capture_point = False
        self._is_resizing_capture_rect = False
        self._resize_handle_size = 10  # 调整大小手柄的尺寸（像素）
        self._active_resize_handle = None  # 当前活动的调整大小手柄

        # 可拉伸矩形框
        self.use_stretchable_rect = True  # 是否使用可拉伸矩形框
        self.capture_rect_relative = QRectF(0.45, 0.45, 0.1, 0.1)  # 相对矩形框（左上角x, y, 宽度, 高度）

        # 固定捕获区域大小
        self.fixed_magnifier_size = False  # 是否固定捕获区域大小

        # 放大内容显示位置
        self.magnifier_position = POSITION_TOP_RIGHT  # 默认右上角

        # 边框颜色
        self.border_color = (255, 0, 0, 255)  # 红色
        self.border_width = 2

        # 文字设置
        self.show_text = False  # 是否显示文字信息
        self.text_color = (255, 255, 255, 255)  # 白色
        self.font_size = 20  # 字体大小
        self.image_texts = []  # 每张图的文字信息

    def _build_ui(self):
        """构建用户界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        # 顶部控制区域
        main_layout.addLayout(self._create_control_layout())

        # 图像显示区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setSpacing(4)
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area, 1)  # 1表示拉伸因子

        # 底部状态区域
        self.status_label = QLabel("准备就绪")
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def _create_control_layout(self):
        """创建控制区域布局"""
        control_layout = QVBoxLayout()
        control_layout.setSpacing(8)

        # 第一行：导入和导出按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        # 导入按钮
        self.btn_import = PushButton(tr("导入图片"))
        self.btn_import.setIcon(FluentIcon.PHOTO.icon())
        self.btn_import.setMinimumWidth(120)
        button_layout.addWidget(self.btn_import)

        # 清除按钮
        self.btn_clear = PushButton(tr("清除所有"))
        self.btn_clear.setIcon(FluentIcon.DELETE.icon())
        self.btn_clear.setMinimumWidth(120)
        button_layout.addWidget(self.btn_clear)

        # 导出按钮
        self.btn_export = PushButton(tr("导出图中图"))
        self.btn_export.setIcon(FluentIcon.SAVE.icon())
        self.btn_export.setMinimumWidth(120)
        button_layout.addWidget(self.btn_export)

        # 导出原图按钮
        self.btn_export_original = PushButton(tr("导出原图"))
        self.btn_export_original.setIcon(FluentIcon.SAVE.icon())
        self.btn_export_original.setMinimumWidth(120)
        button_layout.addWidget(self.btn_export_original)

        # 添加弹性空间
        button_layout.addStretch(1)

        # 帮助按钮
        self.btn_help = TransparentPushButton()
        self.btn_help.setIcon(FluentIcon.HELP.icon())
        self.btn_help.setIconSize(QSize(24, 24))
        self.btn_help.setFixedSize(36, 36)
        self.btn_help.setToolTip(tr("查看帮助"))
        button_layout.addWidget(self.btn_help)

        button_layout.addStretch(1)

        # 第二行：布局控制
        layout_control = QHBoxLayout()
        layout_control.setSpacing(10)

        # 行数控制
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel(tr("行数:")))
        self.spin_rows = SpinBox()
        self.spin_rows.setRange(1, 10)
        self.spin_rows.setValue(self.rows)
        row_layout.addWidget(self.spin_rows)
        layout_control.addLayout(row_layout)

        # 列数控制
        col_layout = QHBoxLayout()
        col_layout.addWidget(QLabel(tr("列数:")))
        self.spin_cols = SpinBox()
        self.spin_cols.setRange(1, 10)
        self.spin_cols.setValue(self.cols)
        col_layout.addWidget(self.spin_cols)
        layout_control.addLayout(col_layout)

        # 放大镜控制
        self.checkbox_magnifier = CheckBox(tr("启用放大镜"))
        self.checkbox_magnifier.setChecked(self.use_magnifier)
        self.checkbox_magnifier.setMinimumWidth(130)
        self.checkbox_magnifier.setIcon(FluentIcon.ZOOM.icon())
        layout_control.addWidget(self.checkbox_magnifier)

        # 固定捕获区域大小控制
        self.checkbox_fixed_size = CheckBox(tr("固定当前捕获区域大小"))
        self.checkbox_fixed_size.setChecked(self.fixed_magnifier_size)
        self.checkbox_fixed_size.setMinimumWidth(180)
        self.checkbox_fixed_size.setIcon(FluentIcon.PIN.icon())
        layout_control.addWidget(self.checkbox_fixed_size)

        layout_control.addStretch(1)

        # 第三行：放大镜设置
        magnifier_layout = QHBoxLayout()
        magnifier_layout.setSpacing(15)

        # 放大镜大小
        magnifier_size_layout = QHBoxLayout()
        magnifier_size_layout.setSpacing(5)
        magnifier_size_icon = QLabel()
        magnifier_size_icon.setPixmap(FluentIcon.ZOOM.icon().pixmap(16, 16))
        magnifier_size_layout.addWidget(magnifier_size_icon)
        self.label_magnifier_size = QLabel(tr("放大镜大小:"))
        magnifier_size_layout.addWidget(self.label_magnifier_size)
        magnifier_layout.addLayout(magnifier_size_layout)

        self.slider_magnifier_size = Slider(Qt.Orientation.Horizontal)
        self.slider_magnifier_size.setRange(5, 40)
        self.slider_magnifier_size.setValue(int(self.magnifier_size_relative * 100))
        self.slider_magnifier_size.setMinimumWidth(100)
        magnifier_layout.addWidget(self.slider_magnifier_size, 1)

        # 捕获区域大小
        capture_size_layout = QHBoxLayout()
        capture_size_layout.setSpacing(5)
        capture_size_icon = QLabel()
        capture_size_icon.setPixmap(FluentIcon.EDIT.icon().pixmap(16, 16))
        capture_size_layout.addWidget(capture_size_icon)
        self.label_capture_size = QLabel(tr("捕获区域大小:"))
        capture_size_layout.addWidget(self.label_capture_size)
        magnifier_layout.addLayout(capture_size_layout)

        self.slider_capture_size = Slider(Qt.Orientation.Horizontal)
        self.slider_capture_size.setRange(1, 30)
        self.slider_capture_size.setValue(int(self.capture_size_relative * 100))
        self.slider_capture_size.setMinimumWidth(100)
        magnifier_layout.addWidget(self.slider_capture_size, 1)

        # 第四行：颜色、位置和文字设置
        position_layout = QHBoxLayout()
        position_layout.setSpacing(15)

        # 边框颜色选择
        position_layout.addWidget(QLabel(tr("边框颜色:")))
        self.color_picker = PushButton(tr("选择颜色"))
        self.color_picker.setIcon(FluentIcon.PALETTE.icon())
        self.color_picker.setMinimumWidth(120)
        position_layout.addWidget(self.color_picker)

        # 显示文字信息复选框
        self.checkbox_show_text = CheckBox(tr("显示文字信息"))
        self.checkbox_show_text.setIcon(FluentIcon.FONT.icon())
        self.checkbox_show_text.setMinimumWidth(150)
        self.checkbox_show_text.setChecked(False)
        position_layout.addWidget(self.checkbox_show_text)

        # 放大内容显示位置
        position_combo_layout = QHBoxLayout()
        position_combo_layout.setSpacing(5)
        position_icon = QLabel()
        position_icon.setPixmap(FluentIcon.GLOBE.icon().pixmap(16, 16))
        position_combo_layout.addWidget(position_icon)
        position_combo_layout.addWidget(QLabel(tr("放大内容位置:")))
        position_layout.addLayout(position_combo_layout)

        self.combo_position = ComboBox()
        self.combo_position.setMinimumWidth(120)
        # 创建位置映射字典
        self.position_map = {}
        for pos_id, pos_name in POSITION_NAMES.items():
            self.combo_position.addItem(pos_name)
            # 将位置 ID 存储在映射字典中
            self.position_map[self.combo_position.count()-1] = pos_id
        # 设置默认选中项
        for i, pos_id in self.position_map.items():
            if pos_id == self.magnifier_position:
                self.combo_position.setCurrentIndex(i)
                break
        position_layout.addWidget(self.combo_position)

        position_layout.addStretch(1)

        # 创建文字编辑区域容器
        self.text_edit_container = QWidget()
        self.text_edit_layout = QVBoxLayout(self.text_edit_container)
        self.text_edit_layout.setSpacing(10)

        # 添加文字颜色选择和字体大小设置
        text_settings_layout = QHBoxLayout()
        text_settings_layout.setSpacing(15)

        # 文字颜色选择
        text_settings_layout.addWidget(QLabel(tr("文字颜色:")))
        self.text_color_picker = PushButton(tr("选择颜色"))
        self.text_color_picker.setIcon(FluentIcon.PALETTE.icon())
        self.text_color_picker.setMinimumWidth(120)
        text_settings_layout.addWidget(self.text_color_picker)

        # 字体大小设置
        text_settings_layout.addWidget(QLabel(tr("字体大小:")))
        self.font_size_slider = Slider(Qt.Orientation.Horizontal)
        self.font_size_slider.setRange(10, 100)
        self.font_size_slider.setValue(20)
        self.font_size_slider.setMinimumWidth(100)
        text_settings_layout.addWidget(self.font_size_slider, 1)

        # 添加到文字编辑布局
        self.text_edit_layout.addLayout(text_settings_layout)

        # 创建文字编辑区域
        self.image_text_edits = []
        self.image_text_labels = []

        # 创建文字编辑区域的滚动区域
        self.text_edit_scroll_area = ScrollArea()
        self.text_edit_scroll_area.setWidgetResizable(True)
        self.text_edit_scroll_widget = QWidget()
        self.text_edit_scroll_layout = QVBoxLayout(self.text_edit_scroll_widget)
        self.text_edit_scroll_layout.setSpacing(10)
        self.text_edit_scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.text_edit_scroll_area.setWidget(self.text_edit_scroll_widget)

        # 添加滚动区域到文字编辑布局
        self.text_edit_layout.addWidget(self.text_edit_scroll_area)

        # 初始化时隐藏文字编辑区域
        self.text_edit_container.setVisible(False)

        # 添加所有行到控制布局
        control_layout.addLayout(button_layout)
        control_layout.addLayout(layout_control)
        control_layout.addLayout(magnifier_layout)
        control_layout.addLayout(position_layout)
        control_layout.addWidget(self.text_edit_container)

        # 初始化控件状态
        visible = self.use_magnifier
        self.slider_magnifier_size.setVisible(visible and not self.fixed_magnifier_size)
        self.label_magnifier_size.setVisible(visible)
        self.slider_capture_size.setVisible(visible and not self.fixed_magnifier_size)
        self.label_capture_size.setVisible(visible)
        self.checkbox_fixed_size.setEnabled(visible)
        self.combo_position.setEnabled(visible)

        return control_layout

    def _connect_signals(self):
        """连接信号和槽"""
        # 按钮信号
        self.btn_import.clicked.connect(self.import_images)
        self.btn_clear.clicked.connect(self.clear_images)
        self.btn_export.clicked.connect(self.export_images)
        self.btn_export_original.clicked.connect(self.export_original_images)
        self.btn_help.clicked.connect(self.show_help)

        # 控件信号
        self.spin_rows.valueChanged.connect(self.update_grid_layout)
        self.spin_cols.valueChanged.connect(self.update_grid_layout)
        self.checkbox_magnifier.stateChanged.connect(self.toggle_magnifier)
        self.checkbox_fixed_size.stateChanged.connect(self.toggle_fixed_magnifier_size)
        self.slider_magnifier_size.valueChanged.connect(self.update_magnifier_size)
        self.slider_capture_size.valueChanged.connect(self.update_capture_size)
        self.color_picker.clicked.connect(self.open_color_dialog)
        self.combo_position.currentIndexChanged.connect(self.update_magnifier_position)

        # 文字编辑相关信号
        self.checkbox_show_text.stateChanged.connect(self.toggle_text_edit)
        self.text_color_picker.clicked.connect(self.open_text_color_dialog)
        self.font_size_slider.valueChanged.connect(self.update_font_size)

    def import_images(self):
        """导入多张图片"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("图像文件 (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)")

        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if not file_paths:
                return

            # 清除现有图像
            if self.images:
                reply = QMessageBox.question(
                    self, tr("确认"), tr("是否清除现有图像并导入新图像？"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
                self.clear_images()

            # 加载新图像
            first_image_size = None
            valid_images = []
            valid_paths = []

            for path in file_paths:
                try:
                    img = Image.open(path)

                    # 检查第一张图片的尺寸
                    if first_image_size is None:
                        first_image_size = img.size

                    # 验证尺寸是否相同
                    if img.size != first_image_size:
                        QMessageBox.warning(
                            self, tr("警告"),
                            tr(f"图像 {os.path.basename(path)} 的尺寸与第一张图像不同，已跳过。")
                        )
                        continue

                    # 转换为RGB模式
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')

                    valid_images.append(img)
                    valid_paths.append(path)

                except Exception as e:
                    QMessageBox.warning(
                        self, tr("警告"),
                        tr(f"无法加载图像 {path}: {str(e)}")
                    )

            if valid_images:
                self.images = valid_images
                self.image_paths = valid_paths
                self.status_label.setText(f"已加载 {len(self.images)} 张图像")
                self.update_grid_layout()
            else:
                QMessageBox.warning(
                    self, tr("警告"),
                    tr("没有加载任何有效图像。")
                )

    def clear_images(self):
        """清除所有图像"""
        self.images = []
        self.image_paths = []
        self.status_label.setText("已清除所有图像")
        self.update_grid_layout()

    def update_grid_layout(self):
        """更新网格布局"""
        # 获取新的行列数
        self.rows = self.spin_rows.value()
        self.cols = self.spin_cols.value()

        # 清除现有布局中的所有小部件
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 如果没有图像，则不创建网格
        if not self.images:
            return

        # 创建图像标签网格
        self.image_labels = []

        for i in range(min(len(self.images), self.rows * self.cols)):
            # 超出网格大小的图像不显示

            row = i // self.cols
            col = i % self.cols

            # 创建可点击的图像标签
            label = ClickableImageLabel()
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            label.setMinimumSize(200, 150)

            # 连接鼠标事件
            label.clicked.connect(lambda evt, idx=i: self.on_image_clicked(evt, idx))
            label.moved.connect(lambda evt, idx=i: self.on_image_mouse_moved(evt, idx))

            # 添加到网格
            self.grid_layout.addWidget(label, row, col)
            self.image_labels.append(label)

        # 确保文字数组与图像数组大小一致
        while len(self.image_texts) < len(self.images):
            self.image_texts.append("")

        # 更新文字编辑区域
        self.update_text_edit_area()

        # 更新图像显示
        self.update_images_display()

    def update_images_display(self):
        """更新所有图像的显示"""
        if not self.images or not hasattr(self, 'image_labels'):
            return

        for i, (img, label) in enumerate(zip(self.images, self.image_labels)):
            if i >= len(self.images) or i >= len(self.image_labels):
                break

            # 创建用于显示的图像副本
            display_img = img.copy()

            # 如果启用了放大镜，添加放大镜效果
            if self.use_magnifier:
                img_width, img_height = display_img.size
                min_dim = min(img_width, img_height)

                # 计算放大镜大小
                magnifier_size = max(20, int(round(self.magnifier_size_relative * min_dim)))

                if self.use_stretchable_rect:
                    # 使用可拉伸矩形框
                    rect = QRectF(
                        self.capture_rect_relative.x() * img_width,
                        self.capture_rect_relative.y() * img_height,
                        self.capture_rect_relative.width() * img_width,
                        self.capture_rect_relative.height() * img_height
                    )

                    # 绘制可拉伸矩形框和获取放大图像
                    framed_img, magnified_img = draw_stretchable_rectangle_magnifier(
                        display_img,
                        rect,
                        magnifier_size,
                        border_color=self.border_color,
                        border_width=self.border_width
                    )

                    if framed_img is not None and magnified_img is not None:
                        # 创建组合图像（原图+放大图）
                        display_img = create_corner_image(
                            framed_img,
                            magnified_img,
                            position=self.magnifier_position,
                            spacing=10,
                            border_color=self.border_color,
                            border_width=self.border_width
                        )
                else:
                    # 使用普通矩形框
                    # 计算捕获中心点和大小
                    capture_center = QPointF(
                        self.capture_position_relative.x() * img_width,
                        self.capture_position_relative.y() * img_height
                    )

                    # 计算捕获大小
                    capture_size = max(10, int(round(self.capture_size_relative * min_dim)))

                    # 绘制矩形框和获取放大图像
                    framed_img, magnified_img = draw_rectangle_magnifier(
                        display_img,
                        capture_center,
                        capture_size,
                        magnifier_size,
                        border_color=self.border_color,
                        border_width=self.border_width
                    )

                    if framed_img is not None and magnified_img is not None:
                        # 创建组合图像（原图+放大图）
                        display_img = create_corner_image(
                            framed_img,
                            magnified_img,
                            position=self.magnifier_position,
                            spacing=10,
                            border_color=self.border_color,
                            border_width=self.border_width
                        )

            # 如果启用了文字显示，添加文字
            if self.show_text and i < len(self.image_texts) and self.image_texts[i]:
                # 创建一个绘图对象
                draw = ImageDraw.Draw(display_img)

                # 计算文字位置（左下角）
                text = self.image_texts[i]
                padding = 10

                # 使用字体大小而不是高度
                try:
                    # 尝试使用默认字体
                    font = ImageFont.truetype("Arial", self.font_size)
                except IOError:
                    # 如果无法加载字体，使用默认字体
                    font = ImageFont.load_default()

                # 获取文字尺寸以计算位置
                text_bbox = draw.textbbox((0, 0), text, font=font)
                # 计算文字高度（宽度暂时不用，但保留以便将来可能需要）
                # text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]

                position = (padding, display_img.height - text_height - padding)

                # 绘制文字阴影（增强可读性）
                shadow_color = (0, 0, 0, 255)  # 黑色阴影
                shadow_offset = 1
                draw.text((position[0] + shadow_offset, position[1] + shadow_offset), text, font=font, fill=shadow_color)

                # 绘制文字
                draw.text(position, text, font=font, fill=self.text_color)

            # 转换为QPixmap并显示
            try:
                qimage = QImage(
                    display_img.tobytes('raw', 'RGBA'),
                    display_img.width, display_img.height,
                    QImage.Format.Format_RGBA8888
                )
                pixmap = QPixmap.fromImage(qimage)

                # 根据标签大小缩放图像
                label_size = label.size()
                if not pixmap.isNull() and label_size.width() > 0 and label_size.height() > 0:
                    scaled_pixmap = pixmap.scaled(
                        label_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    label.setPixmap(scaled_pixmap)

                    # 显示图像文件名
                    if i < len(self.image_paths):
                        label.setToolTip(os.path.basename(self.image_paths[i]))
            except Exception as e:
                print(f"显示图像 {i} 时出错: {e}")
                traceback.print_exc()

    def on_image_clicked(self, event, image_index):
        """处理图像点击事件"""
        if not self.images or image_index >= len(self.images):
            return

        if not self.use_magnifier:
            return

        # 如果固定捕获区域大小，仅允许移动位置，不允许调整大小
        if self.fixed_magnifier_size:
            # 获取鼠标在图像上的相对位置
            pos_in_image = self._get_position_in_image(event, image_index)
            if pos_in_image is None:
                return

            img_x, img_y, pixmap_rect = pos_in_image

            # 仅允许移动位置
            self._is_dragging_capture_point = True

            if self.use_stretchable_rect:
                # 移动矩形框的中心点
                width = self.capture_rect_relative.width()
                height = self.capture_rect_relative.height()
                new_x = (img_x / pixmap_rect.width()) - width / 2
                new_y = (img_y / pixmap_rect.height()) - height / 2

                # 确保矩形在图像范围内
                new_x = max(0, min(new_x, 1 - width))
                new_y = max(0, min(new_y, 1 - height))

                self.capture_rect_relative = QRectF(new_x, new_y, width, height)
            else:
                # 更新捕获位置
                self.capture_position_relative = QPointF(
                    img_x / pixmap_rect.width(),
                    img_y / pixmap_rect.height()
                )

            # 更新显示
            self.update_images_display()
            return

        # 如果不是固定捕获区域大小，允许正常操作
        # 获取鼠标在图像上的相对位置
        pos_in_image = self._get_position_in_image(event, image_index)
        if pos_in_image is None:
            return

        img_x, img_y, pixmap_rect = pos_in_image

        if self.use_stretchable_rect:
            # 检查是否点击了调整大小的手柄
            rect_in_pixels = QRectF(
                self.capture_rect_relative.x() * pixmap_rect.width(),
                self.capture_rect_relative.y() * pixmap_rect.height(),
                self.capture_rect_relative.width() * pixmap_rect.width(),
                self.capture_rect_relative.height() * pixmap_rect.height()
            )

            # 检查是否点击了矩形的边缘或角落
            handle_size = self._resize_handle_size
            left = rect_in_pixels.left()
            top = rect_in_pixels.top()
            right = rect_in_pixels.right()
            bottom = rect_in_pixels.bottom()

            # 检查各个角落和边缘
            if abs(img_x - left) < handle_size and abs(img_y - top) < handle_size:
                self._active_resize_handle = "top-left"
                self._is_resizing_capture_rect = True
            elif abs(img_x - right) < handle_size and abs(img_y - top) < handle_size:
                self._active_resize_handle = "top-right"
                self._is_resizing_capture_rect = True
            elif abs(img_x - left) < handle_size and abs(img_y - bottom) < handle_size:
                self._active_resize_handle = "bottom-left"
                self._is_resizing_capture_rect = True
            elif abs(img_x - right) < handle_size and abs(img_y - bottom) < handle_size:
                self._active_resize_handle = "bottom-right"
                self._is_resizing_capture_rect = True
            elif abs(img_x - left) < handle_size:
                self._active_resize_handle = "left"
                self._is_resizing_capture_rect = True
            elif abs(img_x - right) < handle_size:
                self._active_resize_handle = "right"
                self._is_resizing_capture_rect = True
            elif abs(img_y - top) < handle_size:
                self._active_resize_handle = "top"
                self._is_resizing_capture_rect = True
            elif abs(img_y - bottom) < handle_size:
                self._active_resize_handle = "bottom"
                self._is_resizing_capture_rect = True
            elif rect_in_pixels.contains(img_x, img_y):
                # 点击了矩形内部，开始拖动
                self._is_dragging_capture_point = True
                self._active_resize_handle = None
        else:
            # 使用普通捕获点
            self._is_dragging_capture_point = True
            # 更新捕获位置
            self.capture_position_relative = QPointF(
                img_x / pixmap_rect.width(),
                img_y / pixmap_rect.height()
            )

        # 更新显示
        self.update_images_display()

    def on_image_mouse_moved(self, event, image_index):
        """处理图像鼠标移动事件"""
        if not self.images or image_index >= len(self.images) or not self.use_magnifier:
            return

        # 获取鼠标在图像上的相对位置
        pos_in_image = self._get_position_in_image(event, image_index)
        if pos_in_image is None:
            return

        img_x, img_y, pixmap_rect = pos_in_image

        # 如果固定捕获区域大小，仅允许移动位置
        if self.fixed_magnifier_size and self._is_dragging_capture_point:
            if self.use_stretchable_rect:
                # 移动矩形框的中心点
                width = self.capture_rect_relative.width()
                height = self.capture_rect_relative.height()
                new_x = (img_x / pixmap_rect.width()) - width / 2
                new_y = (img_y / pixmap_rect.height()) - height / 2

                # 确保矩形在图像范围内
                new_x = max(0, min(new_x, 1 - width))
                new_y = max(0, min(new_y, 1 - height))

                self.capture_rect_relative = QRectF(new_x, new_y, width, height)
            else:
                # 更新捕获位置
                self.capture_position_relative = QPointF(
                    img_x / pixmap_rect.width(),
                    img_y / pixmap_rect.height()
                )

            # 更新显示
            self.update_images_display()
            return

        # 如果不是固定捕获区域大小，允许正常操作
        if self._is_dragging_capture_point:
            if self.use_stretchable_rect:
                # 移动整个矩形
                width = self.capture_rect_relative.width()
                height = self.capture_rect_relative.height()
                new_x = (img_x / pixmap_rect.width()) - width / 2
                new_y = (img_y / pixmap_rect.height()) - height / 2

                # 确保矩形在图像范围内
                new_x = max(0, min(new_x, 1 - width))
                new_y = max(0, min(new_y, 1 - height))

                self.capture_rect_relative = QRectF(new_x, new_y, width, height)
            else:
                # 更新捕获点位置
                self.capture_position_relative = QPointF(
                    img_x / pixmap_rect.width(),
                    img_y / pixmap_rect.height()
                )
        elif self._is_resizing_capture_rect and self.use_stretchable_rect and not self.fixed_magnifier_size:
            # 调整矩形大小
            x = self.capture_rect_relative.x()
            y = self.capture_rect_relative.y()
            width = self.capture_rect_relative.width()
            height = self.capture_rect_relative.height()

            # 计算相对位置
            rel_x = img_x / pixmap_rect.width()
            rel_y = img_y / pixmap_rect.height()

            # 根据不同的手柄调整矩形
            if self._active_resize_handle == "top-left":
                new_width = x + width - rel_x
                new_height = y + height - rel_y
                if new_width > 0.01 and new_height > 0.01:
                    self.capture_rect_relative = QRectF(rel_x, rel_y, new_width, new_height)
            elif self._active_resize_handle == "top-right":
                new_width = rel_x - x
                new_height = y + height - rel_y
                if new_width > 0.01 and new_height > 0.01:
                    self.capture_rect_relative = QRectF(x, rel_y, new_width, new_height)
            elif self._active_resize_handle == "bottom-left":
                new_width = x + width - rel_x
                new_height = rel_y - y
                if new_width > 0.01 and new_height > 0.01:
                    self.capture_rect_relative = QRectF(rel_x, y, new_width, new_height)
            elif self._active_resize_handle == "bottom-right":
                new_width = rel_x - x
                new_height = rel_y - y
                if new_width > 0.01 and new_height > 0.01:
                    self.capture_rect_relative = QRectF(x, y, new_width, new_height)
            elif self._active_resize_handle == "left":
                new_width = x + width - rel_x
                if new_width > 0.01:
                    self.capture_rect_relative = QRectF(rel_x, y, new_width, height)
            elif self._active_resize_handle == "right":
                new_width = rel_x - x
                if new_width > 0.01:
                    self.capture_rect_relative = QRectF(x, y, new_width, height)
            elif self._active_resize_handle == "top":
                new_height = y + height - rel_y
                if new_height > 0.01:
                    self.capture_rect_relative = QRectF(x, rel_y, width, new_height)
            elif self._active_resize_handle == "bottom":
                new_height = rel_y - y
                if new_height > 0.01:
                    self.capture_rect_relative = QRectF(x, y, width, new_height)

        # 更新显示
        self.update_images_display()

    def _get_position_in_image(self, event, image_index):
        """获取鼠标在图像上的位置"""
        label = self.image_labels[image_index]
        pixmap = label.pixmap()

        if not pixmap or pixmap.isNull():
            return None

        # 获取图像在标签中的实际显示区域
        label_rect = label.rect()
        pixmap_rect = pixmap.rect()

        # 计算图像的缩放比例和偏移
        scale_w = pixmap_rect.width() / label_rect.width()
        scale_h = pixmap_rect.height() / label_rect.height()
        scale = max(scale_w, scale_h)

        # 计算图像在标签中的实际显示区域
        scaled_width = pixmap_rect.width() / scale
        scaled_height = pixmap_rect.height() / scale

        # 计算图像的偏移量
        offset_x = (label_rect.width() - scaled_width) / 2
        offset_y = (label_rect.height() - scaled_height) / 2

        # 获取鼠标在图像上的相对位置
        pos = event.position()
        img_x = (pos.x() - offset_x) * scale
        img_y = (pos.y() - offset_y) * scale

        # 确保坐标在图像范围内
        img_x = max(0, min(img_x, pixmap_rect.width() - 1))
        img_y = max(0, min(img_y, pixmap_rect.height() - 1))

        return img_x, img_y, pixmap_rect

    def update_capture_position(self, event, image_index):
        """更新捕获位置（兼容旧版本）"""
        pos_in_image = self._get_position_in_image(event, image_index)
        if pos_in_image is None:
            return

        img_x, img_y, pixmap_rect = pos_in_image

        # 更新相对捕获位置
        self.capture_position_relative = QPointF(
            img_x / pixmap_rect.width(),
            img_y / pixmap_rect.height()
        )

        # 更新所有图像显示
        self.update_images_display()

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_dragging_capture_point:
                self._is_dragging_capture_point = False
                self.update_images_display()
            if self._is_resizing_capture_rect:
                self._is_resizing_capture_rect = False
                self._active_resize_handle = None
                self.update_images_display()
        super().mouseReleaseEvent(event)

    def toggle_magnifier(self, state):
        """切换放大镜功能"""
        new_state_bool = bool(state)
        if new_state_bool == self.use_magnifier:
            return

        self.use_magnifier = new_state_bool
        print(f"Magnifier {('enabled' if self.use_magnifier else 'disabled')}")

        # 更新相关控件的可见性
        visible = self.use_magnifier

        # 放大镜大小滑块
        self.slider_magnifier_size.setVisible(visible and not self.fixed_magnifier_size)
        self.label_magnifier_size.setVisible(visible)

        # 捕获区域大小滑块
        self.slider_capture_size.setVisible(visible and not self.fixed_magnifier_size)
        self.label_capture_size.setVisible(visible)

        # 固定捕获区域大小复选框
        self.checkbox_fixed_size.setEnabled(visible)

        # 放大内容位置下拉框
        self.combo_position.setEnabled(visible)

        # 如果禁用放大镜，重置相关状态
        if not self.use_magnifier:
            # 重置拖动状态
            self._is_dragging_capture_point = False
            self._is_resizing_capture_rect = False
            self._active_resize_handle = None

            # 如果已经固定捕获区域大小，取消固定
            if self.fixed_magnifier_size:
                self.checkbox_fixed_size.setChecked(False)

        # 更新显示
        self.update_images_display()

    def toggle_fixed_magnifier_size(self, state):
        """切换固定捕获区域大小功能"""
        self.fixed_magnifier_size = bool(state)

        # 更新放大镜大小滑块的启用状态
        self.slider_magnifier_size.setEnabled(not self.fixed_magnifier_size)
        self.slider_capture_size.setEnabled(not self.fixed_magnifier_size)

        self.update_images_display()

    def update_magnifier_size(self, value):
        """更新放大镜大小"""
        self.magnifier_size_relative = value / 100.0
        self.update_images_display()

    def update_capture_size(self, value):
        """更新捕获区域大小"""
        self.capture_size_relative = value / 100.0
        # 如果使用可拉伸矩形框，更新矩形大小
        if self.use_stretchable_rect:
            # 保持矩形中心不变，保持宽高比例
            center_x = self.capture_rect_relative.x() + self.capture_rect_relative.width() / 2
            center_y = self.capture_rect_relative.y() + self.capture_rect_relative.height() / 2

            # 计算当前宽高比
            current_ratio = self.capture_rect_relative.width() / self.capture_rect_relative.height() if self.capture_rect_relative.height() > 0 else 1.0

            # 使用新的捕获大小，但保持宽高比
            if current_ratio >= 1.0:  # 宽大于高
                new_width = self.capture_size_relative
                new_height = new_width / current_ratio
            else:  # 高大于宽
                new_height = self.capture_size_relative
                new_width = new_height * current_ratio

            # 计算新的左上角坐标
            new_x = center_x - new_width / 2
            new_y = center_y - new_height / 2

            # 确保矩形在图像范围内
            new_x = max(0.0, min(new_x, 1.0 - new_width))
            new_y = max(0.0, min(new_y, 1.0 - new_height))

            self.capture_rect_relative = QRectF(new_x, new_y, new_width, new_height)
        self.update_images_display()

    def open_color_dialog(self):
        """打开颜色选择对话框"""
        current_color = QColor(*self.border_color[:3])
        color = QColorDialog.getColor(current_color, self, tr("选择边框颜色"))

        if color.isValid():
            self.update_border_color(color)

    def update_border_color(self, color):
        """更新边框颜色"""
        self.border_color = (color.red(), color.green(), color.blue(), 255)
        self.update_images_display()

    def update_magnifier_position(self, index):
        """更新放大内容显示位置"""
        position = self.position_map.get(index)
        if position is not None:
            self.magnifier_position = position
            self.update_images_display()

    def toggle_text_edit(self, state):
        """切换文字编辑区域的显示"""
        self.show_text = bool(state)
        self.text_edit_container.setVisible(self.show_text)
        self.update_text_edit_area()
        self.update_images_display()

    def update_text_edit_area(self):
        """更新文字编辑区域"""
        # 清除现有的文字编辑区域
        while self.text_edit_scroll_layout.count():
            item = self.text_edit_scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 重置文字编辑器列表
        self.image_text_edits = []
        self.image_text_labels = []

        # 如果没有图像，不创建编辑区域
        if not self.images:
            return

        # 为每张图像创建文字编辑器
        for i, img in enumerate(self.images):
            if i >= self.rows * self.cols:
                break  # 超出网格大小的图像不显示

            # 创建每张图的文字编辑区域
            item_layout = QHBoxLayout()

            # 添加图像标签
            image_label = QLabel()
            image_label.setFixedSize(50, 50)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 缩小图像并显示
            try:
                thumb = img.copy()
                thumb.thumbnail((50, 50))
                qimage = QImage(
                    thumb.tobytes('raw', 'RGBA'),
                    thumb.width, thumb.height,
                    QImage.Format.Format_RGBA8888
                )
                pixmap = QPixmap.fromImage(qimage)
                image_label.setPixmap(pixmap)
            except Exception as e:
                print(f"创建缩略图 {i} 时出错: {e}")

            item_layout.addWidget(image_label)
            self.image_text_labels.append(image_label)

            # 添加图像名称标签
            name_label = QLabel()
            if i < len(self.image_paths):
                name_label.setText(os.path.basename(self.image_paths[i]))
            else:
                name_label.setText(f"Image {i+1}")
            name_label.setFixedWidth(150)
            item_layout.addWidget(name_label)

            # 添加文字编辑器
            text_edit = LineEdit()
            text_edit.setPlaceholderText(tr("输入图像文字信息"))
            # 移除填充文字效果
            text_edit.setStyleSheet("QLineEdit { background-color: white; }")
            if i < len(self.image_texts) and self.image_texts[i]:
                text_edit.setText(self.image_texts[i])

            # 连接信号
            text_edit.textChanged.connect(lambda text, idx=i: self.update_image_text(idx, text))

            item_layout.addWidget(text_edit, 1)  # 1表示拉伸因子
            self.image_text_edits.append(text_edit)

            # 添加到滚动区域布局
            self.text_edit_scroll_layout.addLayout(item_layout)

        # 添加弹性空间
        self.text_edit_scroll_layout.addStretch(1)

    def update_image_text(self, index, text):
        """更新图像文字"""
        if 0 <= index < len(self.image_texts):
            self.image_texts[index] = text
            self.update_images_display()

    def open_text_color_dialog(self):
        """打开文字颜色选择对话框"""
        current_color = QColor(*self.text_color[:3])
        color = QColorDialog.getColor(current_color, self, tr("选择文字颜色"))

        if color.isValid():
            self.text_color = (color.red(), color.green(), color.blue(), 255)
            self.update_images_display()

    def update_font_size(self, value):
        """更新字体大小"""
        self.font_size = value
        self.update_images_display()

    def export_images(self):
        """导出图中图"""
        if not self.images:
            QMessageBox.warning(self, tr("警告"), tr("没有可导出的图像。"))
            return

        # 选择导出目录
        export_dir = QFileDialog.getExistingDirectory(
            self, tr("选择导出目录"), "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )

        if not export_dir:
            return

        # 导出每张图像
        export_count = 0
        for i, img in enumerate(self.images):
            if i >= len(self.image_labels):
                break

            try:
                # 创建用于导出的图像副本
                export_img = img.copy()

                # 如果启用了放大镜，添加放大镜效果
                if self.use_magnifier:
                    img_width, img_height = export_img.size
                    min_dim = min(img_width, img_height)

                    # 计算放大镜大小
                    magnifier_size = max(20, int(round(self.magnifier_size_relative * min_dim)))

                    if self.use_stretchable_rect:
                        # 使用可拉伸矩形框
                        rect = QRectF(
                            self.capture_rect_relative.x() * img_width,
                            self.capture_rect_relative.y() * img_height,
                            self.capture_rect_relative.width() * img_width,
                            self.capture_rect_relative.height() * img_height
                        )

                        # 绘制可拉伸矩形框和获取放大图像
                        framed_img, magnified_img = draw_stretchable_rectangle_magnifier(
                            export_img,
                            rect,
                            magnifier_size,
                            border_color=self.border_color,
                            border_width=self.border_width
                        )

                        if framed_img is not None and magnified_img is not None:
                            # 创建组合图像（原图+放大图）
                            export_img = create_corner_image(
                                framed_img,
                                magnified_img,
                                position=self.magnifier_position,
                                spacing=10,
                                border_color=self.border_color,
                                border_width=self.border_width
                            )
                    else:
                        # 使用普通矩形框
                        # 计算捕获中心点和大小
                        capture_center = QPointF(
                            self.capture_position_relative.x() * img_width,
                            self.capture_position_relative.y() * img_height
                        )

                        # 计算捕获大小
                        capture_size = max(10, int(round(self.capture_size_relative * min_dim)))

                        # 绘制矩形框和获取放大图像
                        framed_img, magnified_img = draw_rectangle_magnifier(
                            export_img,
                            capture_center,
                            capture_size,
                            magnifier_size,
                            border_color=self.border_color,
                            border_width=self.border_width
                        )

                        if framed_img is not None and magnified_img is not None:
                            # 创建组合图像（原图+放大图）
                            export_img = create_corner_image(
                                framed_img,
                                magnified_img,
                                position=self.magnifier_position,
                                spacing=10,
                                border_color=self.border_color,
                                border_width=self.border_width
                            )

                # 生成文件名
                base_name = os.path.basename(self.image_paths[i]) if i < len(self.image_paths) else f"image_{i+1}"
                file_name = os.path.join(export_dir, f"magnified_{base_name}")

                # 确保文件扩展名正确
                if not file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_name += '.png'

                # 保存图像
                # 如果是保存为JPG格式，需要先转换为RGB模式
                if file_name.lower().endswith(('.jpg', '.jpeg')):
                    # 转换为RGB模式（去除透明通道）
                    export_img = export_img.convert('RGB')

                # 保存图像
                export_img.save(file_name)
                export_count += 1

            except Exception as e:
                QMessageBox.warning(
                    self, tr("警告"),
                    tr(f"导出图像 {i+1} 时出错: {str(e)}")
                )

        if export_count > 0:
            QMessageBox.information(
                self, tr("成功"),
                tr(f"成功导出 {export_count} 张图像到 {export_dir}")
            )
        else:
            QMessageBox.warning(
                self, tr("警告"),
                tr("没有成功导出任何图像。")
            )

    def export_original_images(self):
        """导出原图"""
        if not self.images:
            QMessageBox.warning(self, tr("警告"), tr("没有可导出的图像。"))
            return

        # 选择导出目录
        export_dir = QFileDialog.getExistingDirectory(
            self, tr("选择导出目录"), "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )

        if not export_dir:
            return

        # 导出每张原始图像
        export_count = 0
        for i, img in enumerate(self.images):
            if i >= len(self.image_labels):
                break

            try:
                # 创建用于导出的图像副本
                export_img = img.copy()

                # 生成文件名
                base_name = os.path.basename(self.image_paths[i]) if i < len(self.image_paths) else f"image_{i+1}"
                file_name = os.path.join(export_dir, f"original_{base_name}")

                # 确保文件扩展名正确
                if not file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_name += '.png'

                # 保存图像
                # 如果是保存为JPG格式，需要先转换为RGB模式
                if file_name.lower().endswith(('.jpg', '.jpeg')):
                    # 转换为RGB模式（去除透明通道）
                    export_img = export_img.convert('RGB')

                # 保存图像
                export_img.save(file_name)
                export_count += 1

            except Exception as e:
                QMessageBox.warning(
                    self, tr("警告"),
                    tr(f"导出原图 {i+1} 时出错: {str(e)}")
                )

        if export_count > 0:
            QMessageBox.information(
                self, tr("成功"),
                tr(f"成功导出 {export_count} 张原始图像到 {export_dir}")
            )
        else:
            QMessageBox.warning(
                self, tr("警告"),
                tr("没有成功导出任何图像。")
            )

    def resizeEvent(self, event):
        """处理窗口大小变化事件"""
        super().resizeEvent(event)
        QTimer.singleShot(100, self.update_images_display)

    def show_help(self):
        """显示帮助文档"""
        try:
            # 尝试打开帮助文档
            help_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "help", "multi_image_comparison_help.md")

            # 检查文件是否存在
            if not os.path.exists(help_path):
                QMessageBox.warning(self, tr("警告"), tr("帮助文档不存在。"))
                return

            # 根据操作系统打开文件
            import platform
            import subprocess

            system = platform.system()
            if system == "Windows":
                os.startfile(help_path)
            elif system == "Darwin":  # macOS
                subprocess.call(["open", help_path])
            else:  # Linux
                subprocess.call(["xdg-open", help_path])

        except Exception as e:
            QMessageBox.warning(self, tr("警告"), tr(f"无法打开帮助文档: {str(e)}"))
