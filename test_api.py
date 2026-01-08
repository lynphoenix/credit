#!/usr/bin/env python3
"""
API测试脚本 - 测试证件识别功能
"""
import requests
import json
import os
import sys

# 测试图片列表
test_images = [
    "books/食品证书/水产品证书/非洲/摩洛哥输华水产品检验检疫证书样本、印章及签字官名单、笔迹(2022年11月11日更新)/摩洛哥输华水产品检验检疫证书样本、印章及签字官名单、笔迹(2022年11月11日更新)/摩洛哥输华水产品签字官印章及签字笔迹信息（2022年11月11日启用）/摩洛哥输华水产品签字官印章及签字笔迹信息/Specimen PP svpmn.jpg",
    "books/食品证书/水产品证书/大洋洲/斐济输华水产品卫生证书样本、印章及签字官名单、笔迹(2023年3月1日更新)/斐济输华水产品卫生证书样本、印章及签字官名单、笔迹(2023年3月1日更新)/1.斐济输华水产品卫生证书官方印章(2022年11月11日启用).png",
    "books/WechatIMG329.jpg",
    "books/食品证书/水产品证书/非洲/毛里塔尼亚输华水产品检验检疫证书样本、印章及签字官名单、笔迹(2021年11月11日更新)/毛里塔尼亚输华水产品卫生证书签字官笔迹和印章信息（2022年11月11日新增）.jpg",
    "books/食品证书/水产品证书/南美洲/苏里南输华水产品检验检疫证书样本、印章及签字官名单、笔迹(2021年8月11日更新)/苏里南输华水产品检验检疫证书样本、印章及签字官名单、笔迹(2021年8月11日更新)/苏里南输华水产品卫生证书官方授权签字官员名单及其笔迹和官方印章(2020年6月12日启用).jpg",
    "books/动物证书/亚洲/蒙古国2/蒙古国2/蒙古国新增签证兽医官和印章样本.png",
    "books/植物证书/亚洲(东南亚国家涉及木材 重要)/老挝植物检疫证书.jpg",
    "books/食品证书/水产品证书/大洋洲/斐济输华水产品卫生证书样本、印章及签字官名单、笔迹(2023年3月1日更新)/斐济输华水产品卫生证书样本、印章及签字官名单、笔迹(2023年3月1日更新)/斐济输华水产品印章及签字官笔迹（2022年9月23日启用，2022年11月11日官方印章废止，签字官笔迹继续有效）.png",
    "books/食品证书/水产品证书/南美洲/苏里南输华水产品检验检疫证书样本、印章及签字官名单、笔迹(2021年8月11日更新)/苏里南输华水产品检验检疫证书样本、印章及签字官名单、笔迹(2021年8月11日更新)/苏里南输华水产品签字官及其笔迹和官方机构印章样式（2021年1月14日启用）.jpg",
    "books/食品证书/水产品证书/非洲/摩洛哥输华水产品检验检疫证书样本、印章及签字官名单、笔迹(2022年11月11日更新)/摩洛哥输华水产品检验检疫证书样本、印章及签字官名单、笔迹(2022年11月11日更新)/摩洛哥输华水产品签字官印章及签字笔迹信息（2022年11月11日启用）/摩洛哥输华水产品签字官印章及签字笔迹信息/Spécimens _ DCQ Casa.jpg",
]

API_URL = "http://localhost:5000/api/analyze"

def test_image(image_path):
    """测试单张图片"""
    print(f"\n{'='*80}")
    print(f"测试图片: {os.path.basename(image_path)}")
    print(f"路径: {image_path}")
    print(f"{'='*80}")
    
    if not os.path.exists(image_path):
        print(f"❌ 文件不存在")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f)}
            response = requests.post(API_URL, files=files, timeout=60)
        
        print(f"HTTP状态码: {response.status_code}")
        
        result = response.json()
        
        if result.get('success'):
            print("✅ 识别成功")
            data = result.get('result', {})
            
            # 证件类型
            cert_type = data.get('certificate_type', 'unknown')
            print(f"证件类型: {cert_type}")
            
            # 提取的字段
            fields = data.get('extracted_fields', {})
            print(f"\n提取的字段:")
            for key, value in fields.items():
                if value:
                    print(f"  - {key}: {value}")
            
            # 鉴伪结果
            forgery = data.get('forgery_result', {})
            print(f"\n鉴伪结果:")
            print(f"  - 综合评分: {forgery.get('forgery_score', 0):.2%}")
            print(f"  - 风险等级: {forgery.get('forgery_risk', 'unknown')}")
            print(f"  - 建议: {forgery.get('recommendation', 'N/A')}")
            
            return True
        else:
            print(f"❌ 识别失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 80)
    print("海关证件识别系统 API 测试")
    print("=" * 80)
    
    success_count = 0
    fail_count = 0
    
    for image_path in test_images:
        if test_image(image_path):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"总测试数: {len(test_images)}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"成功率: {success_count/len(test_images)*100:.1f}%")

if __name__ == "__main__":
    main()
