#!/bin/bash
#
# 海关证件识别系统 - Ubuntu 20.04 GPU 自动部署脚本
#
# 使用方法:
#   bash deploy_ubuntu_gpu.sh
#
# 环境要求:
#   - Ubuntu 20.04
#   - NVIDIA GPU + CUDA驱动
#   - conda 已安装
#

set -e  # 遇到错误立即退出

echo "========================================================================"
echo "海关证件识别与鉴伪系统 - Ubuntu GPU 部署脚本"
echo "========================================================================"
echo ""

# 配置变量
CONDA_ENV_NAME="credit_detection"
PYTHON_VERSION="3.9"
PROJECT_DIR="/home/smai/linyining/credit"
CONDA_BASE="/home/smai/dc_dir/yes"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}► $1${NC}"
}

# 1. 检查系统环境
print_info "检查系统环境..."

# 检查是否是Ubuntu
if [ ! -f /etc/os-release ]; then
    print_error "无法识别操作系统"
    exit 1
fi

source /etc/os-release
if [[ "$ID" != "ubuntu" ]]; then
    print_error "此脚本仅支持Ubuntu系统"
    exit 1
fi
print_success "操作系统: Ubuntu $VERSION_ID"

# 检查NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    print_error "未检测到NVIDIA GPU或驱动未安装"
    print_info "请先安装NVIDIA驱动"
    exit 1
fi
print_success "GPU检测通过"
nvidia-smi --query-gpu=name --format=csv,noheader | head -1

# 检查conda
if ! command -v conda &> /dev/null; then
    print_error "未检测到conda，请先安装Anaconda或Miniconda"
    exit 1
fi
print_success "Conda已安装: $(conda --version)"

echo ""

# 2. 创建conda环境
print_info "创建conda环境..."

if conda env list | grep -q "^${CONDA_ENV_NAME} "; then
    print_info "环境 ${CONDA_ENV_NAME} 已存在，是否删除重建? (y/n)"
    read -r response
    if [[ "$response" == "y" ]]; then
        conda env remove -n ${CONDA_ENV_NAME} -y
        print_success "已删除旧环境"
    else
        print_info "使用现有环境"
    fi
fi

if ! conda env list | grep -q "^${CONDA_ENV_NAME} "; then
    conda create -n ${CONDA_ENV_NAME} python=${PYTHON_VERSION} -y
    print_success "创建conda环境: ${CONDA_ENV_NAME}"
fi

# 激活环境
eval "$(conda shell.bash hook)"
conda activate ${CONDA_ENV_NAME}
print_success "激活环境: ${CONDA_ENV_NAME}"

echo ""

# 3. 配置conda镜像源
print_info "配置conda镜像源..."

conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --set show_channel_urls yes

print_success "Conda镜像源配置完成"

echo ""

# 4. 安装CUDA和cuDNN (通过conda)
print_info "安装CUDA和cuDNN..."

conda install -y cudatoolkit=11.8 cudnn=8.9
print_success "CUDA工具包安装完成"

echo ""

# 5. 安装PyTorch GPU版本
print_info "安装PyTorch GPU版本..."

pip install torch torchvision torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple
print_success "PyTorch GPU版本安装完成"

# 验证PyTorch GPU
python -c "import torch; print(f'PyTorch版本: {torch.__version__}'); print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'GPU数量: {torch.cuda.device_count()}')"

echo ""

# 6. 安装PaddlePaddle GPU版本
print_info "安装PaddlePaddle GPU版本..."

python -m pip install paddlepaddle-gpu==2.6.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
print_success "PaddlePaddle GPU版本安装完成"

# 验证PaddlePaddle GPU
python -c "import paddle; print(f'PaddlePaddle版本: {paddle.__version__}'); paddle.utils.run_check()"

echo ""

# 7. 安装其他依赖
print_info "安装项目依赖..."

pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    paddleocr==2.8.1 \
    flask==3.0.0 \
    flask-cors==4.0.0 \
    opencv-python==4.8.1.78 \
    pillow==10.1.0 \
    numpy==1.24.3 \
    sqlalchemy==2.0.23 \
    requests==2.31.0 \
    gunicorn==21.2.0 \
    gevent==23.9.1

print_success "项目依赖安装完成"

echo ""

# 8. 创建项目目录
print_info "设置项目目录..."

if [ -d "$PROJECT_DIR" ]; then
    print_info "项目目录已存在: $PROJECT_DIR"
else
    mkdir -p $PROJECT_DIR
    print_success "创建项目目录: $PROJECT_DIR"
fi

# 创建必要的子目录
cd $PROJECT_DIR
mkdir -p uploads database books test_results

print_success "目录结构创建完成"

echo ""

# 9. 创建Gunicorn配置文件
print_info "创建Gunicorn配置..."

cat > gunicorn_config.py << 'EOF'
"""
Gunicorn 配置文件 - GPU优化版本
"""
import multiprocessing

# 绑定地址
bind = "0.0.0.0:5000"

# Worker配置 - GPU环境下使用较少worker
workers = 2  # GPU环境建议2-4个worker
worker_class = "gevent"  # 使用gevent异步worker
worker_connections = 1000

# 超时设置
timeout = 300  # 5分钟超时
graceful_timeout = 30
keepalive = 5

# 日志
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = "credit_detection_gpu"

# 预加载应用
preload_app = True

# 最大请求数后重启worker
max_requests = 1000
max_requests_jitter = 50

# 守护进程
daemon = False

# PID文件
pidfile = "logs/gunicorn.pid"
EOF

print_success "Gunicorn配置创建完成"

echo ""

# 10. 创建systemd服务文件
print_info "创建systemd服务..."

sudo tee /etc/systemd/system/credit-detection.service > /dev/null << EOF
[Unit]
Description=Credit Certificate Detection System (GPU)
After=network.target

[Service]
Type=notify
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=/home/smai/dc_dir/yes/envs/${CONDA_ENV_NAME}/bin:$PATH"
Environment="CUDA_VISIBLE_DEVICES=1"
ExecStart=/home/smai/dc_dir/yes/envs/${CONDA_ENV_NAME}/bin/gunicorn -c gunicorn_config.py app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_success "Systemd服务创建完成"

echo ""

# 11. 创建启动/停止脚本
print_info "创建管理脚本..."

# 启动脚本
cat > start_server.sh << 'EOF'
#!/bin/bash
# 启动服务脚本

# 激活conda环境
eval "$(conda shell.bash hook)"
conda activate credit_detection

# 创建日志目录
mkdir -p logs

# 使用gunicorn启动
gunicorn -c gunicorn_config.py app:app
EOF

chmod +x start_server.sh

# 停止脚本
cat > stop_server.sh << 'EOF'
#!/bin/bash
# 停止服务脚本

PID_FILE="logs/gunicorn.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    echo "正在停止服务 (PID: $PID)..."
    kill $PID
    echo "服务已停止"
else
    echo "PID文件不存在，查找gunicorn进程..."
    pkill -f "gunicorn.*credit_detection"
    echo "已尝试停止所有相关进程"
fi
EOF

chmod +x stop_server.sh

# 重启脚本
cat > restart_server.sh << 'EOF'
#!/bin/bash
# 重启服务脚本

./stop_server.sh
sleep 2
./start_server.sh
EOF

chmod +x restart_server.sh

print_success "管理脚本创建完成"

echo ""

# 12. 创建环境变量文件
print_info "创建环境配置文件..."

cat > .env << EOF
# 环境配置文件

# GPU配置
CUDA_VISIBLE_DEVICES=0
CUDA_LAUNCH_BLOCKING=1

# PaddlePaddle配置
FLAGS_use_cuda=True
FLAGS_fraction_of_gpu_memory_to_use=0.8

# Flask配置
FLASK_ENV=production
FLASK_DEBUG=0

# 服务配置
HOST=0.0.0.0
PORT=5000
EOF

print_success "环境配置文件创建完成"

echo ""

# 13. 显示部署信息
echo "========================================================================"
echo "部署完成！"
echo "========================================================================"
echo ""
echo "环境信息:"
echo "  - Conda环境: ${CONDA_ENV_NAME}"
echo "  - Python: ${PYTHON_VERSION}"
echo "  - 项目目录: ${PROJECT_DIR}"
echo ""
echo "启动服务:"
echo "  方式1 (手动): cd ${PROJECT_DIR} && ./start_server.sh"
echo "  方式2 (systemd): sudo systemctl start credit-detection"
echo ""
echo "停止服务:"
echo "  方式1 (手动): cd ${PROJECT_DIR} && ./stop_server.sh"
echo "  方式2 (systemd): sudo systemctl stop credit-detection"
echo ""
echo "查看日志:"
echo "  访问日志: tail -f ${PROJECT_DIR}/logs/access.log"
echo "  错误日志: tail -f ${PROJECT_DIR}/logs/error.log"
echo ""
echo "设置开机自启:"
echo "  sudo systemctl enable credit-detection"
echo ""
echo "测试服务:"
echo "  curl http://localhost:5000"
echo ""
echo "========================================================================"
echo ""
print_info "请将项目代码上传到 ${PROJECT_DIR} 目录"
print_info "然后运行: ./start_server.sh 启动服务"
echo ""
