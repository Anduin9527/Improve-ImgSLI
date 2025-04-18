import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from qfluentwidgets import (FluentIcon, FluentWindow,
                           setTheme, Theme)

from image_comparison_app import ImageComparisonApp
from multi_image_comparison import MultiImageComparisonApp
from translations import tr

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()

        # 设置 Fluent 风格和主题
        setTheme(Theme.AUTO)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        # 创建主界面
        self.imageComparisonInterface = QWidget(self)
        self.imageComparisonInterface.setObjectName("imageComparisonInterface")
        self.imageComparisonLayout = QVBoxLayout(self.imageComparisonInterface)
        self.imageComparisonLayout.setContentsMargins(0, 0, 0, 0)

        # 创建图像比较应用实例
        self.imageComparisonApp = ImageComparisonApp()
        self.imageComparisonLayout.addWidget(self.imageComparisonApp)

        # 创建多图对比界面
        self.multiImageComparisonInterface = QWidget(self)
        self.multiImageComparisonInterface.setObjectName("multiImageComparisonInterface")
        self.multiImageComparisonLayout = QVBoxLayout(self.multiImageComparisonInterface)
        self.multiImageComparisonLayout.setContentsMargins(0, 0, 0, 0)

        # 创建多图对比应用实例
        self.multiImageComparisonApp = MultiImageComparisonApp()
        self.multiImageComparisonLayout.addWidget(self.multiImageComparisonApp)

        # 添加到导航界面
        self.addSubInterface(
            self.imageComparisonInterface,
            FluentIcon.PHOTO,
            tr('图像对比')
        )

        self.addSubInterface(
            self.multiImageComparisonInterface,
            FluentIcon.TILES,
            tr('多图对比')
        )

        # 显示导航栏
        self.navigationInterface.setVisible(True)

        # 显示返回按钮（如果存在）
        if hasattr(self.titleBar, 'backButton'):
            self.titleBar.backButton.setVisible(True)

        # 初始化窗口
        self.initWindow()

    def initWindow(self):
        # 设置窗口标题和图标
        self.setWindowTitle(tr('图像比较工具'))

        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'icon.png')
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.setWindowIcon(icon)

            # 设置标题栏图标
            if hasattr(self, 'titleBar'):
                self.titleBar.setIcon(icon)

        # 设置窗口大小
        self.resize(1000, 700)

        # 设置导航面板展开宽度
        self.navigationInterface.setExpandWidth(200)
