"""
最简化的测试脚本 - 逐个测试并立即保存
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from module1_detection import CertificateDetector
from module2_extraction import CertificateExtractor
from module3_forgery import ForgeryDetectionSystem
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# 初始化
print('初始化模块...')
detector = CertificateDetector()
extractor = CertificateExtractor()
forgery_system = ForgeryDetectionSystem()

OUTPUT_DIR = Path('test_results')
OUTPUT_DIR.mkdir(exist_ok=True)

# 读取测试图片列表
with open('test_images.txt', 'r', encoding='utf-8') as f:
    image_paths = [line.strip() for line in f if line.strip()]

total = len(image_paths)
print(f'\n共 {total} 张图片待测试')
print('='*80)

for i, img_path in enumerate(image_paths, 1):
    filename = Path(img_path).name
    print(f'\n[{i}/{total}] {filename}')

    try:
        # 证件检测
        detection_result = detector.detect_certificate(img_path)

        if detection_result.get('has_certificate'):
            # 信息提取
            extraction_result = extractor.extract(
                detection_result['ocr_text'],
                detection_result['certificate_type']
            )

            # 鉴伪检测
            forgery_result = forgery_system.detect(
                img_path,
                detection_result['ocr_result'],
                detection_result['ocr_text'],
                extraction_result['extracted_fields'],
                detection_result['certificate_type'],
                detection_result['bbox']
            )

            # 打印结果
            cert_type_map = {'plant': '植物证书', 'animal': '动物证书', 'food': '食品证书'}
            cert_type = cert_type_map.get(detection_result['certificate_type'], detection_result['certificate_type'])

            print(f'  证件类型: {cert_type} (置信度: {detection_result["confidence"]:.3f})')
            print(f'  鉴伪评分: {forgery_result["forgery_score"]:.3f} ({forgery_result["forgery_risk"]})')

            # 创建简单截图 - 只保存原图
            img = Image.open(img_path)
            if img.width > 1200:
                ratio = 1200 / img.width
                new_size = (1200, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            output_path = OUTPUT_DIR / f'test_{i:02d}_{cert_type}.png'
            img.save(output_path)
            print(f'  ✓ 截图已保存: {output_path.name}')

        else:
            print(f'  ✗ 未检测到证件')

    except Exception as e:
        print(f'  ✗ 错误: {str(e)}')
        import traceback
        traceback.print_exc()

print('\n' + '='*80)
print('测试完成')
print(f'截图保存位置: {OUTPUT_DIR.absolute()}')
