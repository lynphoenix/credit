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
