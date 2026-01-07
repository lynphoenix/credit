"""
配置文件
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据库配置
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'certificate_detection')
}

# 证书类型配置
CERTIFICATE_TYPES = {
    'animal': {
        'name': '动物证书',
        'regions': ['亚洲', '北美洲', '南美洲', '大洋洲', '欧洲', '非洲']
    },
    'plant': {
        'name': '植物证书',
        'regions': ['亚洲', '北美洲', '南美洲', '大洋洲', '欧洲', '非洲']
    },
    'food': {
        'name': '食品证书',
        'categories': ['中药材证书', '干坚果证书', '水产品证书', '燕窝证书', '肉类证书']
    }
}

# 模型路径配置
MODEL_DIR = BASE_DIR / 'models'
YOLO_MODEL_PATH = MODEL_DIR / 'certificate_detection.pt'
CNN_MODEL_PATH = MODEL_DIR / 'forgery_detection.pt'
NLP_MODEL_PATH = MODEL_DIR / 'text_verification'

# 上传文件配置
UPLOAD_FOLDER = BASE_DIR / 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# OCR配置
OCR_CONFIG = {
    'use_textline_orientation': True,
    'lang': 'ch'
}

# 鉴伪阈值配置
FORGERY_THRESHOLDS = {
    'genuine': 0.5,      # < 0.5 判定为真
    'suspicious': 0.8,   # 0.5-0.8 判定为疑似
    # > 0.8 判定为伪造
}

# 训练数据集路径
BOOKS_DIR = BASE_DIR / 'books'
