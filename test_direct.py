"""
简化的直接API测试 - 不使用requests库，直接调用模块
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from module1_detection import CertificateDetector
from module2_extraction import CertificateExtractor
from module3_forgery import ForgeryDetectionSystem
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json

# 初始化模块
print('初始化模块...')
detector = CertificateDetector()
extractor = CertificateExtractor()
forgery_system = ForgeryDetectionSystem()

# 输出目录
OUTPUT_DIR = Path('test_results')
OUTPUT_DIR.mkdir(exist_ok=True)

def create_result_screenshot(image_path, detection_result, extraction_result, forgery_result, index, total):
    """创建结果截图"""
    try:
        # 读取原图并缩放
        img = Image.open(image_path)
        max_width = 900
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # 创建结果图像
        text_height = 450
        result_img = Image.new('RGB', (img.width, img.height + text_height), 'white')
        result_img.paste(img, (0, 0))

        # 绘制文本
        draw = ImageDraw.Draw(result_img)
        try:
            font_title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
            font_normal = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
            font_small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 13)
        except:
            font_title = ImageFont.load_default()
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()

        y = img.height + 15
        filename = Path(image_path).name

        # 标题
        draw.text((15, y), f"测试 {index}/{total}: {filename[:60]}", fill='black', font=font_title)
        y += 35

        if detection_result.get('has_certificate'):
            # 证件类型
            cert_type_map = {'plant': '植物证书', 'animal': '动物证书', 'food': '食品证书'}
            cert_type = cert_type_map.get(detection_result.get('certificate_type', ''), detection_result.get('certificate_type', ''))
            confidence = detection_result.get('confidence', 0)

            draw.text((15, y), f"✓ 证件类型: {cert_type} (置信度: {confidence:.3f})", fill='green', font=font_normal)
            y += 28

            # 提取的关键字段
            fields = extraction_result.get('extracted_fields', {})
            cert_num = fields.get('certificate_number', '-')[:50]
            issuer = fields.get('issuer', '-')[:50]

            draw.text((15, y), f"  证书编号: {cert_num}", fill='black', font=font_small)
            y += 22
            draw.text((15, y), f"  签发机构: {issuer}", fill='black', font=font_small)
            y += 28

            # 鉴伪结果
            risk = forgery_result.get('forgery_risk', 'unknown')
            score = forgery_result.get('forgery_score', 0)

            risk_map = {'genuine': '真实 ✓', 'suspicious': '可疑 ⚠', 'forged': '伪造 ✗'}
            risk_text = risk_map.get(risk, risk)
            risk_color = 'green' if risk == 'genuine' else ('orange' if risk == 'suspicious' else 'red')

            draw.text((15, y), f"  鉴伪结果: {risk_text} (综合评分: {score:.3f})", fill=risk_color, font=font_normal)
            y += 28

            # 详细分析评分
            img_score = forgery_result.get('image_score', 0)
            text_score = forgery_result.get('text_score', 0)
            struct_score = forgery_result.get('structure_score', 0)

            draw.text((15, y), f"    图像分析: {img_score:.3f}  文本分析: {text_score:.3f}  结构分析: {struct_score:.3f}",
                     fill='gray', font=font_small)
            y += 25

            # 分析详情
            img_analysis = forgery_result.get('image_analysis', '')
            if img_analysis:
                draw.text((15, y), f"    {img_analysis[:70]}", fill='gray', font=font_small)
                y += 20

            text_analysis = forgery_result.get('text_analysis', '')
            if text_analysis:
                draw.text((15, y), f"    {text_analysis[:70]}", fill='gray', font=font_small)
                y += 20

        else:
            draw.text((15, y), "✗ 未检测到有效证件", fill='red', font=font_normal)
            y += 25
            draw.text((15, y), f"  OCR文本长度: {len(detection_result.get('ocr_text', ''))}", fill='gray', font=font_small)

        return result_img

    except Exception as e:
        print(f"  创建截图失败: {str(e)}")
        return None

# 读取测试图片列表
with open('test_images.txt', 'r', encoding='utf-8') as f:
    image_paths = [line.strip() for line in f if line.strip()]

total = len(image_paths)
print(f'\n共 {total} 张图片待测试\n')
print('='*80)

stats = {'success': 0, 'failed': 0}

for i, img_path in enumerate(image_paths, 1):
    print(f'\n测试 {i}/{total}: {Path(img_path).name}')

    try:
        # 步骤1: 证件检测
        detection_result = detector.detect_certificate(img_path)

        if detection_result.get('has_certificate'):
            # 步骤2: 信息提取
            extraction_result = extractor.extract(
                detection_result['ocr_text'],
                detection_result['certificate_type']
            )

            # 步骤3: 鉴伪检测
            forgery_result = forgery_system.detect(
                img_path,
                detection_result['ocr_result'],
                detection_result['ocr_text'],
                extraction_result['extracted_fields'],
                detection_result['certificate_type'],
                detection_result['bbox']
            )

            # 创建截图
            result_img = create_result_screenshot(
                img_path, detection_result, extraction_result, forgery_result, i, total
            )

            if result_img:
                output_path = OUTPUT_DIR / f'test_{i:02d}_success.png'
                result_img.save(output_path)
                print(f'  ✓ 成功 - {detection_result["certificate_type"]} (置信度: {detection_result["confidence"]:.3f})')
                print(f'  鉴伪结果: {forgery_result["forgery_risk"]} ({forgery_result["forgery_score"]:.3f})')
                print(f'  截图: {output_path}')
                stats['success'] += 1
        else:
            # 未检测到证件
            print(f'  ✗ 未检测到证件')
            stats['failed'] += 1

    except Exception as e:
        print(f'  ✗ 错误: {str(e)}')
        stats['failed'] += 1

print('\n' + '='*80)
print('测试完成')
print('='*80)
print(f'成功: {stats["success"]}/{total}')
print(f'失败: {stats["failed"]}/{total}')
print(f'\n截图保存位置: {OUTPUT_DIR.absolute()}')
