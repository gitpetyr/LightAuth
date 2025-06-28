#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import pyotp
import qrcode
from io import BytesIO
from PIL import Image, ImageQt
from PyQt6.QtGui import QPixmap

class OTPAccount:
    """OTP账户类，管理单个OTP账户"""
    
    def __init__(self, name, secret, issuer="", icon=""):
        self.name = name            # 账户名称
        self.secret = secret        # 密钥
        self.issuer = issuer        # 发行方
        self.icon = icon            # 图标
        self.totp = pyotp.TOTP(secret)
    
    def get_otp(self):
        """获取当前OTP码"""
        return self.totp.now()
    
    def get_remaining_seconds(self):
        """获取当前OTP码的剩余有效秒数"""
        return 30 - int(time.time()) % 30
    
    def get_progress_percent(self):
        """获取当前OTP码有效期进度百分比"""
        return (30 - self.get_remaining_seconds()) / 30 * 100
    
    def get_uri(self):
        """获取OTP URI"""
        return pyotp.totp.TOTP(self.secret).provisioning_uri(
            name=self.name,
            issuer_name=self.issuer or "LightAuth"
        )
    
    def get_qrcode(self, size=200):
        """生成QR码图像"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.get_uri())
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        
        qimage = ImageQt.ImageQt(Image.open(buffer))
        return QPixmap.fromImage(qimage)
    
    def to_dict(self):
        """将账户信息转换为字典"""
        return {
            "name": self.name,
            "secret": self.secret,
            "issuer": self.issuer,
            "icon": self.icon
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建账户"""
        return cls(
            name=data.get("name", ""),
            secret=data.get("secret", ""),
            issuer=data.get("issuer", ""),
            icon=data.get("icon", "")
        )


class OTPModel:
    """OTP模型类，管理所有OTP账户"""
    
    def __init__(self):
        self.accounts = []
    
    def add_account(self, account):
        """添加账户"""
        self.accounts.append(account)
    
    def remove_account(self, index):
        """删除账户"""
        if 0 <= index < len(self.accounts):
            del self.accounts[index]
    
    def update_account(self, index, account):
        """更新账户"""
        if 0 <= index < len(self.accounts):
            self.accounts[index] = account
    
    def get_account(self, index):
        """获取指定索引的账户"""
        if 0 <= index < len(self.accounts):
            return self.accounts[index]
        return None
    
    def get_accounts(self):
        """获取所有账户"""
        return self.accounts
    
    def count(self):
        """获取账户数量"""
        return len(self.accounts)
    
    def to_list(self):
        """将账户列表转换为可序列化的列表"""
        return [account.to_dict() for account in self.accounts]
    
    @classmethod
    def from_list(cls, data_list):
        """从数据列表创建模型"""
        model = cls()
        for account_data in data_list:
            model.add_account(OTPAccount.from_dict(account_data))
        return model
    
    @staticmethod
    def generate_secret():
        """生成新的密钥"""
        return pyotp.random_base32()
    
    @staticmethod
    def is_valid_secret(secret):
        """验证密钥是否有效"""
        try:
            pyotp.TOTP(secret).now()
            return True
        except Exception:
            return False 