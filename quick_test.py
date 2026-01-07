"""
快速验证分类逻辑 - 不需要加载PaddleOCR模型
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 直接测试分类函数
def test_classification():
    from module1_detection import CertificateDetector

    detector = CertificateDetector()

    # 测试用例 - 模拟OCR文本
    test_cases = [
        ('水产品检验检疫证书 输华水产品', '食品证书'),
        ('植物检疫证书 phytosanitary certificate', '植物证书'),
        ('动物检疫证书 veterinary certificate', '动物证书'),
        ('兽医官 畜牧 animal health', '动物证书'),
        ('fishery aquatic seafood', '食品证书'),
        ('水产 渔业 fish', '食品证书'),
    ]

    print('='*70)
    print('证件分类逻辑测试')
    print('='*70)

    passed = 0
    failed = 0

    for ocr_text, expected in test_cases:
        cert_type, confidence = detector._classify_certificate_type(ocr_text)

        type_map = {'food': '食品证书', 'plant': '植物证书', 'animal': '动物证书'}
        actual = type_map.get(cert_type, cert_type)

        status = '✓' if actual == expected else '✗'
        if actual == expected:
            passed += 1
        else:
            failed += 1

        print(f'{status} 期望: {expected:8s} 实际: {actual:8s} | "{ocr_text[:30]}"')

    print('='*70)
    print(f'测试结果: {passed} 通过, {failed} 失败')
    print('='*70)

if __name__ == '__main__':
    test_classification()
