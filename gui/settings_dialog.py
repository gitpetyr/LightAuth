#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QDialogButtonBox,
    QCheckBox, QComboBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt


class SettingsDialog(QDialog):
    """设置对话框，用于管理应用设置"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config.copy()  # 复制一份配置，避免直接修改原配置
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 设置窗口标题和尺寸
        self.setWindowTitle("设置")
        self.resize(400, 350)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 外观选项
        appearance_group = QGroupBox("外观")
        appearance_layout = QFormLayout()
        
        # 主题选择
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("浅色", "light")
        self.theme_combo.addItem("深色", "dark")
        
        # 设置当前选中项
        current_theme = self.config.get("theme", "light")
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        appearance_layout.addRow("主题:", self.theme_combo)
        appearance_group.setLayout(appearance_layout)
        main_layout.addWidget(appearance_group)
        
        # 行为选项
        behavior_group = QGroupBox("行为")
        behavior_layout = QVBoxLayout()
        
        # 自动复制选项
        self.auto_copy_check = QCheckBox("点击时自动复制验证码到剪贴板")
        self.auto_copy_check.setChecked(self.config.get("auto_copy", False))
        behavior_layout.addWidget(self.auto_copy_check)
        
        # 显示秒数选项
        self.show_seconds_check = QCheckBox("显示验证码剩余有效秒数")
        self.show_seconds_check.setChecked(self.config.get("show_seconds", True))
        behavior_layout.addWidget(self.show_seconds_check)
        
        behavior_group.setLayout(behavior_layout)
        main_layout.addWidget(behavior_group)
        
        # 安全选项
        security_group = QGroupBox("安全")
        security_layout = QVBoxLayout()
        
        # 启用加密选项
        self.encryption_check = QCheckBox("启用安全加密 (启动时需要密码)")
        self.encryption_check.setChecked(self.config.get("encryption_enabled", False))
        self.encryption_check.toggled.connect(self.toggle_encryption)
        security_layout.addWidget(self.encryption_check)
        
        # 密码设置
        password_form = QFormLayout()
        
        self.current_password_edit = QLineEdit()
        self.current_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password_edit.setPlaceholderText("如果已设置，请输入当前密码")
        password_form.addRow("当前密码:", self.current_password_edit)
        
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_edit.setPlaceholderText("留空则保持原密码不变")
        password_form.addRow("新密码:", self.new_password_edit)
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit.setPlaceholderText("留空则保持原密码不变")
        password_form.addRow("确认新密码:", self.confirm_password_edit)
        
        security_layout.addLayout(password_form)
        
        # 初始状态
        self.update_password_fields()
        
        security_group.setLayout(security_layout)
        main_layout.addWidget(security_group)
        
        # 按钮区域
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(self.button_box)
    
    def toggle_encryption(self, checked):
        """切换加密设置"""
        self.update_password_fields()
    
    def update_password_fields(self):
        """更新密码字段的可用性"""
        enabled = self.encryption_check.isChecked()
        
        # 如果是首次启用加密，不需要当前密码
        first_time = not self.config.get("encryption_enabled", False) and enabled
        
        self.current_password_edit.setEnabled(enabled and not first_time)
        # QLineEdit doesn't have setRequired method, so we'll just use setEnabled
        
        self.new_password_edit.setEnabled(enabled)
        self.confirm_password_edit.setEnabled(enabled)
    
    def validate_passwords(self):
        """验证密码"""
        if not self.encryption_check.isChecked():
            return True
            
        # 如果新密码为空，则不更改密码，直接使用原密码
        if not self.new_password_edit.text():
            # 不显示警告，允许不修改密码
            return True
            
        # 检查两次输入的密码是否一致
        if self.new_password_edit.text() != self.confirm_password_edit.text():
            QMessageBox.warning(self, "警告", "两次输入的密码不一致")
            return False
            
        # 如果之前已经启用了加密，验证当前密码
        if self.config.get("encryption_enabled", False):
            # 当前密码验证应该在MainWindow中进行，这里只做形式验证
            if not self.current_password_edit.text():
                QMessageBox.warning(self, "警告", "请输入当前密码")
                return False
        
        return True
    
    def accept(self):
        """确认设置"""
        # 验证密码
        if not self.validate_passwords():
            return
            
        # 保存主题设置
        theme_index = self.theme_combo.currentIndex()
        self.config["theme"] = self.theme_combo.itemData(theme_index)
        
        # 保存行为设置
        self.config["auto_copy"] = self.auto_copy_check.isChecked()
        self.config["show_seconds"] = self.show_seconds_check.isChecked()
        
        # 保存加密设置
        self.config["encryption_enabled"] = self.encryption_check.isChecked()
        
        # 将新密码保存到临时变量中，以便主窗口处理
        if self.encryption_check.isChecked():
            self.config["temp_current_password"] = self.current_password_edit.text()
            self.config["temp_new_password"] = self.new_password_edit.text()
        
        super().accept()
    
    def get_settings(self):
        """获取设置"""
        return self.config 