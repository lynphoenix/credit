"""
集成测试脚本
测试所有模块的集成功能
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from module1_detection import CertificateDetector
from module2_extraction import CertificateExtractor
from module3_forgery import ForgeryDetectionSystem
import os
import json


def test_single_certificate(image_path: str):
    """测试单个证件"""
    print(f"\n{'='*100}")
    print(f"测试图像: {image_path}")
    print('='*100)

    # 初始化模块
    detector = CertificateDetector()
    extractor = CertificateExtractor()
    forgery_system = ForgeryDetectionSystem()

    try:
        # 模块1: 证件检测
        print("\n[模块1] 证件检测与OCR识别...")
        detection_result = detector.detect_certificate(image_path)

        if not detection_result['has_certificate']:
            print("  ✗ 未检测到证件")
            return False

        print(f"  ✓ 检测到证件")
        print(f"    - 证件类型: {detection_result['certificate_type']}")
        print(f"    - 置信度: {detection_result['confidence']:.2f}")
        print(f"    - 边界框: {detection_result['bbox']}")
        print(f"    - OCR文本长度: {len(detection_result['ocr_text'])} 字符")

        # 模块2: 信息提取
        print("\n[模块2] 证件信息提取...")
        extraction_result = extractor.extract(
            detection_result['ocr_text'],
            detection_result['certificate_type']
        )

        extracted_fields = extraction_result['extracted_fields']
        field_count = sum(1 for v in extracted_fields.values() if v)
        print(f"  ✓ 提取了 {field_count} 个字段")

        # 显示提取的关键字段
        key_fields = ['certificate_number', 'issuer', 'goods_name', 'origin', 'destination']
        for field in key_fields:
            value = extracted_fields.get(field)
            if value:
                print(f"    - {field}: {value[:50]}{'...' if len(value) > 50 else ''}")

        # 模块3: 鉴伪检测
        print("\n[模块3] 证件鉴伪检测...")
        forgery_result = forgery_system.detect(
            image_path,
            detection_result['ocr_result'],
            detection_result['ocr_text'],
            extracted_fields,
            detection_result['certificate_type'],
            detection_result['bbox']
        )

        print(f"  ✓ 鉴伪检测完成")
        print(f"    - 综合评分: {forgery_result['forgery_score']:.3f}")
        print(f"    - 风险等级: {forgery_result['forgery_risk']}")
        print(f"    - 图像分析得分: {forgery_result['image_score']:.3f}")
        print(f"    - 文本分析得分: {forgery_result['text_score']:.3f}")
        print(f"    - 结构分析得分: {forgery_result['structure_score']:.3f}")
        print(f"    - 建议: {forgery_result['recommendation']}")

        # 集成测试结果
        print("\n[集成测试结果]")
        print(f"  状态: 成功 ✓")
        print(f"  证件类型: {detection_result['certificate_type']}")
        print(f"  风险评估: {forgery_result['forgery_risk']} (得分: {forgery_result['forgery_score']:.3f})")

        return True

    except Exception as e:
        print(f"\n[错误] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_all_certificates():
    """测试所有证件类型"""
    print("\n" + "="*100)
    print("海关证件识别与鉴伪系统 - 集成测试")
    print("="*100)

    # 定义测试样本
    test_samples = [
        {
            'name': '老挝植物检疫证书',
            'path': 'books/植物证书/亚洲(东南亚国家涉及木材 重要)/老挝植物检疫证书.jpg',
            'expected_type': 'plant'
        },
        # 可以添加更多测试样本
    ]

    results = []
    for i, sample in enumerate(test_samples, 1):
        print(f"\n{'='*100}")
        print(f"测试 {i}/{len(test_samples)}: {sample['name']}")
        print('='*100)

        if not os.path.exists(sample['path']):
            print(f"✗ 文件不存在: {sample['path']}")
            results.append({'sample': sample['name'], 'status': 'file_not_found'})
            continue

        success = test_single_certificate(sample['path'])
        results.append({
            'sample': sample['name'],
            'status': 'success' if success else 'failed'
        })

    # 汇总测试结果
    print("\n" + "="*100)
    print("测试汇总")
    print("="*100)

    total = len(results)
    success_count = sum(1 for r in results if r['status'] == 'success')
    failed_count = sum(1 for r in results if r['status'] == 'failed')
    not_found_count = sum(1 for r in results if r['status'] == 'file_not_found')

    print(f"\n总测试数: {total}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"文件未找到: {not_found_count}")

    print("\n详细结果:")
    for r in results:
        status_symbol = '✓' if r['status'] == 'success' else '✗'
        print(f"  {status_symbol} {r['sample']}: {r['status']}")

    return success_count == total


def test_module_by_module():
    """逐模块测试"""
    print("\n" + "="*100)
    print("逐模块详细测试")
    print("="*100)

    test_image = 'books/植物证书/亚洲(东南亚国家涉及木材 重要)/老挝植物检疫证书.jpg'

    if not os.path.exists(test_image):
        print(f"✗ 测试文件不存在: {test_image}")
        return

    print("\n" + "-"*100)
    print("模块1测试: 证件检测与OCR识别")
    print("-"*100)

    try:
        detector = CertificateDetector()
        detection_result = detector.detect_certificate(test_image)

        print(f"\n检测结果:")
        print(f"  has_certificate: {detection_result['has_certificate']}")
        print(f"  certificate_type: {detection_result['certificate_type']}")
        print(f"  confidence: {detection_result['confidence']:.3f}")
        print(f"  bbox: {detection_result['bbox']}")
        print(f"  ocr_text长度: {len(detection_result['ocr_text'])} 字符")
        print(f"  OCR文本前200字符:")
        print(f"    {detection_result['ocr_text'][:200]}...")

        if detection_result['has_certificate']:
            print("\n✓ 模块1测试通过")
            ocr_text = detection_result['ocr_text']
            ocr_result = detection_result['ocr_result']
            cert_type = detection_result['certificate_type']
            bbox = detection_result['bbox']
        else:
            print("\n✗ 模块1测试失败: 未检测到证件")
            return

    except Exception as e:
        print(f"\n✗ 模块1测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "-"*100)
    print("模块2测试: 证件信息提取")
    print("-"*100)

    try:
        extractor = CertificateExtractor()
        extraction_result = extractor.extract(ocr_text, cert_type)

        print(f"\n提取的字段:")
        for field, value in extraction_result['extracted_fields'].items():
            if value:
                print(f"  {field}: {value}")

        print(f"\n额外信息:")
        for key, value in extraction_result['additional_info'].items():
            print(f"  {key}: {value}")

        print("\n✓ 模块2测试通过")
        extracted_fields = extraction_result['extracted_fields']

    except Exception as e:
        print(f"\n✗ 模块2测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "-"*100)
    print("模块3测试: 证件鉴伪检测")
    print("-"*100)

    try:
        forgery_system = ForgeryDetectionSystem()
        forgery_result = forgery_system.detect(
            test_image,
            ocr_result,
            ocr_text,
            extracted_fields,
            cert_type,
            bbox
        )

        print(f"\n鉴伪结果:")
        print(f"  forgery_score: {forgery_result['forgery_score']:.3f}")
        print(f"  forgery_risk: {forgery_result['forgery_risk']}")
        print(f"  image_score: {forgery_result['image_score']:.3f}")
        print(f"  text_score: {forgery_result['text_score']:.3f}")
        print(f"  structure_score: {forgery_result['structure_score']:.3f}")

        print(f"\n图像分析:")
        print(f"  {forgery_result['image_analysis']}")

        print(f"\n文本分析:")
        print(f"  {forgery_result['text_analysis']}")

        print(f"\n结构分析:")
        print(f"  {forgery_result['structure_analysis']}")

        print(f"\n建议:")
        print(f"  {forgery_result['recommendation']}")

        print("\n✓ 模块3测试通过")

    except Exception as e:
        print(f"\n✗ 模块3测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*100)
    print("✓ 所有模块测试通过!")
    print("="*100)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='海关证件识别与鉴伪系统 - 集成测试')
    parser.add_argument('--mode', choices=['integration', 'modules', 'single'],
                        default='integration',
                        help='测试模式: integration(集成测试), modules(逐模块测试), single(单个文件测试)')
    parser.add_argument('--file', type=str,
                        help='单个文件测试时的图像路径')

    args = parser.parse_args()

    if args.mode == 'integration':
        success = test_all_certificates()
        sys.exit(0 if success else 1)

    elif args.mode == 'modules':
        test_module_by_module()

    elif args.mode == 'single':
        if not args.file:
            print("错误: 单个文件测试需要指定 --file 参数")
            sys.exit(1)

        if not os.path.exists(args.file):
            print(f"错误: 文件不存在: {args.file}")
            sys.exit(1)

        test_single_certificate(args.file)
