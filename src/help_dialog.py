from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QTextBrowser
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from qfluentwidgets import (PushButton, TitleLabel, BodyLabel,
                           ScrollArea, InfoBar)

try:
    from translations import tr as app_tr
except ImportError:
    def app_tr(text, lang='en', *args, **kwargs):
        try:
            return text.format(*args, **kwargs)
        except (KeyError, IndexError):
            return text

class HelpDialog(QDialog):
    def __init__(self, current_language, parent=None, tr_func=None):
        super().__init__(parent)
        self.tr = tr_func if callable(tr_func) else app_tr
        self.current_language = current_language

        # 设置窗口属性
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setWindowTitle(self.tr('帮助', self.current_language))
        self.setMinimumSize(600, 500)

        # 创建布局
        self.main_layout = QVBoxLayout(self)

        # 添加标题
        self.title_label = TitleLabel(self.tr('图像比较工具使用帮助', self.current_language))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        # 创建滚动区域
        self.scroll_area = ScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        # 创建文本浏览器
        self.help_content = self._get_help_content()
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setHtml(self._markdown_to_html(self.help_content))
        self.text_browser.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)

        # 设置样式
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        self.scroll_layout.addWidget(self.text_browser)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)

        # 添加确定按钮
        button_layout = QHBoxLayout()
        self.ok_button = PushButton(self.tr('确定', self.current_language))
        self.ok_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        self.main_layout.addLayout(button_layout)

    def _markdown_to_html(self, markdown_text):
        """将Markdown文本转换为HTML"""
        # 简单的Markdown到HTML转换
        html = "<html><head><style>\n"
        html += "body { font-family: Arial, sans-serif; line-height: 1.6; }\n"
        html += "h1 { color: #2b579a; font-size: 24px; margin-top: 20px; }\n"
        html += "h2 { color: #2b579a; font-size: 20px; margin-top: 15px; }\n"
        html += "ul { margin-left: 20px; }\n"
        html += "li { margin-bottom: 5px; }\n"
        html += "</style></head><body>\n"

        lines = markdown_text.split('\n')
        in_list = False

        for line in lines:
            line = line.strip()
            if not line:
                if in_list:
                    html += "</ul>\n"
                    in_list = False
                html += "<br>\n"
                continue

            # 处理标题
            if line.startswith('# '):
                if in_list:
                    html += "</ul>\n"
                    in_list = False
                html += f"<h1>{line[2:]}</h1>\n"
            elif line.startswith('## '):
                if in_list:
                    html += "</ul>\n"
                    in_list = False
                html += f"<h2>{line[3:]}</h2>\n"
            # 处理列表项
            elif line.startswith('- '):
                if not in_list:
                    html += "<ul>\n"
                    in_list = True
                html += f"<li>{line[2:]}</li>\n"
            # 普通文本
            else:
                if in_list:
                    html += "</ul>\n"
                    in_list = False
                html += f"<p>{line}</p>\n"

        if in_list:
            html += "</ul>\n"

        html += "</body></html>"
        return html

    def _get_help_content(self):
        """获取帮助内容，根据当前语言返回相应的Markdown文本"""
        return f"""
# {self.tr('图像比较工具使用指南', self.current_language)}

## {self.tr('加载图片', self.current_language)}
- {self.tr('使用"添加图片"按钮或直接拖放图片到左/右侧区域', self.current_language)}
- {self.tr('使用下拉菜单从已加载的图片中选择', self.current_language)}
- {self.tr('使用 ⇄ 按钮交换左右图片列表', self.current_language)}
- {self.tr('使用垃圾桶按钮 (🗑️) 清除相应的图像列表', self.current_language)}

## {self.tr('比较视图', self.current_language)}
- {self.tr('点击并拖动分隔线调整分割位置（当放大镜关闭时）', self.current_language)}
- {self.tr('勾选"水平分割"可以改变分割方向', self.current_language)}

## {self.tr('放大镜工具（勾选后）', self.current_language)}
- {self.tr('点击/拖动主图像设置捕获点（红色圆圈）', self.current_language)}
- {self.tr('使用WASD键移动放大视图相对于捕获点的位置', self.current_language)}
- {self.tr('使用QE键调整两个放大镜半部分之间的间距（当分离时）', self.current_language)}
- {self.tr('滑块可调整放大镜大小（缩放级别）、捕获大小（采样区域）和移动速度', self.current_language)}
- {self.tr('勾选"冻结放大镜"可锁定屏幕上的放大视图位置（WASD移动冻结视图）', self.current_language)}

## {self.tr('输出', self.current_language)}
- {self.tr('勾选"在保存的图像中包含文件名"启用在图像上保存名称的选项', self.current_language)}
- {self.tr('编辑名称、调整字体大小，并在底部面板中选择文本颜色（当包含名称时可见）', self.current_language)}
- {self.tr('点击"保存结果"将当前视图（包括分割、放大镜、名称（如果启用））保存为PNG或JPG文件', self.current_language)}

## {self.tr('设置', self.current_language)}
- {self.tr('点击设置按钮(...)更改应用程序语言、最大显示名称长度和JPEG质量', self.current_language)}
"""
