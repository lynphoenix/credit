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
