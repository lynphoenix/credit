"""
测试OCR结果格式调试脚本
"""
from paddleocr import PaddleOCR
from config import OCR_CONFIG
import json

# 初始化OCR
ocr = PaddleOCR(**OCR_CONFIG)

# 测试图像
test_image = 'books/植物证书/亚洲(东南亚国家涉及木材 重要)/老挝植物检疫证书.jpg'

print(f"测试图像: {test_image}")
print("="*80)

# 执行OCR
result = ocr.predict(test_image)

print(f"\n结果类型: {type(result)}")
print(f"结果长度: {len(result) if isinstance(result, list) else 'N/A'}")

if isinstance(result, list) and len(result) > 0:
    first_item = result[0]
    print(f"\n第一个元素类型: {type(first_item)}")
    print(f"第一个元素类名: {first_item.__class__.__name__}")

    # 检查是否有json属性
    if hasattr(first_item, 'json'):
        print("\n找到 .json 属性")
        json_data = first_item.json
        print(f"JSON数据类型: {type(json_data)}")

        if isinstance(json_data, dict):
            print(f"\nJSON字典的键: {list(json_data.keys())}")

            # 打印每个键的前几个元素
            for key, value in json_data.items():
                if isinstance(value, list):
                    print(f"\n{key} (列表, 长度={len(value)}):")
                    if len(value) > 0:
                        print(f"  第一个元素类型: {type(value[0])}")
                        if len(value) <= 3:
                            print(f"  内容: {value}")
                        else:
                            print(f"  前3个元素: {value[:3]}")
                elif isinstance(value, str):
                    print(f"\n{key} (字符串): {value[:100]}")
                else:
                    print(f"\n{key} ({type(value)}): {value}")

    # 检查是否有str属性
    if hasattr(first_item, 'str'):
        print("\n\n找到 .str 属性:")
        print(type(first_item.str))
        # str是一个属性，不是方法，直接print
        print(first_item.str)

    # 检查是否有print方法
    if hasattr(first_item, 'print'):
        print("\n\n调用 .print() 方法:")
        first_item.print()

    # 提取rec_text用于测试
    if 'res' in json_data and isinstance(json_data['res'], dict):
        res = json_data['res']
        if 'rec_text' in res:
            print("\n\n从res中提取rec_text:")
            rec_texts = res['rec_text']
            print(f"rec_text类型: {type(rec_texts)}")
            print(f"rec_text长度: {len(rec_texts) if isinstance(rec_texts, list) else 'N/A'}")
            if isinstance(rec_texts, list) and len(rec_texts) > 0:
                print(f"前5个文本: {rec_texts[:5]}")
