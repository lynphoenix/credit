"""
Web API 快速测试 - 测试3张代表性图片
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import time
from pathlib import Path

API_URL = 'http://localhost:5000/api/analyze'

# 3张代表性测试图片
test_images = [
    'books/食品证书/水产品证书/非洲/摩洛哥输华水产品检验检疫证书样本、印章及签字官名单、笔迹(2022年11月11日更新)/摩洛哥输华水产品检验检疫证书样本、印章及签字官名单、笔迹(2022年11月11日更新)/摩洛哥输华水产品签字官印章及签字笔迹信息（2022年11月11日启用）/摩洛哥输华水产品签字官印章及签字笔迹信息/Specimen PP svpmn.jpg',
    'books/植物证书/亚洲(东南亚国家涉及木材 重要)/老挝植物检疫证书.jpg',
    'books/动物证书/亚洲/蒙古国2/蒙古国2/蒙古国新增签证兽医官和印章样本.png'
]

print('='*80)
print('Web API 快速测试')
print('='*80)
print()

for i, img_path in enumerate(test_images, 1):
    filename = Path(img_path).name
    print(f'[{i}/3] 测试: {filename[:50]}')

    try:
        with open(img_path, 'rb') as f:
            files = {'file': (filename, f, 'image/jpeg')}
            response = requests.post(API_URL, files=files, timeout=300)  # 超时设置为300秒

        result = response.json()

        if result.get('success'):
            res = result['result']
            cert_type_map = {'plant': '植物证书', 'animal': '动物证书', 'food': '食品证书'}
            cert_type = cert_type_map.get(res['certificate_type'], res['certificate_type'])

            print(f'  ✓ 成功')
            print(f'    证件类型: {cert_type}')
            print(f'    置信度: {res["confidence"]:.3f}')
            print(f'    鉴伪结果: {res["forgery_result"]["forgery_risk"]} ({res["forgery_result"]["forgery_score"]:.3f})')
        else:
            error = result.get('error', '未知错误')
            print(f'  ✗ 失败: {error}')

    except requests.exceptions.Timeout:
        print(f'  ✗ 超时')
    except Exception as e:
        print(f'  ✗ 异常: {str(e)}')

    print()
    time.sleep(1)

print('='*80)
print('测试完成')
