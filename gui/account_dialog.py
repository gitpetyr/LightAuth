#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QDialogButtonBox,
    QTabWidget, QWidget, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

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
        
        # 扫描二维码标签页
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
        
        # 如果父窗口处于深色主题，则覆盖本对话框样式为亮色，以确保文字可见
        parent = self.parent()
        dark_mode = False
        if parent and hasattr(parent, "config"):
            dark_mode = parent.config.get("theme", "light") == "dark"  # type: ignore[attr-defined]

        if dark_mode:
            self.setStyleSheet(
                """
                QDialog {
                    background-color: #ffffff;
                    color: #000000;
                }
                QWidget {
                    color: #000000;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                }
                QTabBar::tab {
                    background: #e0e0e0;
                    color: #000000;
                    padding: 6px;
                }
                QTabBar::tab:selected {
                    background: #ffffff;
                }
                QPushButton {
                    background-color: #4184f3;
                    color: #ffffff;
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
                """
            )
    
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
        
        # 如果是编辑模式，则填充现有数据但隐藏/锁定密钥
        if self.account:
            self.name_edit.setText(self.account.name)
            self.issuer_edit.setText(self.account.issuer)

            # 隐藏真实密钥，禁止查看和修改
            self.secret_edit.setText("********")
            self.secret_edit.setReadOnly(True)
            self.secret_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.generate_button.setEnabled(False)
    
    def create_qr_tab(self):
        """创建扫描二维码标签页"""
        layout = QVBoxLayout(self.qr_tab)
        
        # 说明
        info_label = QLabel("请选择扫描方式：")
        layout.addWidget(info_label)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        self.camera_btn = QPushButton("相机扫描")
        self.camera_btn.clicked.connect(self.scan_by_camera)
        btn_layout.addWidget(self.camera_btn)
        
        self.screen_btn = QPushButton("屏幕扫描")
        self.screen_btn.clicked.connect(self.scan_by_screen)
        btn_layout.addWidget(self.screen_btn)
        
        self.image_btn = QPushButton("图片扫描")
        self.image_btn.clicked.connect(self.scan_by_image)
        btn_layout.addWidget(self.image_btn)
        
        layout.addLayout(btn_layout)
        
        # 扫描结果显示
        self.scan_result_label = QLabel()
        self.scan_result_label.setWordWrap(True)
        self.scan_result_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.scan_result_label)
        
        layout.addStretch(1)
    
    def generate_secret(self):
        """生成新的密钥"""
        from models.otp_model import OTPModel
        secret = OTPModel.generate_secret()
        self.secret_edit.setText(secret)
    
    def accept(self):
        """确认对话框"""
        name = self.name_edit.text().strip()
        issuer = self.issuer_edit.text().strip()
        
        # 处理密钥：新增模式读取用户输入，编辑模式保持原密钥
        if self.account is None:
            secret_input = self.secret_edit.text().strip().upper().replace(" ", "")
            secret = secret_input
        else:
            secret = self.account.secret  # 不允许修改
        
        # 验证输入
        if not name:
            QMessageBox.warning(self, "输入错误", "请输入账户名称")
            return
        if self.account is None and not secret:
            QMessageBox.warning(self, "输入错误", "请输入密钥")
            return
        
        # 新增模式下验证密钥有效性；编辑模式跳过
        if self.account is None:
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

    # ----------------------- 扫描相关槽函数 -----------------------
    def _apply_scanned_data(self, data: str):
        """解析扫描到的数据并填充输入框"""
        from utils.qr_utils import parse_otp_uri

        parsed = parse_otp_uri(data)
        if parsed:
            self.name_edit.setText(parsed.get("name", ""))
            self.issuer_edit.setText(parsed.get("issuer", ""))
            self.secret_edit.setText(parsed.get("secret", ""))
            self.scan_result_label.setText(f"已解析二维码：\n名称: {parsed.get('name')}\n发行方: {parsed.get('issuer')}\n密钥: {parsed.get('secret')}")
        else:
            # 如果无法解析为OTP URI，则直接填入密钥字段
            self.secret_edit.setText(data)
            self.scan_result_label.setText("无法解析为OTP URI，已将内容填入密钥字段。")

    def scan_by_camera(self):
        """通过相机扫描二维码"""
        try:
            from gui.qr_scanner_dialogs import CameraScanDialog
        except ImportError as e:
            QMessageBox.critical(self, "错误", f"无法导入扫描模块: {str(e)}")
            return

        dlg = CameraScanDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_selected_data()
            if data:
                self._apply_scanned_data(data)

    def scan_by_screen(self):
        """通过屏幕截图扫描二维码"""
        try:
            from gui.qr_scanner_dialogs import ScreenScanDialog
        except ImportError as e:
            QMessageBox.critical(self, "错误", f"无法导入扫描模块: {str(e)}")
            return

        dlg = ScreenScanDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_selected_data()
            if data:
                self._apply_scanned_data(data)

    def scan_by_image(self):
        """通过本地图片扫描二维码"""
        try:
            from gui.qr_scanner_dialogs import ImageScanDialog
        except ImportError as e:
            QMessageBox.critical(self, "错误", f"无法导入扫描模块: {str(e)}")
            return

        dlg = ImageScanDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_selected_data()
            if data:
                self._apply_scanned_data(data) 