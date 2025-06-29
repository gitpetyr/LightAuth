#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# -------------------------------------------------------------
# Dynamically select Qt binding:
#   • macOS   -> PySide6
#   • Windows -> PyQt6 (default)
# All other modules continue to import from `PyQt6.*` normally.
# -------------------------------------------------------------

if sys.platform.startswith("darwin"):
    # On macOS prefer PySide6 but keep backward-compat aliases so that
    # existing `from PyQt6...` imports do not have to be rewritten.
    try:
        import importlib, types
        import PySide6 as _PySide6

        # Expose top-level alias
        sys.modules.setdefault("PyQt6", _PySide6)

        # Map commonly used sub-modules
        for _sub in (
            "QtCore",
            "QtGui",
            "QtWidgets",
            "QtNetwork",
            "QtSvg",
        ):
            sys.modules.setdefault(f"PyQt6.{_sub}", importlib.import_module(f"PySide6.{_sub}"))

    except ImportError as exc:
        # Fallback: PySide6 not available, let the regular PyQt6 import fail below
        print("[Warning] Unable to import PySide6 on macOS →", exc, file=sys.stderr)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
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