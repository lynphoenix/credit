"""
Web API测试脚本 - 测试20张证件图片并生成截图报告
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import time

# 配置
API_URL = 'http://localhost:5000/api/analyze'
OUTPUT_DIR = Path('test_results')
OUTPUT_DIR.mkdir(exist_ok=True)

def create_result_image(image_path, result_data, index, total):
    """创建带有测试结果的截图"""
    try:
        # 读取原图
        img = Image.open(image_path)

        # 缩放到合适大小
        max_width = 800
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # 创建结果图像（原图 + 文本区域）
        text_height = 400
        result_img = Image.new('RGB', (img.width, img.height + text_height), 'white')
        result_img.paste(img, (0, 0))

        # 绘制文本
        draw = ImageDraw.Draw(result_img)

        # 尝试使用系统字体
        try:
            font_title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24)
            font_normal = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
            font_small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
        except:
            font_title = ImageFont.load_default()
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()

        y = img.height + 20

        # 标题
        filename = os.path.basename(image_path)
        draw.text((20, y), f"测试 {index}/{total}: {filename[:50]}", fill='black', font=font_title)
        y += 40

        if result_data.get('success'):
            # 成功 - 显示检测结果
            res = result_data['result']

            # 证件类型
            cert_type_map = {'plant': '植物证书', 'animal': '动物证书', 'food': '食品证书'}
            cert_type = cert_type_map.get(res.get('certificate_type', ''), res.get('certificate_type', 'unknown'))
            draw.text((20, y), f"✓ 证件类型: {cert_type}", fill='green', font=font_normal)
            y += 30

            # 置信度
            confidence = res.get('confidence', 0)
            draw.text((20, y), f"  置信度: {confidence:.3f}", fill='black', font=font_normal)
            y += 30

            # 提取的字段
            fields = res.get('extracted_fields', {})
            cert_num = fields.get('certificate_number', '-')
            draw.text((20, y), f"  证书编号: {cert_num[:40]}", fill='black', font=font_small)
            y += 25

            issuer = fields.get('issuer', '-')
            draw.text((20, y), f"  签发机构: {issuer[:40]}", fill='black', font=font_small)
            y += 30

            # 鉴伪结果
            forgery = res.get('forgery_result', {})
            risk = forgery.get('forgery_risk', 'unknown')
            score = forgery.get('forgery_score', 0)

            risk_map = {'genuine': '真实', 'suspicious': '可疑', 'forged': '伪造'}
            risk_text = risk_map.get(risk, risk)
            risk_color = 'green' if risk == 'genuine' else ('orange' if risk == 'suspicious' else 'red')

            draw.text((20, y), f"  鉴伪结果: {risk_text} (评分: {score:.3f})", fill=risk_color, font=font_normal)
            y += 30

            # 详细分析
            img_score = forgery.get('image_score', 0)
            text_score = forgery.get('text_score', 0)
            struct_score = forgery.get('structure_score', 0)

            draw.text((20, y), f"    图像: {img_score:.3f}  文本: {text_score:.3f}  结构: {struct_score:.3f}",
                     fill='gray', font=font_small)

        else:
            # 失败 - 显示错误
            error_msg = result_data.get('error', '未知错误')
            draw.text((20, y), f"✗ 失败: {error_msg}", fill='red', font=font_normal)

        return result_img

    except Exception as e:
        print(f"创建结果图像失败: {str(e)}")
        return None

def test_image(image_path, index, total):
    """测试单张图片"""
    print(f'\n测试 {index}/{total}: {os.path.basename(image_path)}')

    if not os.path.exists(image_path):
        print(f'  ✗ 文件不存在')
        return None

    try:
        # 发送请求 - 超时时间设置为300秒
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
            response = requests.post(API_URL, files=files, timeout=300)

        result = response.json()

        if result.get('success'):
            print(f'  ✓ 成功 - {result["result"]["certificate_type"]} (置信度: {result["result"]["confidence"]:.3f})')

            # 创建结果截图
            result_img = create_result_image(image_path, result, index, total)
            if result_img:
                output_path = OUTPUT_DIR / f'test_{index:02d}_success.png'
                result_img.save(output_path)
                print(f'  截图已保存: {output_path}')

            return {'status': 'success', 'result': result}
        else:
            error = result.get('error', '未知错误')
            print(f'  ✗ 失败 - {error}')

            # 创建失败截图
            result_img = create_result_image(image_path, result, index, total)
            if result_img:
                output_path = OUTPUT_DIR / f'test_{index:02d}_failed.png'
                result_img.save(output_path)
                print(f'  截图已保存: {output_path}')

            return {'status': 'failed', 'error': error}

    except requests.exceptions.Timeout:
        print(f'  ✗ 超时')
        return {'status': 'timeout'}
    except Exception as e:
        print(f'  ✗ 异常: {str(e)}')
        return {'status': 'error', 'error': str(e)}

def main():
    """主函数"""
    print('='*80)
    print('Web API 测试脚本')
    print('='*80)

    # 读取测试图片列表
    with open('test_images.txt', 'r', encoding='utf-8') as f:
        image_paths = [line.strip() for line in f if line.strip()]

    total = len(image_paths)
    print(f'\n共 {total} 张图片待测试\n')

    # 测试统计
    stats = {
        'success': 0,
        'failed': 0,
        'timeout': 0,
        'error': 0
    }

    # 逐个测试
    results = []
    for i, img_path in enumerate(image_paths, 1):
        result = test_image(img_path, i, total)
        if result:
            stats[result['status']] += 1
            results.append({
                'index': i,
                'path': img_path,
                'result': result
            })

        # 短暂延迟避免请求过快
        time.sleep(0.5)

    # 生成汇总报告
    print('\n' + '='*80)
    print('测试完成 - 统计结果')
    print('='*80)
    print(f'成功: {stats["success"]}/{total}')
    print(f'失败: {stats["failed"]}/{total}')
    print(f'超时: {stats["timeout"]}/{total}')
    print(f'错误: {stats["error"]}/{total}')
    print(f'\n截图已保存至: {OUTPUT_DIR.absolute()}')

    # 保存JSON结果
    json_path = OUTPUT_DIR / 'test_results.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'stats': stats,
            'results': results
        }, f, ensure_ascii=False, indent=2)
    print(f'详细结果已保存: {json_path}')

if __name__ == '__main__':
    main()
