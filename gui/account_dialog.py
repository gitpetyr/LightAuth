#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QDialogButtonBox,
    QTabWidget, QWidget, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

from models.otp_model import OTPAccount

class AccountDialog(QDialog):
    """账户对话框，用于添加或编辑OTP账户"""
    
    def __init__(self, parent=None, account=None):
        super().__init__(parent)
        self.account = account  # 如果是编辑模式，则提供一个现有账户
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 设置窗口标题和尺寸
        self.setWindowTitle("添加账户" if self.account is None else "编辑账户")
        self.resize(400, 300)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 手动输入标签页
        self.manual_tab = QWidget()
        self.create_manual_tab()
        self.tab_widget.addTab(self.manual_tab, "手动输入")
        
        # 扫描二维码标签页（暂未实现）
        self.qr_tab = QWidget()
        self.create_qr_tab()
        self.tab_widget.addTab(self.qr_tab, "扫描二维码")
        
        main_layout.addWidget(self.tab_widget)
        
        # 按钮区域
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(self.button_box)
    
    def create_manual_tab(self):
        """创建手动输入标签页"""
        layout = QVBoxLayout(self.manual_tab)
        
        form_layout = QFormLayout()
        
        # 账户名称
        self.name_edit = QLineEdit()
        form_layout.addRow("账户名称:", self.name_edit)
        
        # 发行方
        self.issuer_edit = QLineEdit()
        form_layout.addRow("发行方:", self.issuer_edit)
        
        # 密钥
        self.secret_edit = QLineEdit()
        self.secret_edit.setPlaceholderText("请输入BASE32编码的密钥")
        
        # 密钥验证器 - 只允许输入BASE32字符
        base32_regex = QRegularExpression("[A-Z2-7]+")
        base32_validator = QRegularExpressionValidator(base32_regex)
        self.secret_edit.setValidator(base32_validator)
        
        form_layout.addRow("密钥:", self.secret_edit)
        
        # 生成新密钥按钮
        self.generate_button = QPushButton("生成新密钥")
        self.generate_button.clicked.connect(self.generate_secret)
        form_layout.addRow("", self.generate_button)
        
        layout.addLayout(form_layout)
        
        # 如果是编辑模式，则填充现有数据
        if self.account:
            self.name_edit.setText(self.account.name)
            self.issuer_edit.setText(self.account.issuer)
            self.secret_edit.setText(self.account.secret)
    
    def create_qr_tab(self):
        """创建扫描二维码标签页"""
        layout = QVBoxLayout(self.qr_tab)
        
        # 提示标签
        label = QLabel("该功能尚未实现，请使用手动输入标签页。")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
    
    def generate_secret(self):
        """生成新的密钥"""
        from models.otp_model import OTPModel
        secret = OTPModel.generate_secret()
        self.secret_edit.setText(secret)
    
    def accept(self):
        """确认对话框"""
        name = self.name_edit.text().strip()
        issuer = self.issuer_edit.text().strip()
        secret = self.secret_edit.text().strip().upper().replace(" ", "")
        
        # 验证输入
        if not name:
            QMessageBox.warning(self, "输入错误", "请输入账户名称")
            return
        
        if not secret:
            QMessageBox.warning(self, "输入错误", "请输入密钥")
            return
        
        # 验证密钥是否有效
        from models.otp_model import OTPModel
        if not OTPModel.is_valid_secret(secret):
            QMessageBox.warning(self, "输入错误", "密钥格式不正确，请确保是有效的BASE32编码")
            return
        
        # 创建账户对象
        self.result_account = OTPAccount(name, secret, issuer)
        
        super().accept()
    
    def get_account(self):
        """获取账户对象"""
        return getattr(self, "result_account", None) 