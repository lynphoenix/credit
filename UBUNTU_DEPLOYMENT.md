# Ubuntu 20.04 GPU 部署说明

## 系统要求

- **操作系统**: Ubuntu 20.04 LTS
- **GPU**: NVIDIA GPU（支持 CUDA 11.8）
- **驱动**: NVIDIA Driver >= 450.80.02
- **内存**: 建议 >= 16GB
- **硬盘**: 建议 >= 50GB 可用空间
- **Conda**: Anaconda 或 Miniconda

## 快速部署步骤

### 1. 准备服务器环境

检查 GPU 状态:
```bash
nvidia-smi
```

检查 conda:
```bash
conda --version
```

### 2. 获取代码

**方式A: 从 Git 仓库克隆**
```bash
cd /home/smai/linyining
git clone <你的仓库URL> credit
cd credit
```

**方式B: 从本地传输**
```bash
# 在 Windows 上打包
cd D:\work\code\credit
tar --exclude='uploads' --exclude='database' --exclude='test_results' \
    --exclude='__pycache__' --exclude='*.pyc' --exclude='books' \
    -czf credit.tar.gz .

# 传输到 Ubuntu
scp credit.tar.gz username@server-ip:/home/smai/linyining/

# 在 Ubuntu 上解压
ssh username@server-ip
mkdir -p /home/smai/linyining/credit
tar -xzf credit.tar.gz -C /home/smai/linyining/credit/
cd /home/smai/linyining/credit
```

### 3. 运行自动部署脚本

**注意**: 部署脚本会自动使用清华大学镜像源加速下载，如果您的网络环境较好，可以注释掉脚本中的镜像源配置。

```bash
cd /home/smai/linyining/credit
bash deploy_ubuntu_gpu.sh
```

部署脚本会自动完成:
- ✓ 检查系统环境和 GPU
- ✓ 创建 conda 环境 (credit_detection)
- ✓ 安装 CUDA 和 cuDNN
- ✓ 安装 PyTorch GPU 版本
- ✓ 安装 PaddlePaddle GPU 版本
- ✓ 安装项目依赖
- ✓ 配置 Gunicorn 和 systemd 服务
- ✓ 创建管理脚本

### 4. 启动服务

**方式A: 手动启动（推荐用于测试）**
```bash
cd /home/smai/linyining/credit

# 激活conda环境
eval "$(conda shell.bash hook)"
conda activate credit_detection

# 设置使用GPU 1（如果GPU 0被占用）
export CUDA_VISIBLE_DEVICES=1

# 启动服务
nohup gunicorn -c gunicorn_config.py app:app > logs/startup.log 2>&1 &

# 或使用启动脚本
./start_server.sh
```

**方式B: 使用 systemd（推荐用于生产）**
```bash
# 启动服务
sudo systemctl start credit-detection

# 设置开机自启
sudo systemctl enable credit-detection

# 查看服务状态
sudo systemctl status credit-detection
```

### 5. 验证服务

```bash
# 测试本地访问
curl http://localhost:5000

# 测试远程访问（从其他机器）
curl http://100.100.152.204:5000

# 查看日志
tail -f /home/smai/linyining/credit/logs/access.log
tail -f /home/smai/linyining/credit/logs/error.log
```

## 服务管理

### 启动服务
```bash
./start_server.sh
# 或
sudo systemctl start credit-detection
```

### 停止服务
```bash
./stop_server.sh
# 或
sudo systemctl stop credit-detection
```

### 重启服务
```bash
./restart_server.sh
# 或
sudo systemctl restart credit-detection
```

### 查看日志
```bash
# 访问日志
tail -f logs/access.log

# 错误日志
tail -f logs/error.log

# systemd 日志
sudo journalctl -u credit-detection -f
```

## GPU 配置说明

### 指定使用的 GPU

编辑 `.env` 文件:
```bash
# 使用GPU 1（如果GPU 0被占用）
CUDA_VISIBLE_DEVICES=1

# 使用第一个 GPU（如果空闲）
CUDA_VISIBLE_DEVICES=0

# 使用多个 GPU（如果支持）
CUDA_VISIBLE_DEVICES=0,1
```

**注意**: 在本次部署中，由于GPU 0已被其他进程占用，系统已自动配置使用GPU 1。

### 监控 GPU 使用

```bash
# 实时监控
watch -n 1 nvidia-smi

# 或使用 gpustat
pip install gpustat
gpustat -i 1

# 查看当前服务使用的GPU情况
nvidia-smi | grep python
```

## 性能优化

### Gunicorn 配置

编辑 `gunicorn_config.py`:

```python
# Worker 数量（GPU环境建议2-4个）
workers = 2

# 超时设置
timeout = 300  # 5分钟

# GPU 内存设置
# 在 config_gpu.py 中调整 GPU_MEM_LIMIT
```

### 启用 TensorRT 加速（可选）

编辑 `config_gpu.py`:
```python
PADDLE_GPU_CONFIG = {
    'use_gpu': True,
    'use_tensorrt': True,  # 启用 TensorRT
    'precision_mode': 'fp16',  # 使用半精度
}
```

## 更新代码

### 从 Git 更新

```bash
cd ~/credit

# 停止服务
./stop_server.sh

# 拉取最新代码
git pull

# 如有依赖更新
conda activate credit_detection
pip install -r requirements.txt

# 重启服务
./start_server.sh
```

### 从本地更新

```bash
# 在 Windows 打包新代码
cd D:\work\code\credit
tar -czf credit-update.tar.gz *.py *.sh *.yml *.md

# 传输到服务器
scp credit-update.tar.gz username@server-ip:~/credit/

# 在服务器解压
cd ~/credit
./stop_server.sh
tar -xzf credit-update.tar.gz
./start_server.sh
```

## 故障排除

### 服务无法启动

1. 检查 GPU 状态:
```bash
nvidia-smi
```

2. 检查 conda 环境:
```bash
conda activate credit_detection
python -c "import torch; print(torch.cuda.is_available())"
python -c "import paddle; paddle.utils.run_check()"
```

3. 查看错误日志:
```bash
tail -f logs/error.log
sudo journalctl -u credit-detection -n 50
```

### GPU 内存不足

编辑 `config_gpu.py` 减少内存使用:
```python
GPU_MEM_LIMIT = 0.5  # 降低到50%
```

### 端口被占用

修改端口:
```bash
# 编辑 gunicorn_config.py
bind = "0.0.0.0:8000"  # 改为其他端口
```

### 性能慢

1. 检查是否使用 GPU:
```bash
# 查看日志中的设备信息
grep -i "gpu\|cuda" logs/error.log
```

2. 监控 GPU 使用:
```bash
watch -n 1 nvidia-smi
```

3. 减少 worker 数量:
```python
# gunicorn_config.py
workers = 2  # 降低到2个
```

## 安全建议

1. **防火墙配置**
```bash
# 仅允许特定IP访问
sudo ufw allow from 192.168.1.0/24 to any port 5000

# 或使用反向代理
sudo apt install nginx
```

2. **HTTPS 配置**
```bash
# 使用 Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx
```

3. **限制上传文件大小**
```python
# config_gpu.py
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

## 性能指标

### 预期性能（GPU模式）

- 单张证件检测: ~2-5秒
- 并发处理: 2-4个请求
- GPU 内存占用: ~3-4GB

### 对比（CPU vs GPU）

| 操作 | CPU 模式 | GPU 模式 |
|-----|---------|---------|
| 模型加载 | 30-60秒 | 10-20秒 |
| 单张检测 | 20-40秒 | 2-5秒 |
| 并发能力 | 低 | 高 |

## 备份和恢复

### 备份数据

```bash
# 备份上传文件和数据库
cd ~/credit
tar -czf backup-$(date +%Y%m%d).tar.gz uploads/ database/

# 传输到本地
scp username@server-ip:~/credit/backup-*.tar.gz ./
```

### 恢复数据

```bash
cd /home/smai/linyining/credit
tar -xzf backup-20260107.tar.gz
```

## 监控和维护

### 设置定时任务清理日志

```bash
# 编辑 crontab
crontab -e

# 每周清理超过30天的日志
0 0 * * 0 find /home/smai/linyining/credit/logs -name "*.log" -mtime +30 -delete
```

### 设置告警

```bash
# 监控服务状态
#!/bin/bash
if ! systemctl is-active --quiet credit-detection; then
    echo "服务已停止" | mail -s "告警" your@email.com
fi
```

## 完整流程总结

```bash
# 1. 获取代码
cd /home/smai/linyining
git clone <repo-url> credit
cd credit

# 2. 部署环境（会自动配置镜像源和GPU）
bash deploy_ubuntu_gpu.sh

# 3. 启动服务
# 激活conda环境
eval "$(conda shell.bash hook)"
conda activate credit_detection

# 设置使用GPU 1
export CUDA_VISIBLE_DEVICES=1

# 启动服务
nohup gunicorn -c gunicorn_config.py app:app > logs/startup.log 2>&1 &

# 4. 验证
# 本地访问
curl http://localhost:5000

# 远程访问（从其他机器，请根据实际IP修改）
curl http://100.100.152.204:5000

# 5. 查看日志
tail -f logs/access.log

# 6. 查看GPU使用情况
nvidia-smi | grep python
```

完成！您的证件识别系统已在 Ubuntu GPU 服务器上运行。

## 重要提示

1. **OCR模式**: 系统已配置使用CPU模式进行OCR识别，避免Gunicorn多进程与CUDA初始化冲突
2. **GPU选择**: 如需使用GPU加速，建议使用单worker模式（workers=1）或sync worker
3. **镜像源**: 部署脚本已配置清华大学镜像源加速下载
4. **远程访问**: 服务已绑定到0.0.0.0:5000，可从远程访问（请根据实际IP修改示例中的IP地址）
5. **依赖管理**: 所有Python依赖已通过pip安装到credit_detection conda环境中
6. **PDF支持**: 系统已安装PyMuPDF库，支持PDF格式证件识别

## 已知问题和解决方案

### PaddleOCR多进程CUDA冲突

**问题**: Gunicorn多worker模式下，PaddleOCR的GPU初始化会导致worker崩溃

**解决方案**:
- 当前配置：OCR使用CPU模式（`config.py`中`OCR_CONFIG['use_gpu'] = False`）
- 如需GPU加速：
  ```python
  # gunicorn_config.py
  workers = 1  # 改为单worker
  worker_class = "sync"  # 使用sync worker
  ```
  ```python
  # config.py
  OCR_CONFIG = {
      'use_gpu': True,  # 启用GPU
      'gpu_id': 1,  # 指定GPU编号
  }
  ```
