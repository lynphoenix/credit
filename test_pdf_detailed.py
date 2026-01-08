#!/usr/bin/env python3
"""
测试PDF文件识别 - 详细版
"""
import requests
import os
import json

# 测试多个PDF文件
test_pdfs = [
    "books/动物证书/大洋洲/澳大利亚/澳大利亚/澳大利亚澳大利亚输华食用水生动物卫生证书样本（2013年7月16日）/澳大利亚输华食用水生动物（水产养殖类）卫生证书样本（2013年7月16日）.pdf",
    "books/动物证书/大洋洲/澳大利亚/澳大利亚/澳大利亚澳大利亚输华食用水生动物卫生证书样本（2013年7月16日）/澳大利亚输华食用水生动物（野生捕捞类）卫生证书样本（2013年7月16日）.pdf",
]

API_URL = "http://localhost:5000/api/analyze"

success_count = 0
fail_count = 0

for test_pdf in test_pdfs:
    print(f"\n{'='*80}")
    print(f"测试PDF: {os.path.basename(test_pdf)}")
    print(f"{'='*80}")
    
    if not os.path.exists(test_pdf):
        print(f"❌ 文件不存在")
        fail_count += 1
        continue
    
    try:
        with open(test_pdf, 'rb') as f:
            files = {'file': (os.path.basename(test_pdf), f, 'application/pdf')}
            response = requests.post(API_URL, files=files, timeout=120)
        
        print(f"HTTP状态码: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            print("✅ 识别成功")
            data = result.get('result', {})
            
            print(f"\n证件类型: {data.get('certificate_type')}")
            print(f"置信度: {data.get('confidence', 0):.2%}")
            
            # 提取的字段
            fields = data.get('extracted_fields', {})
            print(f"\n提取的字段 ({len(fields)}个):")
            for key, value in fields.items():
                if value:
                    print(f"  - {key}: {value}")
            
            # 鉴伪结果
            forgery = data.get('forgery_result', {})
            print(f"\n鉴伪结果:")
            print(f"  - 综合评分: {forgery.get('forgery_score', 0):.2%}")
            print(f"  - 风险等级: {forgery.get('forgery_risk', 'unknown')}")
            
            success_count += 1
        else:
            print(f"❌ 识别失败: {result.get('error')}")
            fail_count += 1
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        fail_count += 1

print(f"\n{'='*80}")
print("PDF测试总结")
print(f"{'='*80}")
print(f"总测试数: {success_count + fail_count}")
print(f"成功: {success_count}")
print(f"失败: {fail_count}")
print(f"成功率: {success_count/(success_count + fail_count)*100:.1f}%")
