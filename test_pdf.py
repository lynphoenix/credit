#!/usr/bin/env python3
"""
测试PDF文件识别
"""
import requests
import os

# 测试PDF文件
test_pdf = "books/动物证书/大洋洲/澳大利亚/澳大利亚/澳大利亚澳大利亚输华食用水生动物卫生证书样本（2013年7月16日）/澳大利亚输华食用水生动物（水产养殖类）卫生证书样本（2013年7月16日）.pdf"

API_URL = "http://localhost:5000/api/analyze"

print(f"测试PDF: {os.path.basename(test_pdf)}")
print(f"文件存在: {os.path.exists(test_pdf)}")

if os.path.exists(test_pdf):
    try:
        with open(test_pdf, 'rb') as f:
            files = {'file': (os.path.basename(test_pdf), f, 'application/pdf')}
            response = requests.post(API_URL, files=files, timeout=120)
        
        print(f"HTTP状态码: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            print("✅ 识别成功")
            data = result.get('result', {})
            print(f"证件类型: {data.get('certificate_type')}")
            print(f"提取字段数: {len(data.get('extracted_fields', {}))}")
        else:
            print(f"❌ 识别失败: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
