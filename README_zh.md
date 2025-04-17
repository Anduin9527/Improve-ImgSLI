<p align="center"><img src="https://raw.githubusercontent.com/johnpetersa19/Improve-ImgSLI/037ab021aa79aa40a85a25d591e887dca85cd50d/src/icons/logo-github%20.svg" alt="Logo" width="384">

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/Loganavter/Improve-ImgSLI?style=flat-square)](https://github.com/Loganavter/Improve-ImgSLI/releases/latest)
[![License: MIT](https://img.shields.io/github/license/Loganavter/Improve-ImgSLI?style=flat-square)](LICENSE)

**一款直观、开源的高级图像比较和交互工具**

---

## 目录

* [概述](#概述)
* [主要功能](#主要功能)
* [安装方法](#安装方法)
* [基本使用](#基本使用)
* [贡献](#贡献)
* [许可证](#许可证)

---

## 概述 <a name="概述"></a>

Improve ImgSLI 是一款开源、非专有的软件，专为直观的图像交互而设计。它完全免费，允许在没有限制性许可的情况下轻松分发。它适用于任何需要详细图像比较、分析或处理的人，如设计师、图像优化爱好者、摄影师或研究人员。

---

## 主要功能 <a name="主要功能"></a>

**图像比较与分析：**
* 并排比较两张图像，通过可调整的分隔线直观对比差异
* 支持水平或垂直分割模式，灵活适应不同图像比较需求
* 同步放大镜功能，可放大查看图像细节，支持独立移动和调整
* 支持冻结放大镜位置，便于固定关注点进行比较

**图像处理与导出：**
* 保存当前比较视图为单一图像文件
* 创建扫描线动画，展示两图之间的平滑过渡效果
* 支持创建多图像序列动画，实现多张图像间的连续过渡
* 支持GIF和MP4格式导出，可调整质量和帧率

**用户体验与界面：**
* 多语言支持（英语、俄语、中文、巴西葡萄牙语），通过国旗图标快速切换
* 动态窗口调整，内容自适应渲染（相对坐标）
* 跨会话保存窗口状态、语言和各种显示偏好设置
* 支持拖放操作，便于快速加载图像
* 现代化Fluent设计风格界面

---

## 安装方法 <a name="安装方法"></a>

**Python（从源码安装）：**
* 需要：Python、pip、bash
```bash
git clone https://github.com/Loganavter/Improve-ImgSLI.git
cd Improve-ImgSLI
chmod +x launcher.sh
./launcher.sh
```

**Arch Linux（AUR）：**
```bash
yay -S improve-imgsli
```

**Windows（Inno Setup）：**
1. 直接从[这里](https://github.com/Loganavter/Improve-ImgSLI/releases/download/v3.1.2/Improve_ImgSLI.exe)下载
2. 运行安装程序并按照提示操作

**Flatpak（FlatHub）：**
* 需要：Flatpak
```bash
flatpak install io.github.Loganavter.Improve-ImgSLI
flatpak run io.github.Loganavter.Improve-ImgSLI
```

**MacOS：**
* 需要帮助！我们正在寻求帮助创建和维护macOS版本。[在这里参与讨论并贡献](https://github.com/Loganavter/Improve-ImgSLI/pull/15)

---

## 基本使用 <a name="基本使用"></a>

1. **启动：** 使用与您的安装方式相对应的方法启动Improve ImgSLI
2. **加载图像：** 使用"添加图(组)"按钮或将图像文件拖放到主图像显示区域的左侧或右侧。如果在一侧加载多个文件，使用其上方的下拉菜单选择活动图像
3. **比较：** 在标准比较模式下，点击并拖动鼠标在图像上移动分隔线。使用"水平分割"复选框更改分割方向
4. **放大：** 通过复选框激活放大镜工具。在此模式下，点击或拖动图像设置中心捕获点。使用WASD键独立移动放大视图区域。使用Q/E键调整放大镜圆圈之间的距离。您还可以使用相应的复选框冻结捕获点（此时WASD将移动冻结点）
5. **保存：** 点击界面中的"保存结果"按钮，将当前比较视图导出为单个图像文件
6. **创建动画：** 点击"保存动画"按钮，导出GIF或MP4动画，展示从左到右移动的扫描线，在两个图像之间进行视觉过渡
7. **创建序列动画：** 点击"保存序列"按钮，选择多个图像并创建连续动画，通过平滑扫描线按顺序过渡所有选定的图像

---

## 贡献 <a name="贡献"></a>

欢迎贡献！您可以：
* 通过开启[Issue](https://github.com/Loganavter/Improve-ImgSLI/issues)报告错误或建议功能
* 通过创建[Pull Request](https://github.com/Loganavter/Improve-ImgSLI/pulls)提交改进

---

## 许可证 <a name="许可证"></a>

本项目在MIT许可证下分发。有关更多详细信息，请参阅[LICENSE](https://github.com/Loganavter/Improve-ImgSLI/blob/main/LICENSE.txt)文件。

---

[![Star History Chart](https://api.star-history.com/svg?repos=Loganavter/Improve-ImgSLI&type=Date)](https://star-history.com/#loganavter/Improve-ImgSLI&Date)
