import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from qfluentwidgets import setTheme, Theme

from main_window import MainWindow

if __name__ == '__main__':
    # 在PyQt6中，高DPI缩放默认启用，不需要显式设置
    # 高DPI属性在PyQt6中的处理方式不同

    app = QApplication(sys.argv)

    # 设置程序基本信息
    app.setApplicationName("Improve ImgSLI")
    app.setApplicationDisplayName("Improve ImgSLI")
    app.setOrganizationName("MyCompany")

    # 设置主题
    setTheme(Theme.AUTO)

    # 应用Fluent样式
    # 在不同版本的QFluentWidgets中，这个方法可能不同

    # 创建主窗口
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
