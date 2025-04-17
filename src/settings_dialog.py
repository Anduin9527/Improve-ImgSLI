import base64
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QSizePolicy
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize, Qt

# 导入Fluent控件
from qfluentwidgets import (RadioButton, SpinBox, PushButton,
                          BodyLabel, TitleLabel, FluentStyleSheet,
                          MessageBox)

try:
    from translations import tr as app_tr
except ImportError:

    def app_tr(text, lang='en', *args, **kwargs):
        try:
            return text.format(*args, **kwargs)
        except (KeyError, IndexError):
            return text
try:
    from icons import FLAG_ICONS
except ImportError:
    FLAG_ICONS = {}

class SettingsDialog(QDialog):

    def __init__(self, current_language, current_max_length, min_limit, max_limit, current_jpeg_quality, parent=None, tr_func=None):
        super().__init__(parent)
        self.tr = tr_func if callable(tr_func) else app_tr
        self.current_language = current_language

        # 应用Fluent样式到对话框
        # FluentStyleSheet.applyToWidget(self)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        self.setWindowTitle(self.tr('Settings', self.current_language))
        self.setMinimumWidth(350)
        main_layout = QVBoxLayout(self)

        # 语言设置部分
        lang_title = TitleLabel(self.tr('Language:', self.current_language))
        main_layout.addWidget(lang_title)

        # 使用网格布局来安排语言选项
        from PyQt6.QtWidgets import QGridLayout
        lang_layout = QGridLayout()
        lang_layout.setSpacing(10)

        # 创建单选按钮
        self.radio_en = RadioButton()
        self.radio_ru = RadioButton()
        self.radio_zh = RadioButton()
        self.radio_pt_br = RadioButton()

        # 设置单选按钮的属性
        self._setup_language_radio(self.radio_en, 'en', FLAG_ICONS.get('en'))
        self._setup_language_radio(self.radio_ru, 'ru', FLAG_ICONS.get('ru'))
        self._setup_language_radio(self.radio_zh, 'zh', FLAG_ICONS.get('zh'))
        self._setup_language_radio(self.radio_pt_br, 'pt_BR', FLAG_ICONS.get('pt_BR'))

        # 将单选按钮添加到网格布局中
        lang_layout.addWidget(self.radio_en, 0, 0)
        lang_layout.addWidget(self.radio_ru, 0, 1)
        lang_layout.addWidget(self.radio_zh, 1, 0)
        lang_layout.addWidget(self.radio_pt_br, 1, 1)

        main_layout.addLayout(lang_layout)

        if current_language == 'en':
            self.radio_en.setChecked(True)
        elif current_language == 'ru':
            self.radio_ru.setChecked(True)
        elif current_language == 'zh':
            self.radio_zh.setChecked(True)
        elif current_language == 'pt_BR':
            self.radio_pt_br.setChecked(True)
        else:
            self.radio_en.setChecked(True)

        # 最大名称长度设置
        length_layout = QHBoxLayout()
        length_label = BodyLabel(self.tr('Maximum Name Length (UI):', self.current_language))
        self.spin_max_length = SpinBox()
        self.spin_max_length.setRange(min_limit, max_limit)
        clamped_current_max_length = max(min_limit, min(max_limit, current_max_length))
        self.spin_max_length.setValue(clamped_current_max_length)
        tooltip_template = self.tr('Limits the displayed name length in the UI ({min}-{max}).', self.current_language)
        tooltip_text = tooltip_template.format(min=min_limit, max=max_limit)
        self.spin_max_length.setToolTip(tooltip_text)
        length_layout.addWidget(length_label)
        length_layout.addWidget(self.spin_max_length)
        main_layout.addLayout(length_layout)

        # JPEG质量设置
        jpeg_quality_layout = QHBoxLayout()
        jpeg_quality_label = BodyLabel(self.tr('JPEG Quality:', self.current_language))
        self.spin_jpeg_quality = SpinBox()
        self.spin_jpeg_quality.setRange(1, 100)
        clamped_jpeg_quality = max(1, min(100, current_jpeg_quality))
        self.spin_jpeg_quality.setValue(clamped_jpeg_quality)
        self.spin_jpeg_quality.setToolTip(self.tr('JPEG compression quality (1-100, higher is better).', self.current_language))
        jpeg_quality_layout.addWidget(jpeg_quality_label)
        jpeg_quality_layout.addWidget(self.spin_jpeg_quality)
        main_layout.addLayout(jpeg_quality_layout)

        # 按钮布局
        button_layout = QHBoxLayout()
        self.ok_button = PushButton(self.tr('OK', self.current_language))
        self.cancel_button = PushButton(self.tr('Cancel', self.current_language))
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _setup_language_radio(self, radio_button, lang_code, base64_icon):
        radio_button.setProperty('language_code', lang_code)

        # 设置语言文本
        if lang_code == 'en':
            radio_button.setText('English')
        elif lang_code == 'ru':
            radio_button.setText('Русский')
        elif lang_code == 'zh':
            radio_button.setText('中文')
        elif lang_code == 'pt_BR':
            radio_button.setText('Português')
        else:
            radio_button.setText(lang_code)

        # 设置图标
        icon = QIcon()
        if base64_icon:
            try:
                pixmap = QPixmap()
                loaded = pixmap.loadFromData(base64.b64decode(base64_icon))
                if loaded and (not pixmap.isNull()):
                    icon = QIcon(pixmap)
                else:
                    print(f"Warning: Failed to load pixmap from base64 for language '{lang_code}' in SettingsDialog.")
            except Exception as e:
                print(f"Error creating flag icon for language '{lang_code}' in SettingsDialog: {e}")
        else:
            print(f"Warning: No base64 icon data provided for language '{lang_code}' in SettingsDialog.")
        radio_button.setIcon(icon)
        radio_button.setIconSize(QSize(24, 16))

        # 设置提示文本
        tooltip_key = f'Switch language to {lang_code}'
        if lang_code == 'en':
            tooltip_key = 'Switch language to English'
        elif lang_code == 'ru':
            tooltip_key = 'Switch language to Русский'
        elif lang_code == 'zh':
            tooltip_key = 'Switch language to 中文'
        elif lang_code == 'pt_BR':
            tooltip_key = 'Switch language to Brazilian Portuguese'
        radio_button.setToolTip(self.tr(tooltip_key, self.current_language))

        # 设置大小策略
        radio_button.setMinimumSize(QSize(100, 22))
        radio_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def get_settings(self):
        selected_language = 'en'
        if self.radio_en.isChecked():
            selected_language = 'en'
        elif self.radio_ru.isChecked():
            selected_language = 'ru'
        elif self.radio_zh.isChecked():
            selected_language = 'zh'
        elif self.radio_pt_br.isChecked():
            selected_language = 'pt_BR'
        max_length = self.spin_max_length.value()
        jpeg_quality = self.spin_jpeg_quality.value()
        return (selected_language, max_length, jpeg_quality)
