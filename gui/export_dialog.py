#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox,
    QPushButton, QLabel, QLineEdit, QFileDialog,
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox, QWidget
)
from PyQt6.QtCore import Qt
from utils.config import encrypt_data

class CheckableAccountItemWidget(QWidget):
    """自定义的可勾选账户条目，包含一个真实的复选框"""
    def __init__(self, text, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.checkbox = QCheckBox()
        self.label = QLabel(text)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addStretch(1)

    def is_checked(self):
        return self.checkbox.isChecked()

    def set_checked(self, checked):
        self.checkbox.setChecked(checked)

class ExportDialog(QDialog):
    """账户导出对话框"""
    
    def __init__(self, accounts, parent=None):
        super().__init__(parent)
        self.accounts = accounts  # 传入账户列表
        self.selected_indices = []
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("导出账户")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 账户选择区域
        accounts_group = QGroupBox("选择要导出的账户")
        accounts_layout = QVBoxLayout()
        
        # 全选/取消全选
        select_layout = QHBoxLayout()
        self.select_all_cb = QCheckBox("全选")
        self.select_all_cb.clicked.connect(self.toggle_select_all)
        select_layout.addWidget(self.select_all_cb)
        select_layout.addStretch()
        accounts_layout.addLayout(select_layout)
        
        # 账户列表
        self.accounts_list = QListWidget()
        for account in self.accounts:
            item = QListWidgetItem(self.accounts_list)
            widget = CheckableAccountItemWidget(f"{account.name} ({account.issuer})")
            widget.checkbox.stateChanged.connect(self.update_select_all_state)
            item.setSizeHint(widget.sizeHint())
            self.accounts_list.setItemWidget(item, widget)
        
        accounts_layout.addWidget(self.accounts_list)
        accounts_group.setLayout(accounts_layout)
        layout.addWidget(accounts_group)
        
        # 加密选项
        encrypt_group = QGroupBox("加密选项")
        encrypt_layout = QVBoxLayout()
        
        self.encrypt_cb = QCheckBox("使用密码加密导出的数据")
        self.encrypt_cb.toggled.connect(self.toggle_password_field)
        encrypt_layout.addWidget(self.encrypt_cb)
        
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("密码:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setEnabled(False)
        password_layout.addWidget(self.password_edit)
        encrypt_layout.addLayout(password_layout)
        
        confirm_layout = QHBoxLayout()
        confirm_layout.addWidget(QLabel("确认密码:"))
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit.setEnabled(False)
        confirm_layout.addWidget(self.confirm_password_edit)
        encrypt_layout.addLayout(confirm_layout)
        
        encrypt_group.setLayout(encrypt_layout)
        layout.addWidget(encrypt_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        self.export_btn = QPushButton("导出")
        self.export_btn.clicked.connect(self.export_accounts)
        btn_layout.addWidget(self.export_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def update_select_all_state(self):
        """当单个条目状态改变时，更新"全选"复选框的状态"""
        all_checked = True
        for i in range(self.accounts_list.count()):
            widget = self.accounts_list.itemWidget(self.accounts_list.item(i))
            if widget and not widget.is_checked():
                all_checked = False
                break
        
        # 临时阻塞信号，避免触发toggle_select_all导致循环
        self.select_all_cb.blockSignals(True)
        self.select_all_cb.setChecked(all_checked)
        self.select_all_cb.blockSignals(False)

    def toggle_select_all(self, checked):
        """全选/取消全选"""
        for i in range(self.accounts_list.count()):
            widget = self.accounts_list.itemWidget(self.accounts_list.item(i))
            if widget:
                widget.set_checked(checked)
    
    def toggle_password_field(self, checked):
        """切换密码字段状态"""
        self.password_edit.setEnabled(checked)
        self.confirm_password_edit.setEnabled(checked)
    
    def get_selected_accounts(self):
        """获取选中的账户"""
        selected_accounts = []
        for i in range(self.accounts_list.count()):
            widget = self.accounts_list.itemWidget(self.accounts_list.item(i))
            if widget and widget.is_checked():
                selected_accounts.append(self.accounts[i])
                self.selected_indices.append(i)
        return selected_accounts
    
    def export_accounts(self):
        """导出账户"""
        selected_accounts = self.get_selected_accounts()
        
        if not selected_accounts:
            QMessageBox.warning(self, "警告", "请至少选择一个账户进行导出")
            return
        
        # 验证密码
        if self.encrypt_cb.isChecked():
            password = self.password_edit.text()
            confirm_password = self.confirm_password_edit.text()
            
            if not password:
                QMessageBox.warning(self, "警告", "请输入密码")
                return
                
            if password != confirm_password:
                QMessageBox.warning(self, "警告", "两次输入的密码不一致")
                return
        
        # 选择保存位置
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "保存导出文件", 
            "", 
            "LightAuth 账户文件 (*.lauth);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
            
        # 如果没有扩展名，添加 .lauth
        if not os.path.splitext(file_path)[1]:
            file_path += ".lauth"
        
        # 准备导出数据
        export_data = {
            "version": "1.0",
            "encrypted": self.encrypt_cb.isChecked(),
            "accounts": [account.to_dict() for account in selected_accounts]
        }
        
        try:
            if self.encrypt_cb.isChecked():
                # 加密导出
                encrypted_data = encrypt_data(export_data, self.password_edit.text())
                with open(file_path, 'wb') as f:
                    f.write(encrypted_data)
            else:
                # 不加密直接保存 JSON
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=4)
                    
            QMessageBox.information(
                self, 
                "导出成功", 
                f"成功导出 {len(selected_accounts)} 个账户到 {file_path}"
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出过程中发生错误: {str(e)}") 