"""
模块2: 证件语义结构化信息提取
功能：根据证件类型，提取证件上的结构化内容信息
"""
import re
from typing import Dict, Optional, List
from datetime import datetime
import json


class CertificateExtractor:
    """证件信息提取器"""

    def __init__(self):
        """初始化提取器"""
        # 字段提取模式
        self.field_patterns = {
            # 通用字段
            'certificate_number': [
                r'(?:Certificate\s+No|No\.|NO\.|Number|编号)[\.:\s：]*([A-Z0-9\-/]+)',
                r'\b([A-Z]{2,}\d{4,}[-/]\d+[-/]\d+)\b',  # 匹配类似格式
                r'(\d{4,}[-]\d{3}[-]\d{2,})',  # 8010-203-60格式
            ],
            'issue_date': [
                r'(?:Date\s+Issued|签发日期|Issue\s+Date)[\.:\s：]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})',
                r'(?:Date\s+Issued|签发日期)[\.:\s：]*(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})',
            ],
            'inspection_date': [
                r'(?:Date\s+Inspected|检验日期|Inspection\s+Date)[\.:\s：]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})',
            ],
            'issuer': [
                r'(MINISTRY\s+OF\s+[A-Z\s]+(?:AND\s+[A-Z]+)?)',
                r'(DEPARTMENT\s+OF\s+[A-Z\s]+)',
                r'(?:Issued\s+by|签发机构|Authority)[\.:\s：]*([^\n]{10,})',
            ],
            'origin': [
                r'(?:Place\s+of\s+origin|产地)[\.:\s：]*([^\n]+)',
                r'Piaco\s+of\s+origin[\.:\s：]*([^\n]+)',
            ],
            'destination': [
                r'(?:Destination|目的地)[\.:\s：]*([^\n]+)',
                r'(?:point\s+of\s+entry)[\.:\s：]*([^\n]+)',
            ],
            'applicant': [
                r'(?:Name\s+and\s+address\s+of\s+exer)[\.:\s：]*([^\n]+)',
                r'(?:Applicant|申请人|Exporter|出口商)[\.:\s：]*([^\n]+)',
            ],
            'goods_name': [
                r'(?:Name\s+of\s+product\s+and\s+quantit)[\.:\s：]*([^\n]+)',
                r'(?:Product|货物名称|商品名称)[\.:\s：]*([^\n]+)',
                r'This\s+cosignment\s+of\s+(\w+)',  # "This cosignment of watermelon"
            ],
            'goods_quantity': [
                r'(?:Quantity|数量|quantit)[\.:\s：]*([^\n]+)',
                r'(?:Weight|重量)[\.:\s：]*([0-9.,\s]+(?:kg|KG|tons?|MT|吨)?)',
            ],
        }

        # 植物证书特有字段
        self.plant_patterns = {
            'botanical_name': [
                r'(?:Botanical\s+name\s*of\s+plants|植物学名|Scientific\s+name)[\.:\s：]*([^\n]+)',
                r'Botanical\s+name[a-z]*\s+plants[\.:\s：]*([^\n]+)',
            ],
            'treatment': [
                r'(?:Treatment[\.:\s：]+)([^\n]+)',
                r'(?:TREATMENT)[\.:\s：]*([^\n]+)',
                r'(?:Chemical\s*\([^)]+\))[\.:\s：]*([^\n]+)',
            ],
            'treatment_date': [
                r'(?:Treatment\s+Date|处理日期)[\.:\s：]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})',
            ],
            'protocol_info': [
                r'(Protocol\s+on\s+the\s+[^\.]+)',
            ],
        }

        # 动物证书特有字段
        self.animal_patterns = {
            'species': [
                r'(?:Species|物种|Animal\s+species)[\s:：]*([^\n]+)',
            ],
            'veterinary_info': [
                r'(?:Veterinary|兽医|Health\s+certificate)[\s:：]*([^\n]+)',
            ],
            'inspection_date': [
                r'(?:Date\s+Inspected|检验日期|Inspection\s+Date)[\s:：]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})',
            ],
        }

        # 食品证书特有字段
        self.food_patterns = {
            'production_date': [
                r'(?:Production\s+Date|生产日期|Manufactured)[\s:：]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})',
            ],
            'expiry_date': [
                r'(?:Expiry\s+Date|有效期|Valid\s+until)[\s:：]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})',
            ],
            'batch_number': [
                r'(?:Batch\s+No|批号|Lot\s+No)[\s:：]*([A-Z0-9\-/]+)',
            ],
        }

    def extract(self, ocr_text: str, certificate_type: str) -> Dict:
        """
        提取证件的结构化信息

        Args:
            ocr_text: OCR识别的文本
            certificate_type: 证件类型 ('animal', 'plant', 'food')

        Returns:
            提取的结构化信息字典
        """
        result = {
            'certificate_type': certificate_type,
            'extracted_fields': {},
            'raw_text': ocr_text
        }

        # 提取通用字段
        result['extracted_fields'].update(self._extract_fields(ocr_text, self.field_patterns))

        # 根据证件类型提取特定字段
        if certificate_type == 'plant':
            result['extracted_fields'].update(self._extract_fields(ocr_text, self.plant_patterns))
        elif certificate_type == 'animal':
            result['extracted_fields'].update(self._extract_fields(ocr_text, self.animal_patterns))
        elif certificate_type == 'food':
            result['extracted_fields'].update(self._extract_fields(ocr_text, self.food_patterns))

        # 清理和标准化提取的字段
        result['extracted_fields'] = self._clean_fields(result['extracted_fields'])

        # 提取额外信息
        result['additional_info'] = self._extract_additional_info(ocr_text, certificate_type)

        return result

    def _extract_fields(self, text: str, patterns: Dict[str, List[str]]) -> Dict[str, Optional[str]]:
        """
        使用正则表达式提取字段

        Args:
            text: 文本内容
            patterns: 字段模式字典

        Returns:
            提取的字段字典
        """
        extracted = {}

        for field_name, pattern_list in patterns.items():
            value = None
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1) if match.lastindex else match.group(0)
                    break
            extracted[field_name] = value

        return extracted

    def _clean_fields(self, fields: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
        """
        清理和标准化提取的字段

        Args:
            fields: 原始字段字典

        Returns:
            清理后的字段字典
        """
        cleaned = {}

        for key, value in fields.items():
            if value:
                # 去除首尾空白
                value = value.strip()
                # 去除多余空格
                value = re.sub(r'\s+', ' ', value)
                # 去除特殊字符
                value = value.strip(':：')

                # 如果值太短或只是空白，设为None
                if len(value) < 2 or value.isspace():
                    value = None

            cleaned[key] = value

        return cleaned

    def _extract_additional_info(self, text: str, certificate_type: str) -> Dict:
        """
        提取额外信息

        Args:
            text: 文本内容
            certificate_type: 证件类型

        Returns:
            额外信息字典
        """
        additional = {}

        # 提取关键词
        keywords = self._extract_keywords(text, certificate_type)
        additional['keywords'] = keywords

        # 提取国家/地区信息
        countries = self._extract_countries(text)
        if countries:
            additional['countries'] = countries

        # 提取数字信息（可能是证书编号、数量等）
        numbers = re.findall(r'\b\d{4,}\b', text)
        if numbers:
            additional['numbers'] = numbers[:5]  # 只保留前5个

        return additional

    def _extract_keywords(self, text: str, certificate_type: str) -> List[str]:
        """
        提取关键词

        Args:
            text: 文本内容
            certificate_type: 证件类型

        Returns:
            关键词列表
        """
        keywords = []

        # 通用关键词
        common_keywords = [
            'certificate', 'quarantine', 'inspection', 'health',
            'sanitary', 'phytosanitary', 'veterinary'
        ]

        # 类型特定关键词
        type_keywords = {
            'plant': ['plant', 'botanical', 'phyto', 'flora', 'wood', 'timber'],
            'animal': ['animal', 'veterinary', 'meat', 'fish', 'livestock'],
            'food': ['food', 'edible', 'consumption', 'nutrition']
        }

        # 搜索关键词
        text_lower = text.lower()
        for keyword in common_keywords:
            if keyword in text_lower:
                keywords.append(keyword)

        if certificate_type in type_keywords:
            for keyword in type_keywords[certificate_type]:
                if keyword in text_lower and keyword not in keywords:
                    keywords.append(keyword)

        return keywords

    def _extract_countries(self, text: str) -> List[str]:
        """
        提取国家/地区名称

        Args:
            text: 文本内容

        Returns:
            国家列表
        """
        # 常见国家名称列表（可以扩展）
        countries = [
            'China', 'Lao', 'Laos', 'Vietnam', 'Thailand', 'Myanmar', 'Cambodia',
            'Malaysia', 'Singapore', 'Indonesia', 'Philippines',
            'USA', 'Canada', 'Mexico', 'Brazil', 'Argentina',
            'Australia', 'New Zealand',
            'Japan', 'Korea', 'India',
            'Russia', 'Germany', 'France', 'UK', 'Italy', 'Spain'
        ]

        found_countries = []
        for country in countries:
            if re.search(r'\b' + country + r'\b', text, re.IGNORECASE):
                if country not in found_countries:
                    found_countries.append(country)

        return found_countries

    def format_for_database(self, extracted_data: Dict) -> Dict:
        """
        将提取的数据格式化为数据库格式

        Args:
            extracted_data: 提取的数据

        Returns:
            数据库格式的字典
        """
        fields = extracted_data.get('extracted_fields', {})
        additional = extracted_data.get('additional_info', {})

        db_format = {
            'certificate_type': extracted_data.get('certificate_type'),
            'certificate_number': fields.get('certificate_number'),
            'issuer': fields.get('issuer'),
            'issue_date': fields.get('issue_date'),
            'applicant': fields.get('applicant'),
            'goods_name': fields.get('goods_name'),
            'goods_quantity': fields.get('goods_quantity'),
            'origin': fields.get('origin'),
            'destination': fields.get('destination'),
            'ocr_text': extracted_data.get('raw_text'),
            'additional_info': json.dumps(additional, ensure_ascii=False)
        }

        # 添加类型特定字段
        cert_type = extracted_data.get('certificate_type')
        if cert_type == 'plant':
            db_format['botanical_name'] = fields.get('botanical_name')
            db_format['treatment'] = fields.get('treatment')
        elif cert_type == 'animal':
            db_format['species'] = fields.get('species')
            db_format['inspection_date'] = fields.get('inspection_date')
        elif cert_type == 'food':
            db_format['production_date'] = fields.get('production_date')
            db_format['expiry_date'] = fields.get('expiry_date')

        return db_format


if __name__ == '__main__':
    # 设置控制台编码
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # 测试代码
    from module1_detection import CertificateDetector

    # 初始化检测器和提取器
    detector = CertificateDetector()
    extractor = CertificateExtractor()

    # 测试图像
    test_image = 'books/植物证书/亚洲(东南亚国家涉及木材 重要)/老挝植物检疫证书.jpg'

    print(f"正在处理: {test_image}")
    print("="*80)

    # 步骤1: 检测证件
    detection_result = detector.detect_certificate(test_image)

    if detection_result['has_certificate']:
        print(f"\n[+] 检测到证件: {detection_result['certificate_type']}")
        print(f"置信度: {detection_result['confidence']:.2f}")

        # 步骤2: 提取结构化信息
        extraction_result = extractor.extract(
            detection_result['ocr_text'],
            detection_result['certificate_type']
        )

        print("\n提取的结构化信息:")
        print("-"*80)
        for field, value in extraction_result['extracted_fields'].items():
            if value:
                print(f"{field:20s}: {value}")

        print("\n额外信息:")
        print("-"*80)
        for key, value in extraction_result['additional_info'].items():
            print(f"{key:20s}: {value}")

        # 步骤3: 格式化为数据库格式
        db_data = extractor.format_for_database(extraction_result)
        print("\n数据库格式:")
        print("-"*80)
        for key, value in db_data.items():
            if value and key != 'ocr_text' and key != 'additional_info':
                print(f"{key:20s}: {value}")
    else:
        print("[-] 未检测到证件")

    print("\n" + "="*80)
