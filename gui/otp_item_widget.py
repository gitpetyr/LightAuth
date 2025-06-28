#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyperclip
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QProgressBar, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QAction, QColor, QFontMetrics
from typing import cast
from PyQt6.QtWidgets import QListWidgetItem


class OTPItemWidget(QWidget):
    """OTP项目部件，显示单个OTP账户信息"""
    
    def __init__(self, account, index, parent=None):
        super().__init__(parent)
        self.account = account
        self.index = index
        self.main_window = parent
        self.animations = []  # 保存动画引用
        # 不再使用阴影和悬停动画，避免QPainter多线程冲突
        self._hover_in = False  # 仅记录悬停状态
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 根据主窗口配置确定当前主题
        self.setObjectName("otpItem")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.dark_mode = (
            getattr(self.main_window, "config", {}).get("theme", "light") == "dark"
        )

        base_bg = "#3d3d3d" if self.dark_mode else "white"
        border_normal = "#505050" if self.dark_mode else "#e0e0e0"

        # 设置初始样式
        self.setStyleSheet(
            f"""
            QWidget#otpItem {{
                background-color: {base_bg};
                border-radius: 8px;
                border: 1px solid {border_normal};
            }}
        """
        )
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # 顶部信息
        info_layout = QHBoxLayout()
        
        # 左侧账户信息
        account_layout = QVBoxLayout()
        
        # 账户名称
        self.name_label = QLabel(self.account.name)
        self.name_label.setFont(QFont("Noto Sans CJK SC", 11, QFont.Weight.Bold))
        if self.dark_mode:
            self.name_label.setStyleSheet("color: #f0f0f0;")
        account_layout.addWidget(self.name_label)
        
        # 发行方
        if self.account.issuer:
            self.issuer_label = QLabel(self.account.issuer)
            self.issuer_label.setFont(QFont("Noto Sans CJK SC", 9))
            self.issuer_label.setWordWrap(True)
            self.issuer_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.issuer_label.setToolTip(self.account.issuer)
            issuer_color = "#b0b0b0" if self.dark_mode else "#707070"
            self.issuer_label.setStyleSheet(f"color: {issuer_color};")
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
        otp_color = "#90CAF9" if self.dark_mode else "#2979FF"
        self.otp_label.setStyleSheet(f"color: {otp_color};")
        otp_layout.addWidget(self.otp_label)
        
        # 添加"点击复制"提示文本
        self.copy_hint = QLabel("点击复制")
        self.copy_hint.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        hint_color = "#c0c0c0" if self.dark_mode else "#909090"
        self.copy_hint.setStyleSheet(f"color: {hint_color}; font-size: 8pt;")
        otp_layout.addWidget(self.copy_hint)
        
        info_layout.addLayout(otp_layout)
        
        main_layout.addLayout(info_layout)
        
        # 进度条和计时器
        progress_layout = QHBoxLayout()
        
        self.timer_label = QLabel()
        timer_color = "#c0c0c0" if self.dark_mode else "#707070"
        self.timer_label.setStyleSheet(f"color: {timer_color};")
        progress_layout.addWidget(self.timer_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(6)
        pg_bg = "#505050" if self.dark_mode else "#f0f0f0"
        self.progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: {pg_bg};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                border-radius: 3px;
            }}
        """
        )
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(progress_layout)
        
        # 更新OTP码
        self.update_otp()
        
        # 如果配置要求隐藏秒数，初始也应隐藏
        if not getattr(self.main_window, "config", {}).get("show_seconds", True):
            self.timer_label.hide()
            self.progress_bar.hide()
        
        # 上下文菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    # 阴影效果已移除
    def setup_effects(self):
        pass
    
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
        base_bg = "#3d3d3d" if self.dark_mode else "white"
        border_hover = "#707070" if self.dark_mode else "#d0d0d0"
        border_normal = "#505050" if self.dark_mode else "#e0e0e0"

        if hover_in and not self._hover_in:
            self._hover_in = True
            self.setStyleSheet(
                f"""
                QWidget#otpItem {{
                    background-color: {base_bg};
                    border-radius: 8px;
                    border: 1px solid {border_hover};
                }}
            """
            )
        elif (not hover_in) and self._hover_in:
            self._hover_in = False
            self.setStyleSheet(
                f"""
                QWidget#otpItem {{
                    background-color: {base_bg};
                    border-radius: 8px;
                    border: 1px solid {border_normal};
                }}
            """
            )
    
    def update_otp(self):
        """更新OTP码"""
        # 根据主题确定进度条背景色
        pg_bg = "#505050" if self.dark_mode else "#f0f0f0"

        # 获取当前OTP码
        otp = self.account.get_otp()
        
        # 设置OTP码显示格式为 XXX XXX
        formatted_otp = f"{otp[:3]} {otp[3:]}" if len(otp) == 6 else otp
        self.otp_label.setText(formatted_otp)
        
        # 更新进度条和计时器
        remaining = self.account.get_remaining_seconds()
        progress = self.account.get_progress_percent()
        self.progress_bar.setValue(int(progress))
        
        # 根据用户配置决定是否显示秒数和进度条
        show_seconds = getattr(self.main_window, "config", {}).get("show_seconds", True)

        if show_seconds:
            self.timer_label.show()
            self.progress_bar.show()
            self.timer_label.setText(f"{remaining}秒")
        else:
            self.timer_label.hide()
            self.progress_bar.hide()

        # 如果用户隐藏秒数，同样不需要后面颜色切换逻辑
        if not show_seconds:
            return
        
        # 根据剩余时间仅在必要时更新样式，避免频繁调用setStyleSheet
        if remaining <= 5 and getattr(self, '_last_style', '') != 'danger':
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {pg_bg};
                    border: none;
                    border-radius: 3px;
                }}
                QProgressBar::chunk {{
                    background-color: #FF5252;
                    border-radius: 3px;
                }}
            """)
            self.timer_label.setStyleSheet("color: #FF5252; font-weight: bold;")
            self._last_style = 'danger'
        elif 5 < remaining <= 10 and getattr(self, '_last_style', '') != 'warning':
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {pg_bg};
                    border: none;
                    border-radius: 3px;
                }}
                QProgressBar::chunk {{
                    background-color: #FFD740;
                    border-radius: 3px;
                }}
            """)
            self.timer_label.setStyleSheet("color: #FFB300;")
            self._last_style = 'warning'
        elif remaining > 10 and getattr(self, '_last_style', '') != 'normal':
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {pg_bg};
                    border: none;
                    border-radius: 3px;
                }}
                QProgressBar::chunk {{
                    background-color: #4CAF50;
                    border-radius: 3px;
                }}
            """)
            self.timer_label.setStyleSheet("color: #707070;")
            self._last_style = 'normal'

        # 根据当前配置设置复制提示可见性
        auto_copy_enabled = getattr(self.main_window, "config", {}).get("auto_copy", False)
        self.toggle_copy_hint(auto_copy_enabled)
    
    def copy_otp(self, ev):
        """复制OTP码到剪贴板"""
        # 根据设置判断是否允许自动复制
        if not getattr(self.main_window, "config", {}).get("auto_copy", False):
            return

        otp = self.account.get_otp()
        try:
            pyperclip.copy(otp)
            
            # 添加复制成功的视觉反馈
            original_style = self.otp_label.styleSheet()
            self.otp_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            # 1 秒后恢复原来的样式
            QTimer.singleShot(1000, lambda: self.otp_label.setStyleSheet(original_style))
            
        except Exception:
            pass

    def toggle_copy_hint(self, enabled: bool):
        """根据是否启用自动复制显示或隐藏提示文字，并调整光标形状"""
        if enabled:
            self.copy_hint.show()
            self.otp_label.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.copy_hint.hide()
            self.otp_label.setCursor(Qt.CursorShape.ArrowCursor)
    
    # 删除 hideEvent 中关于动画停止的逻辑，不再需要
    def hideEvent(self, event):
        super().hideEvent(event)
    
    def show_context_menu(self, position):
        """显示上下文菜单"""
        menu = QMenu(self)

        if self.dark_mode:
            menu.setStyleSheet("""
                QMenu {
                    background-color: #3d3d3d;
                    border: 1px solid #505050;
                    border-radius: 4px;
                    padding: 5px;
                    color: #f0f0f0;
                }
                QMenu::item {
                    padding: 5px 25px 5px 20px;
                    border-radius: 3px;
                    color: #f0f0f0;
                }
                QMenu::item:selected {
                    background-color: #505050;
                }
            """)
        else:
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
        
        if self.main_window is not None:
            edit_action = QAction("编辑", self)
            edit_action.triggered.connect(lambda: self.main_window.edit_account(self.index))  # type: ignore[attr-defined]
            menu.addAction(edit_action)

            delete_action = QAction("删除", self)
            delete_action.triggered.connect(lambda: self.main_window.delete_account(self.index))  # type: ignore[attr-defined]
            menu.addAction(delete_action)
        
        menu.exec(self.mapToGlobal(position))
    
    def sizeHint(self):
        """根据 issuer 文本长度动态增加高度，避免裁剪"""
        base_height = 90

        if self.account.issuer:
            metrics = QFontMetrics(self.issuer_label.font())
            # OTP 区域预估宽度 140，边距约 40
            available_width = 380 - 140
            text_width = metrics.horizontalAdvance(self.account.issuer)
            lines = max(1, int(text_width / available_width) + 1)
            extra_height = (lines - 1) * metrics.lineSpacing()
        else:
            extra_height = 0

        total_height = base_height + extra_height
        return QSize(380, total_height)

    def refresh_list_item_size(self):
        """刷新所属 QListWidgetItem 的 sizeHint"""
        if self.main_window and self.main_window.accounts_list:
            for i in range(self.main_window.accounts_list.count()):
                item = self.main_window.accounts_list.item(i)
                if self.main_window.accounts_list.itemWidget(item) is self:
                    item.setSizeHint(self.sizeHint())  # type: ignore[arg-type]
                    # 通知自身重新布局
                    self.updateGeometry()
                    break

    # 当宽度变化时重新计算高度，确保文本不会被进度条遮挡
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 异步调用，确保布局完成后再刷新尺寸
        QTimer.singleShot(0, self.refresh_list_item_size) 