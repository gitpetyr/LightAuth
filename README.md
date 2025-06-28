# LightAuth - 轻量级OTP认证器

一个基于Python3和PyQt6构建的轻量级OTP认证器应用程序，类似于Android上的Google Authenticator或Microsoft Authenticator。

## 功能特性

- 基于时间的一次性密码(TOTP)生成
- 添加、编辑和删除认证账户
- 手动输入密钥或扫描二维码添加账户
- 密码剩余有效时间倒计时
- 本地加密存储账户信息

## 项目结构

```
LightAuth/
├── main.py                # 主程序入口
├── gui/                   # GUI界面模块
│   ├── __init__.py
│   ├── main_window.py     # 主窗口
│   ├── account_dialog.py  # 账户对话框
│   ├── settings_dialog.py # 设置对话框
│   └── otp_item_widget.py # OTP项目小部件
├── models/                # 数据模型
│   ├── __init__.py
│   └── otp_model.py       # OTP模型
├── utils/                 # 工具函数
│   ├── __init__.py
│   └── config.py          # 配置管理
└── resources/             # 资源文件
    └── __init__.py
```

## 依赖项

- Python 3.6+
- PyQt6
- pyotp
- qrcode
- pillow
- cryptography
- pyperclip

## 安装

1. 确保已安装Python 3.6或更高版本

2. 克隆仓库
```bash
git clone https://github.com/your-username/LightAuth.git
cd LightAuth
```

3. 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python -m venv venv
source venv/bin/activate
```

4. 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行应用
```bash
python main.py
```

2. 添加账户
   - 点击"添加账户"按钮
   - 输入账户名称、发行方和密钥
   - 或点击"生成新密钥"生成随机密钥

3. 使用OTP码
   - OTP码每30秒更新一次
   - 点击OTP码可复制到剪贴板

## 安全说明

- 所有账户数据都使用加密方式存储在本地
- 密钥从不会发送到任何远程服务器
- 请妥善保管您的密钥，丢失后将无法恢复

## 开发说明

要对项目进行开发或扩展：

1. 确保已安装所有开发依赖
```bash
pip install -r requirements.txt
```

2. 主要开发任务：
   - 实现二维码扫描功能
   - 添加更多的主题和自定义选项
   - 实现导入/导出功能
   - 完善密码保护功能 