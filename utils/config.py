#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib

# 配置文件路径 - 存储在当前目录下
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
DATA_FILE = os.path.join(CONFIG_DIR, "accounts.dat")

# 默认配置
DEFAULT_CONFIG = {
    "theme": "light",
    "auto_copy": False,
    "show_seconds": True,
    "encryption_enabled": False,
    "encryption_password_hash": ""  # 存储密码的哈希值
}

def init_config():
    """初始化配置目录和文件"""
    # 创建配置目录
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    
    # 创建配置文件
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
    
    # 确保数据文件存在
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'wb') as f:
            f.write(b'')

def load_config():
    """加载配置"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG

def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def hash_password(password):
    """创建密码的安全哈希值
    
    Args:
        password: 原始密码字符串
        
    Returns:
        哈希后的密码字符串
    """
    salt = b'LightAuth_Security_Salt'  # 固定盐值
    # 使用SHA-256哈希算法
    hash_obj = hashlib.sha256()
    hash_obj.update(salt + password.encode('utf-8'))
    return hash_obj.hexdigest()

def verify_password(password, password_hash):
    """验证密码
    
    Args:
        password: 输入的密码
        password_hash: 存储的哈希值
        
    Returns:
        如果密码匹配返回True，否则返回False
    """
    return hash_password(password) == password_hash

def get_encryption_key(password=""):
    """生成加密密钥"""
    # 使用密码或默认盐值生成密钥
    salt = b'LightAuth_Salt_Value' if not password else password.encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(b'LightAuth'))
    return key

def encrypt_data(data, password=""):
    """加密数据"""
    key = get_encryption_key(password)
    fernet = Fernet(key)
    return fernet.encrypt(json.dumps(data).encode())

def decrypt_data(encrypted_data, password=""):
    """解密数据"""
    if not encrypted_data:
        return []
        
    key = get_encryption_key(password)
    fernet = Fernet(key)
    try:
        decrypted_data = fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    except Exception:
        return []

def load_accounts(password=""):
    """加载账户数据"""
    try:
        with open(DATA_FILE, 'rb') as f:
            encrypted_data = f.read()
        return decrypt_data(encrypted_data, password)
    except Exception:
        return []

def save_accounts(accounts, password=""):
    """保存账户数据"""
    encrypted_data = encrypt_data(accounts, password)
    with open(DATA_FILE, 'wb') as f:
        f.write(encrypted_data) 