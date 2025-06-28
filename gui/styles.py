#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用程序的样式表
"""

LIGHT_STYLE = """
QMainWindow {
    background-color: #f5f5f5;
}

QWidget {
    font-family: "Noto Sans CJK SC", "Source Han Sans SC", "PingFang SC", "Hiragino Sans GB", "WenQuanYi Micro Hei", sans-serif;
}

QListWidget {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 5px;
}

QPushButton {
    background-color: #4184f3;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #5294ff;
}

QPushButton:pressed {
    background-color: #3367d6;
}

QProgressBar {
    border: none;
    background-color: #e0e0e0;
    border-radius: 2px;
}

QProgressBar::chunk {
    border-radius: 2px;
}

QMenuBar {
    background-color: #f5f5f5;
    border-bottom: 1px solid #e0e0e0;
}

QMenuBar::item {
    padding: 6px 10px;
}

QMenuBar::item:selected {
    background-color: #e0e0e0;
    border-radius: 4px;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 20px;
    border-radius: 3px;
}

QMenu::item:selected {
    background-color: #e0e0e0;
}

QLineEdit {
    padding: 6px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background-color: #ffffff;
}

QLineEdit:focus {
    border: 1px solid #4184f3;
}

QGroupBox {
    font-weight: bold;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
}
"""

DARK_STYLE = """
QMainWindow, QDialog {
    background-color: #2d2d2d;
    color: #f0f0f0;
}

QWidget {
    color: #f0f0f0;
    font-family: "Noto Sans CJK SC", "Source Han Sans SC", "PingFang SC", "Hiragino Sans GB", "WenQuanYi Micro Hei", sans-serif;
}

QListWidget {
    background-color: #3d3d3d;
    border: 1px solid #505050;
    border-radius: 6px;
    padding: 5px;
}

QPushButton {
    background-color: #4184f3;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #5294ff;
}

QPushButton:pressed {
    background-color: #3367d6;
}

QProgressBar {
    border: none;
    background-color: #505050;
    border-radius: 2px;
}

QProgressBar::chunk {
    border-radius: 2px;
}

QMenuBar {
    background-color: #2d2d2d;
    border-bottom: 1px solid #505050;
}

QMenuBar::item {
    padding: 6px 10px;
    color: #f0f0f0;
}

QMenuBar::item:selected {
    background-color: #505050;
    border-radius: 4px;
}

QMenu {
    background-color: #3d3d3d;
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 20px;
    border-radius: 3px;
    color: #f0f0f0;
}

QMenu::item:selected {
    background-color: #505050;
}

QLabel {
    color: #f0f0f0;
}

QLineEdit {
    padding: 6px;
    border: 1px solid #505050;
    border-radius: 4px;
    background-color: #3d3d3d;
    color: #f0f0f0;
}

QLineEdit:focus {
    border: 1px solid #4184f3;
}

QGroupBox {
    font-weight: bold;
    border: 1px solid #505050;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 10px;
    color: #f0f0f0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
}

QCheckBox {
    color: #f0f0f0;
}

QComboBox {
    padding: 6px;
    border: 1px solid #505050;
    border-radius: 4px;
    background-color: #3d3d3d;
    color: #f0f0f0;
}

QComboBox QAbstractItemView {
    background-color: #3d3d3d;
    border: 1px solid #505050;
    selection-background-color: #505050;
    selection-color: #f0f0f0;
}
""" 