#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyperclip
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QProgressBar, QMenu,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QAction, QColor


class OTPItemWidget(QWidget):
    """OTP项目部件，显示单个OTP账户信息"""
    
    def __init__(self, account, index, parent=None):
        super().__init__(parent)
        self.account = account
        self.index = index
        self.parent = parent
        self.animations = []  # 保存动画引用
        self.init_ui()
        
        # 添加动态效果
        self.setup_effects()
    
    def init_ui(self):
        """初始化UI"""
        # 设置样式
        self.setObjectName("otpItem")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget#otpItem {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # 顶部信息
        info_layout = QHBoxLayout()
        
        # 左侧账户信息
        account_layout = QVBoxLayout()
        
        # 账户名称
        self.name_label = QLabel(self.account.name)
        self.name_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        account_layout.addWidget(self.name_label)
        
        # 发行方
        if self.account.issuer:
            self.issuer_label = QLabel(self.account.issuer)
            self.issuer_label.setFont(QFont("Microsoft YaHei", 9))
            self.issuer_label.setStyleSheet("color: #707070;")
            account_layout.addWidget(self.issuer_label)
        
        info_layout.addLayout(account_layout)
        info_layout.addStretch()
        
        # 右侧OTP码
        otp_layout = QVBoxLayout()
        otp_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.otp_label = QLabel()
        self.otp_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.otp_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.otp_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.otp_label.mousePressEvent = self.copy_otp
        self.otp_label.setStyleSheet("color: #2979FF;")
        otp_layout.addWidget(self.otp_label)
        
        # 添加"点击复制"提示文本
        copy_hint = QLabel("点击复制")
        copy_hint.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        copy_hint.setStyleSheet("color: #909090; font-size: 8pt;")
        otp_layout.addWidget(copy_hint)
        
        info_layout.addLayout(otp_layout)
        
        main_layout.addLayout(info_layout)
        
        # 进度条和计时器
        progress_layout = QHBoxLayout()
        
        self.timer_label = QLabel()
        self.timer_label.setStyleSheet("color: #707070;")
        progress_layout.addWidget(self.timer_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #f0f0f0;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(progress_layout)
        
        # 更新OTP码
        self.update_otp()
        
        # 上下文菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def setup_effects(self):
        """设置视觉效果"""
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def enterEvent(self, event):
        """鼠标进入事件 - 添加悬停效果"""
        self.animate_hover(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件 - 移除悬停效果"""
        self.animate_hover(False)
        super().leaveEvent(event)
    
    def animate_hover(self, hover_in):
        """悬停动画"""
        # 创建阴影动画
        shadow = self.graphicsEffect()
        animation = QPropertyAnimation(shadow, b"blurRadius")
        animation.setDuration(150)
        
        if hover_in:
            # 悬停时增大阴影
            animation.setStartValue(10)
            animation.setEndValue(15)
            self.setStyleSheet("""
                QWidget#otpItem {
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #d0d0d0;
                }
            """)
        else:
            # 离开时恢复阴影
            animation.setStartValue(15)
            animation.setEndValue(10)
            self.setStyleSheet("""
                QWidget#otpItem {
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                }
            """)
        
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        
        # 保存动画引用，避免被垃圾回收
        self.animations.append(animation)
    
    def update_otp(self):
        """更新OTP码"""
        # 获取当前OTP码
        otp = self.account.get_otp()
        
        # 设置OTP码显示格式为 XXX XXX
        formatted_otp = f"{otp[:3]} {otp[3:]}" if len(otp) == 6 else otp
        self.otp_label.setText(formatted_otp)
        
        # 更新进度条和计时器
        remaining = self.account.get_remaining_seconds()
        progress = self.account.get_progress_percent()
        self.progress_bar.setValue(int(progress))
        
        # 更新倒计时文本
        self.timer_label.setText(f"{remaining}秒")
        
        # 设置进度条颜色
        if remaining <= 5:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #f0f0f0;
                    border: none;
                    border-radius: 3px;
                }
                QProgressBar::chunk {
                    background-color: #FF5252;
                    border-radius: 3px;
                }
            """)
            self.timer_label.setStyleSheet("color: #FF5252; font-weight: bold;")
        elif remaining <= 10:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #f0f0f0;
                    border: none;
                    border-radius: 3px;
                }
                QProgressBar::chunk {
                    background-color: #FFD740;
                    border-radius: 3px;
                }
            """)
            self.timer_label.setStyleSheet("color: #FFB300;")
        else:
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #f0f0f0;
                    border: none;
                    border-radius: 3px;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 3px;
                }
            """)
            self.timer_label.setStyleSheet("color: #707070;")
    
    def copy_otp(self, event):
        """复制OTP码到剪贴板"""
        otp = self.account.get_otp()
        try:
            pyperclip.copy(otp)
            
            # 添加复制成功的视觉反馈
            original_style = self.otp_label.styleSheet()
            self.otp_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            # 2秒后恢复原来的样式
            QTimer.singleShot(1000, lambda: self.otp_label.setStyleSheet(original_style))
            
        except Exception:
            pass
    
    def show_context_menu(self, position):
        """显示上下文菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 25px 5px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
            }
        """)
        
        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(lambda: self.parent.edit_account(self.index))
        menu.addAction(edit_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self.parent.delete_account(self.index))
        menu.addAction(delete_action)
        
        menu.exec(self.mapToGlobal(position))
    
    def sizeHint(self):
        """提供建议的尺寸"""
        return QSize(380, 90) 