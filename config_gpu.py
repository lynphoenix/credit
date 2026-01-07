"""
GPU 配置文件 - 用于 Ubuntu 20.04 部署
"""
from pathlib import Path

# GPU 设置
USE_GPU = True
GPU_ID = 0  # 使用的GPU ID
GPU_MEM_LIMIT = 0.8  # GPU 内存使用限制（80%）

# PaddlePaddle GPU 配置
PADDLE_GPU_CONFIG = {
    'use_gpu': True,
    'gpu_mem': 3000,  # MB
    'gpu_id': GPU_ID,
    'enable_mkldnn': False,  # GPU模式下禁用MKLDNN
    'use_tensorrt': False,  # 如需加速可设为True
}

# 基本配置（保持与原config.py一致）
UPLOAD_FOLDER = Path('uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 确保目录存在
UPLOAD_FOLDER.mkdir(exist_ok=True)
Path('database').mkdir(exist_ok=True)
Path('logs').mkdir(exist_ok=True)
