#!/bin/bash
# 启动服务脚本

# 激活conda环境
eval "$(conda shell.bash hook)"
conda activate credit_detection

# 创建日志目录
mkdir -p logs

# 设置GPU环境变量
export CUDA_VISIBLE_DEVICES=1

# 使用gunicorn启动
gunicorn -c gunicorn_config.py app:app
