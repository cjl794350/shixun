# -*- coding: utf-8 -*-
"""全局配置"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# MySQL 数据库配置（账号/密码均为 root）
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'pdf_summary',
    'charset': 'utf8mb4',
}

# 上传文件保存目录
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'pdf'}

# 单个上传文件大小上限 (16MB)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# 服务端口
SERVER_PORT = 5000
