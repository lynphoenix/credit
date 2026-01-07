"""
项目启动脚本
快速启动整个系统
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import subprocess
import time


def check_dependencies():
    """检查依赖是否安装"""
    print("="*80)
    print("检查系统依赖...")
    print("="*80)

    required_packages = [
        'flask',
        'paddleocr',
        'torch',
        'cv2',
        'sqlalchemy'
    ]

    missing = []
    for package in required_packages:
        try:
            if package == 'cv2':
                __import__('cv2')
            else:
                __import__(package)
            print(f"✓ {package:20s} 已安装")
        except ImportError:
            print(f"✗ {package:20s} 未安装")
            missing.append(package)

    if missing:
        print(f"\n缺少依赖: {', '.join(missing)}")
        print("请运行: pip install -r requirements.txt")
        return False

    print("\n✓ 所有依赖已安装")
    return True


def check_directories():
    """检查必要的目录"""
    print("\n" + "="*80)
    print("检查目录结构...")
    print("="*80)

    dirs = ['uploads', 'database', 'books']

    for d in dirs:
        if os.path.exists(d):
            print(f"✓ {d:20s} 存在")
        else:
            print(f"✗ {d:20s} 不存在，正在创建...")
            os.makedirs(d, exist_ok=True)

    print("\n✓ 目录结构完整")
    return True


def run_tests():
    """运行测试"""
    print("\n" + "="*80)
    print("运行集成测试...")
    print("="*80)

    try:
        result = subprocess.run(
            [sys.executable, 'test_integration.py', '--mode', 'integration'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=180
        )

        # 打印输出（去除ANSI颜色代码）
        output = result.stdout
        print(output)

        if result.returncode == 0:
            print("\n✓ 集成测试通过")
            return True
        else:
            print(f"\n✗ 集成测试失败 (返回码: {result.returncode})")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("\n✗ 测试超时")
        return False
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        return False


def start_web_server():
    """启动Web服务器"""
    print("\n" + "="*80)
    print("启动Web服务...")
    print("="*80)
    print("\n提示:")
    print("  - 访问地址: http://localhost:5000")
    print("  - 按 Ctrl+C 停止服务")
    print("\n" + "="*80 + "\n")

    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n\n服务已停止")


def main():
    """主函数"""
    print("\n" + "="*80)
    print("海关证件识别与鉴伪系统 - 启动脚本")
    print("="*80 + "\n")

    # 1. 检查依赖
    if not check_dependencies():
        print("\n请先安装依赖后再启动")
        sys.exit(1)

    # 2. 检查目录
    if not check_directories():
        sys.exit(1)

    # 3. 询问是否运行测试
    print("\n是否运行集成测试? (y/n, 默认n): ", end='')
    run_test = input().strip().lower()

    if run_test == 'y':
        if not run_tests():
            print("\n测试未通过，是否继续启动Web服务? (y/n, 默认y): ", end='')
            continue_run = input().strip().lower()
            if continue_run == 'n':
                sys.exit(1)

    # 4. 启动Web服务
    start_web_server()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
        sys.exit(0)
