"""
调试证件检测逻辑
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from module1_detection import CertificateDetector
import cv2
import numpy as np

detector = CertificateDetector()

# 测试图片
test_images = [
    'books/植物证书/亚洲(东南亚国家涉及木材 重要)/老挝植物检疫证书.jpg',
    'books/食品证书/水产品证书/非洲/摩洛哥输华水产品检验检疫证书样本、印章及签字官名单、笔迹(2022年11月11日更新)/摩洛哥输华水产品检验检疫证书样本、印章及签字官名单、笔迹(2022年11月11日更新)/摩洛哥输华水产品签字官印章及签字笔迹信息（2022年11月11日启用）/摩洛哥输华水产品签字官印章及签字笔迹信息/Specimen PP svpmn.jpg',
]

for img_path in test_images[:2]:
    print('='*80)
    print(f'测试: {img_path.split("/")[-1]}')
    print('='*80)

    # 读取图像
    with open(img_path, 'rb') as f:
        image_data = np.frombuffer(f.read(), np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    # OCR识别
    ocr_result = detector.ocr.predict(img_path)
    ocr_text = detector._extract_ocr_text(ocr_result)

    print(f'\n图像尺寸: {image.shape[1]} x {image.shape[0]}')
    print(f'OCR文本长度: {len(ocr_text)}')
    print(f'\nOCR文本（前500字符）:')
    print(ocr_text[:500])
    print()

    # 检查关键词
    keywords = [
        '证书', '证明', 'certificate', 'CERTIFICATE',
        '检疫', 'quarantine', 'QUARANTINE',
        '卫生', 'health', 'HEALTH',
        '植物', 'plant', 'PLANT', 'phytosanitary',
        '动物', 'animal', 'ANIMAL', 'veterinary',
        '食品', 'food', 'FOOD'
    ]

    has_keywords = any(keyword in ocr_text for keyword in keywords)
    matched_keywords = [k for k in keywords if k in ocr_text]

    print(f'包含关键词: {has_keywords}')
    print(f'匹配的关键词: {matched_keywords}')

    # 尺寸检查
    height, width = image.shape[:2]
    reasonable_size = (width > 500 and height > 300)
    print(f'满足尺寸要求: {reasonable_size}')

    # 最终检测结果
    has_certificate = detector._detect_certificate_presence(image, ocr_text)
    print(f'\n最终检测结果: {has_certificate}')
    print()
