#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
import os
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QPushButton, QLabel, QScrollArea,
    QListWidget, QListWidgetItem, QSplitter, 
    QMessageBox, QMenu, QDialog, QInputDialog, QLineEdit,
    QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QAction, QIcon, QFont, QPixmap

from models.otp_model import OTPModel, OTPAccount
from utils.config import (
    load_config, save_config, load_accounts, save_accounts, 
    hash_password, verify_password
)
from gui.account_dialog import AccountDialog
from gui.settings_dialog import SettingsDialog
from gui.otp_item_widget import OTPItemWidget
from gui.export_dialog import ExportDialog
from gui.import_dialog import ImportDialog
from gui.styles import LIGHT_STYLE, DARK_STYLE
from gui.animations import FadeAnimation, SlideAnimation


class MainWindow(QMainWindow):
    """主窗口"""
    
    update_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.model = OTPModel()
        self.config = load_config()
        self.encryption_password = ""
        self.animations = []  # 保存动画对象的引用，避免被垃圾回收
        
        # 设置应用图标
        self.setup_icons()
        
        # 应用样式
        self.apply_theme()
        
        # 检查是否启用加密
        if self.config.get("encryption_enabled", False):
            self.prompt_for_password()
        else:
            self.load_application_data()
        
        self.init_ui()
        
        # 设置更新计时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_otp_codes)
        self.timer.start(1000)  # 每秒更新一次
    
    def setup_icons(self):
        """设置应用图标"""
        # 检查src目录中的图标
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "src", "LightAuth_logo.png")
        
        if os.path.exists(icon_path):
            self.app_icon = QIcon(icon_path)
            self.setWindowIcon(self.app_icon)
    
    def apply_theme(self):
        """应用主题样式"""
        theme = self.config.get("theme", "light")
        if theme == "dark":
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)
    
    def prompt_for_password(self, retry=False):
        """提示用户输入密码"""
        # 获取存储的密码哈希值
        stored_hash = self.config.get("encryption_password_hash", "")
        
        # 如果没有设置密码哈希，则无需密码即可加载
        if not stored_hash:
            self.load_application_data()
            return
        
        # 提示消息
        message = "请输入解锁密码:" if not retry else "密码错误，请重试:"
        
        # 弹出密码输入框
        password, ok = QInputDialog.getText(
            self, "安全验证", message, 
            QLineEdit.EchoMode.Password
        )
        
        if ok:
            # 验证密码
            if verify_password(password, stored_hash):
                self.encryption_password = password
                self.load_application_data()
            else:
                # 密码错误，重试
                self.prompt_for_password(retry=True)
        else:
            # 用户取消，退出应用
            self.close()
    
    def load_application_data(self):
        """加载应用数据"""
        # 加载账户数据，如果启用了加密，则使用用户输入的密码
        accounts_data = load_accounts(self.encryption_password)
        self.model = OTPModel.from_list(accounts_data)
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("LightAuth - OTP认证器")
        self.setMinimumSize(400, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 标题和Logo
        header_layout = QHBoxLayout()
        
        # 添加Logo
        logo_label = QLabel()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "src", "LightAuth_logo.png")
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            header_layout.addWidget(logo_label)
        
        # 标题
        title_label = QLabel("LightAuth 认证器")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # 账户列表
        self.accounts_list = QListWidget()
        self.accounts_list.setSpacing(8)
        self.accounts_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        main_layout.addWidget(self.accounts_list)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.add_btn = QPushButton("添加账户")
        self.add_btn.setIcon(QIcon(os.path.join(base_dir, "src", "LightAuth_logo.png")))
        self.add_btn.clicked.connect(self.add_account)
        btn_layout.addWidget(self.add_btn)
        
        self.settings_btn = QPushButton("设置")
        self.settings_btn.clicked.connect(self.open_settings)
        btn_layout.addWidget(self.settings_btn)
        
        main_layout.addLayout(btn_layout)
        
        # 创建菜单
        self.create_menus()
        
        # 更新账户列表
        self.update_accounts_list()
        
        # 应用进入动画
        self.animate_startup()
    
    def animate_startup(self):
        """应用启动动画"""
        # 渐显动画
        for widget in [self.centralWidget()]:
            anim = FadeAnimation.fade_in(widget, duration=500)
            self.animations.append(anim)
    
    def create_menus(self):
        """创建菜单"""
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件")
        
        add_action = QAction("添加账户", self)
        add_action.triggered.connect(self.add_account)
        file_menu.addAction(add_action)
        
        import_action = QAction("导入账户", self)
        import_action.triggered.connect(self.import_accounts)
        file_menu.addAction(import_action)
        
        export_action = QAction("导出账户", self)
        export_action.triggered.connect(self.export_accounts)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = self.menuBar().addMenu("编辑")
        
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)
        
        # 帮助菜单
        help_menu = self.menuBar().addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def update_accounts_list(self):
        """更新账户列表"""
        self.accounts_list.clear()
        
        for idx, account in enumerate(self.model.get_accounts()):
            item = QListWidgetItem()
            widget = OTPItemWidget(account, idx, self)
            item.setSizeHint(widget.sizeHint())
            
            self.accounts_list.addItem(item)
            self.accounts_list.setItemWidget(item, widget)
            
            # 添加列表项动画
            anim = SlideAnimation.slide_in(widget, direction="right", duration=200 + idx * 50)
            self.animations.append(anim)
    
    def update_otp_codes(self):
        """更新所有OTP码"""
        for idx in range(self.accounts_list.count()):
            item = self.accounts_list.item(idx)
            widget = self.accounts_list.itemWidget(item)
            if widget:
                widget.update_otp()
    
    def add_account(self):
        """添加新账户"""
        dialog = AccountDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            account = dialog.get_account()
            self.model.add_account(account)
            self.save_accounts()
            self.update_accounts_list()
    
    def edit_account(self, index):
        """编辑账户"""
        account = self.model.get_account(index)
        if account:
            dialog = AccountDialog(self, account)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                edited_account = dialog.get_account()
                self.model.update_account(index, edited_account)
                self.save_accounts()
                self.update_accounts_list()
    
    def delete_account(self, index):
        """删除账户"""
        account = self.model.get_account(index)
        if account:
            reply = QMessageBox.question(
                self, 
                "确认删除", 
                f"确定要删除账户 '{account.name}' 吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # 获取要删除的部件
                item = self.accounts_list.item(index)
                widget = self.accounts_list.itemWidget(item)
                
                # 应用删除动画
                def remove_item():
                    self.model.remove_account(index)
                    self.save_accounts()
                    self.update_accounts_list()
                
                if widget:
                    anim = SlideAnimation.slide_out(widget, direction="left", finished_callback=remove_item)
                    self.animations.append(anim)
                else:
                    remove_item()
    
    def open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_config = dialog.get_settings()
            
            # 处理加密设置
            if new_config.get("encryption_enabled", False):
                current_password = new_config.get("temp_current_password", "")
                new_password = new_config.get("temp_new_password", "")
                
                # 验证当前密码（如果之前已启用加密）
                if self.config.get("encryption_enabled", False):
                    stored_hash = self.config.get("encryption_password_hash", "")
                    if not verify_password(current_password, stored_hash):
                        QMessageBox.critical(self, "错误", "当前密码不正确")
                        return
                
                # 如果提供了新密码，才更新密码哈希
                if new_password:
                    # 设置新的密码哈希
                    new_config["encryption_password_hash"] = hash_password(new_password)
                    
                    # 如果更改了密码，需要重新加密数据
                    self.encryption_password = new_password
                    self.save_accounts()
                elif not self.config.get("encryption_enabled", False):
                    # 第一次启用加密但未提供密码（不应该发生，但添加防护）
                    if not self.config.get("encryption_password_hash", ""):
                        # 使用一个默认密码，这种情况理论上不应该发生
                        default_password = "default"
                        new_config["encryption_password_hash"] = hash_password(default_password)
                        self.encryption_password = default_password
                        self.save_accounts()
                        QMessageBox.warning(self, "警告", "已使用默认密码启用加密，请尽快在设置中修改密码")
            
            # 清除临时密码字段
            if "temp_current_password" in new_config:
                del new_config["temp_current_password"]
            if "temp_new_password" in new_config:
                del new_config["temp_new_password"]
            
            # 检查是否更改了主题
            old_theme = self.config.get("theme", "light")
            new_theme = new_config.get("theme", "light")
            
            # 保存新的配置
            self.config = new_config
            save_config(self.config)
            
            # 如果主题改变，应用新主题
            if old_theme != new_theme:
                self.apply_theme()
    
    def save_accounts(self):
        """保存账户数据，使用加密密码（如果启用）"""
        save_accounts(self.model.to_list(), self.encryption_password)
    
    def import_accounts(self):
        """导入账户"""
        dialog = ImportDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            imported_accounts = dialog.get_imported_accounts()
            
            if imported_accounts:
                # 添加导入的账户
                for account in imported_accounts:
                    self.model.add_account(account)
                
                # 保存并更新界面
                self.save_accounts()
                self.update_accounts_list()
                
                QMessageBox.information(
                    self, 
                    "导入成功", 
                    f"成功导入 {len(imported_accounts)} 个账户"
                )
    
    def export_accounts(self):
        """导出账户"""
        if self.model.count() == 0:
            QMessageBox.information(self, "提示", "没有可导出的账户")
            return
            
        dialog = ExportDialog(self.model.get_accounts(), self)
        dialog.exec()
    
    def show_about(self):
        """显示关于对话框"""
        # 获取Logo路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "src", "LightAuth_logo.png")
        
        about_text = "LightAuth - 轻量级OTP认证器\n\n"
        about_text += "版本: 1.0.0\n"
        about_text += "作者: LightAuth Team\n\n"
        about_text += "一个基于Python和PyQt6构建的轻量级OTP认证器应用程序"
        
        # 使用带Logo的消息框
        about_box = QMessageBox(self)
        about_box.setWindowTitle("关于 LightAuth")
        about_box.setText(about_text)
        about_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            about_box.setIconPixmap(scaled_pixmap)
        
        about_box.exec()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存账户数据
        self.save_accounts()
        event.accept() 