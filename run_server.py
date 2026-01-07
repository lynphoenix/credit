"""
启动 Web 服务的快速脚本
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('='*80)
print('海关证件识别与鉴伪系统 - Web服务')
print('='*80)
print()
print('正在启动服务器...')
print()

# 导入并启动 Flask app
from app import app

if __name__ == '__main__':
    print('服务启动成功！')
    print()
    print('  访问地址: http://localhost:5000')
    print('  按 Ctrl+C 停止服务')
    print()
    print('='*80)
    print()

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
