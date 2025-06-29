#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox,
    QPushButton, QLabel, QLineEdit, QFileDialog,
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox, QWidget
)
from PySide6.QtCore import Qt
from utils.config import decrypt_data
from models.otp_model import OTPAccount

class CheckableAccountItemWidget(QWidget):
    """自定义的可勾选账户条目，包含一个真实的复选框"""
    def __init__(self, text, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)  # 默认勾选
        self.label = QLabel(text)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addStretch(1)

    def is_checked(self):
        return self.checkbox.isChecked()

    def set_checked(self, checked):
        self.checkbox.setChecked(checked)

class ImportDialog(QDialog):
    """账户导入对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.import_data = None
        self.accounts_to_import = []
        self.is_encrypted = False
        self.raw_file_data = None
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("导入账户")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 文件选择区域
        file_group = QGroupBox("选择文件")
        file_layout = QHBoxLayout()
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        file_layout.addWidget(self.file_path_edit)
        
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 密码区域
        password_group = QGroupBox("密码")
        password_layout = QVBoxLayout()
        
        self.password_label = QLabel("导入文件已加密，请输入密码:")
        password_layout.addWidget(self.password_label)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_edit)
        
        self.decrypt_btn = QPushButton("解密")
        self.decrypt_btn.clicked.connect(self.decrypt_file)
        password_layout.addWidget(self.decrypt_btn)
        
        password_group.setLayout(password_layout)
        password_group.setVisible(False)  # 初始隐藏
        self.password_group = password_group
        layout.addWidget(password_group)
        
        # 账户选择区域
        accounts_group = QGroupBox("选择要导入的账户")
        accounts_layout = QVBoxLayout()
        
        # 全选/取消全选
        select_layout = QHBoxLayout()
        self.select_all_cb = QCheckBox("全选")
        self.select_all_cb.setChecked(True)
        self.select_all_cb.clicked.connect(self.toggle_select_all)
        select_layout.addWidget(self.select_all_cb)
        select_layout.addStretch()
        accounts_layout.addLayout(select_layout)
        
        # 账户列表
        self.accounts_list = QListWidget()
        accounts_layout.addWidget(self.accounts_list)
        
        accounts_group.setLayout(accounts_layout)
        accounts_group.setVisible(False)  # 初始隐藏
        self.accounts_group = accounts_group
        layout.addWidget(accounts_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("导入")
        self.import_btn.clicked.connect(self.import_accounts)
        self.import_btn.setEnabled(False)
        btn_layout.addWidget(self.import_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "打开导入文件", 
            "", 
            "LightAuth 账户文件 (*.lauth);;所有文件 (*.*)"
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """加载文件"""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # 尝试作为JSON加载
            try:
                self.import_data = json.loads(file_data.decode('utf-8'))
                self.is_encrypted = self.import_data.get('encrypted', False)
                
                if self.is_encrypted:
                    # 文件声明加密但内容为JSON，这是一个错误
                    QMessageBox.warning(self, "警告", "文件格式错误：声明为加密但内容未加密")
                    return
                    
                # 显示账户列表
                self.show_accounts_list()
                
            except json.JSONDecodeError:
                # 可能是加密文件
                self.is_encrypted = True
                self.password_group.setVisible(True)
                self.raw_file_data = file_data
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载文件: {str(e)}")
    
    def decrypt_file(self):
        """解密文件"""
        if not self.raw_file_data:
            return
            
        password = self.password_edit.text()
        if not password:
            QMessageBox.warning(self, "警告", "请输入密码")
            return
            
        try:
            self.import_data = decrypt_data(self.raw_file_data, password)
            
            if not self.import_data:
                QMessageBox.warning(self, "警告", "密码错误或文件格式不正确")
                return
                
            # 显示账户列表
            self.show_accounts_list()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"解密过程中发生错误: {str(e)}")
    
    def show_accounts_list(self):
        """显示账户列表"""
        if not self.import_data or 'accounts' not in self.import_data:
            QMessageBox.warning(self, "警告", "文件中没有找到账户数据")
            return
            
        # 清空账户列表
        self.accounts_list.clear()
        
        # 添加账户到列表
        for account_data in self.import_data['accounts']:
            name = account_data.get('name', '未命名')
            issuer = account_data.get('issuer', '')
            display_text = f"{name} ({issuer})" if issuer else name
            
            item = QListWidgetItem(self.accounts_list)
            widget = CheckableAccountItemWidget(display_text)
            widget.checkbox.stateChanged.connect(self.update_select_all_state)
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, account_data) # 仍然需要存储原始数据
            self.accounts_list.setItemWidget(item, widget)
        
        # 显示账户选择区域
        self.password_group.setVisible(False)
        self.accounts_group.setVisible(True)
        self.import_btn.setEnabled(True)
    
    def update_select_all_state(self):
        """当单个条目状态改变时，更新"全选"复选框的状态"""
        all_checked = True
        for i in range(self.accounts_list.count()):
            widget = self.accounts_list.itemWidget(self.accounts_list.item(i))
            if widget and not widget.is_checked():
                all_checked = False
                break
        
        self.select_all_cb.blockSignals(True)
        self.select_all_cb.setChecked(all_checked)
        self.select_all_cb.blockSignals(False)
    
    def toggle_select_all(self, checked):
        """全选/取消全选"""
        for i in range(self.accounts_list.count()):
            widget = self.accounts_list.itemWidget(self.accounts_list.item(i))
            if widget:
                widget.set_checked(checked)
    
    def import_accounts(self):
        """导入账户"""
        self.accounts_to_import = []
        
        # 收集选中的账户
        for i in range(self.accounts_list.count()):
            item = self.accounts_list.item(i) # item用于获取数据
            widget = self.accounts_list.itemWidget(item) # widget用于获取勾选状态
            if widget and widget.is_checked():
                account_data = item.data(Qt.ItemDataRole.UserRole)
                if account_data:
                    otp_account = OTPAccount.from_dict(account_data)
                    self.accounts_to_import.append(otp_account)
        
        if not self.accounts_to_import:
            QMessageBox.warning(self, "警告", "请至少选择一个账户进行导入")
            return
            
        self.accept()
    
    def get_imported_accounts(self):
        """获取要导入的账户"""
        return self.accounts_to_import 