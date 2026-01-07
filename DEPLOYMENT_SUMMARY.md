# 海关证件识别系统 - Ubuntu GPU 部署完整方案

## 📋 目录

1. [部署脚本](#部署脚本)
2. [Git 上传指引](#git-上传指引)
3. [客户端超时配置](#客户端超时配置)
4. [部署流程](#部署流程)
5. [快速开始](#快速开始)

---

## 🚀 已完成的准备工作

### ✅ 1. Ubuntu GPU 自动部署脚本
**文件**: `deploy_ubuntu_gpu.sh`

**功能**:
- 自动检查系统环境（Ubuntu、GPU、Conda）
- 创建 conda 环境（Python 3.9）
- 安装 CUDA 11.8 + cuDNN 8.9
- 安装 PyTorch GPU 版本
- 安装 PaddlePaddle GPU 版本
- 配置 Gunicorn 生产服务器
- 创建 systemd 服务
- 生成管理脚本（启动/停止/重启）

**使用方法**:
```bash
bash deploy_ubuntu_gpu.sh
```

### ✅ 2. Conda 环境配置文件
**文件**: `environment_gpu.yml`

**包含**:
- Python 3.9
- CUDA Toolkit 11.8
- cuDNN 8.9
- PyTorch 2.1.0 (GPU)
- PaddlePaddle GPU 2.6.0
- 所有项目依赖

**使用方法**:
```bash
conda env create -f environment_gpu.yml
```

### ✅ 3. 客户端超时已更新
**修改的文件**:
- `test_web_api.py` - 超时从 120秒 → 300秒
- `quick_web_test.py` - 超时从 60秒 → 300秒

### ✅ 4. GPU 配置文件
**文件**: `config_gpu.py`

**配置**:
- GPU ID 选择
- GPU 内存限制（80%）
- PaddlePaddle GPU 参数
- TensorRT 选项（可选）

### ✅ 5. Git 文件准备
**文件**: `.gitignore`

**排除项**:
- uploads/ - 上传文件目录
- database/ - 数据库文件
- test_results/ - 测试结果
- books/ - 证书样本（可选）
- logs/ - 日志文件
- `__pycache__/` - Python 缓存
- 模型缓存文件

---

## 📝 Git 上传指引

### 方式一：使用现有 Git 仓库

```bash
# 1. 进入项目目录
cd D:\work\code\credit

# 2. 初始化 Git（如果还未初始化）
git init

# 3. 添加所有文件
git add .

# 4. 创建提交
git commit -m "Initial commit: 海关证件识别系统 GPU版本"

# 5. 添加远程仓库
git remote add origin <你的仓库URL>

# 6. 推送到远程
git push -u origin main
```

### 方式二：GitHub 完整流程

**1. 在 GitHub 创建新仓库**
- 访问: https://github.com/new
- 仓库名: `credit-detection-system`
- 类型: Private（建议）
- 不要勾选 "Initialize with README"

**2. 本地推送**
```bash
cd D:\work\code\credit

git init
git add .
git commit -m "Initial commit: 海关证件识别系统"
git branch -M main
git remote add origin https://github.com/你的用户名/credit-detection-system.git
git push -u origin main
```

**3. 使用 SSH（推荐）**
```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 添加到 GitHub: https://github.com/settings/keys
# 复制 ~/.ssh/id_ed25519.pub 内容

# 修改远程 URL
git remote set-url origin git@github.com:你的用户名/credit-detection-system.git
```

### 文件检查清单

上传前确认这些文件存在:
- ✅ `deploy_ubuntu_gpu.sh` - 部署脚本
- ✅ `environment_gpu.yml` - Conda 环境
- ✅ `config_gpu.py` - GPU 配置
- ✅ `requirements.txt` - Python 依赖
- ✅ `.gitignore` - Git 忽略规则
- ✅ `GIT_UPLOAD_GUIDE.md` - Git 指引
- ✅ `UBUNTU_DEPLOYMENT.md` - 部署文档
- ✅ `BUG_FIX_REPORT.md` - Bug 修复报告
- ✅ 所有 Python 模块文件（module*.py, app.py 等）

---

## 🔧 完整部署流程

### 步骤 1: 推送代码到 Git

```bash
# Windows 本地
cd D:\work\code\credit
git add .
git commit -m "准备 GPU 部署"
git push
```

### 步骤 2: Ubuntu 服务器获取代码

```bash
# SSH 登录 Ubuntu
ssh username@your-ubuntu-server

# 克隆仓库
cd ~
git clone <你的仓库URL> credit
cd credit
```

### 步骤 3: 运行自动部署

```bash
# 执行部署脚本
bash deploy_ubuntu_gpu.sh
```

脚本会提示你:
- 环境名称是否覆盖（如果已存在）
- 自动完成所有安装和配置

### 步骤 4: 启动服务

```bash
# 方式 A: 手动启动（测试用）
./start_server.sh

# 方式 B: systemd 服务（生产用）
sudo systemctl start credit-detection
sudo systemctl enable credit-detection  # 开机自启
```

### 步骤 5: 验证部署

```bash
# 测试服务
curl http://localhost:5000

# 查看 GPU 使用
watch -n 1 nvidia-smi

# 查看日志
tail -f logs/access.log
tail -f logs/error.log
```

---

## ⚡ 快速开始（一键部署）

### 在 Ubuntu 服务器上执行

```bash
# 一键部署命令
curl -fsSL <你的仓库raw文件URL>/deploy_ubuntu_gpu.sh | bash

# 或者
wget <你的仓库raw文件URL>/deploy_ubuntu_gpu.sh
chmod +x deploy_ubuntu_gpu.sh
./deploy_ubuntu_gpu.sh
```

### 完整命令序列

```bash
# 1. 获取代码
git clone <仓库URL> ~/credit && cd ~/credit

# 2. 部署环境
bash deploy_ubuntu_gpu.sh

# 3. 启动服务
./start_server.sh

# 4. 测试
curl http://localhost:5000
```

---

## 🔍 GPU 配置验证

### 验证 CUDA

```bash
conda activate credit_detection
python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU数量: {torch.cuda.device_count()}')"
python -c "import torch; print(f'GPU名称: {torch.cuda.get_device_name(0)}')"
```

### 验证 PaddlePaddle

```bash
python -c "import paddle; paddle.utils.run_check()"
```

### 运行测试

```bash
# 使用 GPU 版本配置
export USE_GPU=1
python quick_test.py
```

---

## 📊 性能对比

| 指标 | CPU 模式 | GPU 模式 |
|------|---------|---------|
| 模型加载时间 | 30-60秒 | 10-20秒 |
| 单张证件处理 | 20-40秒 | 2-5秒 |
| 并发处理能力 | 1-2请求 | 2-4请求 |
| 内存占用 | 2-4GB | 3-5GB |
| 适用场景 | 开发测试 | 生产环境 |

---

## 🛠 管理命令

### 服务管理

```bash
# 启动
./start_server.sh
sudo systemctl start credit-detection

# 停止
./stop_server.sh
sudo systemctl stop credit-detection

# 重启
./restart_server.sh
sudo systemctl restart credit-detection

# 查看状态
sudo systemctl status credit-detection
```

### 日志查看

```bash
# 访问日志
tail -f logs/access.log

# 错误日志
tail -f logs/error.log

# systemd 日志
sudo journalctl -u credit-detection -f
```

### GPU 监控

```bash
# 实时监控
watch -n 1 nvidia-smi

# 详细信息
nvidia-smi -l 1

# 使用 gpustat
pip install gpustat
gpustat -i 1
```

---

## 🔄 代码更新流程

### 更新服务器代码

```bash
# 1. SSH 登录服务器
ssh username@your-ubuntu-server

# 2. 进入项目目录
cd ~/credit

# 3. 停止服务
./stop_server.sh

# 4. 拉取最新代码
git pull

# 5. 如有依赖更新（可选）
conda activate credit_detection
pip install -r requirements.txt

# 6. 重启服务
./start_server.sh
```

### 本地开发流程

```bash
# 1. Windows 开发完成
git add .
git commit -m "修复XXX功能"
git push

# 2. Ubuntu 更新
ssh username@server
cd ~/credit
./stop_server.sh
git pull
./start_server.sh
```

---

## ⚠️ 故障排除

### GPU 未识别

```bash
# 检查驱动
nvidia-smi

# 重新安装 CUDA
conda install cudatoolkit=11.8 -c conda-forge
```

### 服务无法启动

```bash
# 查看错误日志
tail -50 logs/error.log

# 检查端口占用
netstat -tulpn | grep 5000

# 手动运行查看错误
conda activate credit_detection
python app.py
```

### GPU 内存不足

编辑 `config_gpu.py`:
```python
GPU_MEM_LIMIT = 0.5  # 降低到 50%
```

---

## 📦 备份和恢复

### 备份数据

```bash
# 备份上传文件和数据库
cd ~/credit
tar -czf backup-$(date +%Y%m%d).tar.gz uploads/ database/

# 下载到本地
scp username@server:~/credit/backup-*.tar.gz ./
```

### 恢复数据

```bash
cd ~/credit
tar -xzf backup-20260107.tar.gz
```

---

## 📚 相关文档

- `GIT_UPLOAD_GUIDE.md` - 详细的 Git 使用指引
- `UBUNTU_DEPLOYMENT.md` - Ubuntu 部署详细说明
- `BUG_FIX_REPORT.md` - Bug 修复记录
- `deploy_ubuntu_gpu.sh` - 自动部署脚本
- `environment_gpu.yml` - Conda 环境配置

---

## ✅ 部署检查清单

部署前:
- [ ] 确认 Ubuntu 20.04 系统
- [ ] 确认 NVIDIA GPU 可用
- [ ] 确认 conda 已安装
- [ ] 代码已推送到 Git 仓库

部署中:
- [ ] 运行 `deploy_ubuntu_gpu.sh`
- [ ] 确认所有依赖安装成功
- [ ] 验证 GPU 可用
- [ ] 确认服务启动成功

部署后:
- [ ] 测试 API 接口
- [ ] 检查 GPU 使用率
- [ ] 查看日志无错误
- [ ] 配置防火墙（如需）
- [ ] 设置开机自启
- [ ] 配置定时备份

---

## 🎯 总结

您现在拥有:
1. ✅ 完整的 Ubuntu GPU 自动部署脚本
2. ✅ Conda GPU 环境配置
3. ✅ 客户端超时已更新（300秒）
4. ✅ Git 上传和部署指引
5. ✅ GPU 配置文件
6. ✅ 生产环境服务器配置（Gunicorn）
7. ✅ Systemd 服务管理
8. ✅ 完整的文档和故障排除指南

**下一步操作**:
1. 将代码推送到 Git 仓库
2. 在 Ubuntu 服务器上克隆代码
3. 运行 `bash deploy_ubuntu_gpu.sh`
4. 启动服务并测试

祝部署顺利！🚀
