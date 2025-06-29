#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from gui.main_window import MainWindow
from utils.config import init_config

def main():
    # 初始化配置
    init_config()
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("LightAuth")
    
    # 设置应用图标
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 创建主窗口（会处理加密验证）
    window = MainWindow()
    window.show()
    
    # 执行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 