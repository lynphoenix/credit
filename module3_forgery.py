"""
模块3: 证件鉴伪系统
功能：从图像、文本和结构三个方面进行特征识别并鉴伪
"""
import cv2
import numpy as np
from typing import Dict, Tuple, List
import torch
import torch.nn as nn
from PIL import Image
import json


class ImageForgeryDetector:
    """图像层面伪造检测器

    使用CNN检测图像中的物理伪造痕迹：
    - 拼接伪影
    - 分辨率不一致
    - 水印缺失或异常
    """

    def __init__(self):
        """初始化图像检测器"""
        # 简化的CNN模型（实际应用中需要训练）
        self.model = self._build_simple_cnn()

    def _build_simple_cnn(self):
        """构建简单的CNN模型用于伪造检测"""
        class SimpleForgeryNet(nn.Module):
            def __init__(self):
                super(SimpleForgeryNet, self).__init__()
                self.features = nn.Sequential(
                    nn.Conv2d(3, 32, 3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2, 2),
                    nn.Conv2d(32, 64, 3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2, 2),
                    nn.Conv2d(64, 128, 3, padding=1),
                    nn.ReLU(),
                    nn.AdaptiveAvgPool2d((1, 1))
                )
                self.classifier = nn.Sequential(
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.Dropout(0.5),
                    nn.Linear(64, 1),
                    nn.Sigmoid()
                )

            def forward(self, x):
                x = self.features(x)
                x = x.view(x.size(0), -1)
                x = self.classifier(x)
                return x

        return SimpleForgeryNet()

    def detect(self, image_path: str) -> Dict:
        """
        检测图像中的伪造痕迹

        Args:
            image_path: 图像路径

        Returns:
            检测结果字典
        """
        result = {
            'forgery_score': 0.0,
            'analysis': [],
            'details': {}
        }

        try:
            # 读取图像
            with open(image_path, 'rb') as f:
                image_data = np.frombuffer(f.read(), np.uint8)
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

            if image is None:
                result['analysis'].append("无法读取图像")
                return result

            # 1. 检测拼接伪影
            splice_score = self._detect_splicing(image)
            result['details']['splice_score'] = splice_score
            if splice_score > 0.5:
                result['analysis'].append(f"检测到拼接伪影 (得分: {splice_score:.2f})")

            # 2. 检测分辨率不一致
            resolution_score = self._detect_resolution_inconsistency(image)
            result['details']['resolution_score'] = resolution_score
            if resolution_score > 0.5:
                result['analysis'].append(f"检测到分辨率不一致 (得分: {resolution_score:.2f})")

            # 3. 检测JPEG压缩伪影
            jpeg_score = self._detect_jpeg_artifacts(image)
            result['details']['jpeg_score'] = jpeg_score
            if jpeg_score > 0.5:
                result['analysis'].append(f"检测到JPEG压缩异常 (得分: {jpeg_score:.2f})")

            # 4. 检测边缘异常
            edge_score = self._detect_edge_anomalies(image)
            result['details']['edge_score'] = edge_score
            if edge_score > 0.5:
                result['analysis'].append(f"检测到边缘异常 (得分: {edge_score:.2f})")

            # 综合评分
            result['forgery_score'] = (splice_score + resolution_score + jpeg_score + edge_score) / 4

            if not result['analysis']:
                result['analysis'].append("未检测到明显的图像伪造痕迹")

        except Exception as e:
            result['analysis'].append(f"图像检测错误: {str(e)}")

        return result

    def _detect_splicing(self, image: np.ndarray) -> float:
        """检测拼接伪影"""
        # 使用ELA (Error Level Analysis) 技术
        # 简化实现：检测图像不同区域的压缩差异
        try:
            h, w = image.shape[:2]
            # 将图像分成网格
            grid_size = 64
            scores = []

            for i in range(0, h - grid_size, grid_size):
                for j in range(0, w - grid_size, grid_size):
                    block = image[i:i+grid_size, j:j+grid_size]
                    # 计算块的标准差
                    std = np.std(block)
                    scores.append(std)

            if len(scores) > 0:
                # 如果标准差差异很大，可能存在拼接
                score_std = np.std(scores)
                return min(score_std / 100.0, 1.0)

        except:
            pass

        return 0.0

    def _detect_resolution_inconsistency(self, image: np.ndarray) -> float:
        """检测分辨率不一致"""
        try:
            # 使用拉普拉斯算子检测不同区域的清晰度
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)

            h, w = gray.shape
            grid_size = 100
            sharpness_scores = []

            for i in range(0, h - grid_size, grid_size):
                for j in range(0, w - grid_size, grid_size):
                    block = laplacian[i:i+grid_size, j:j+grid_size]
                    sharpness = np.var(block)
                    sharpness_scores.append(sharpness)

            if len(sharpness_scores) > 1:
                # 清晰度差异大可能表示分辨率不一致
                score_std = np.std(sharpness_scores)
                mean_score = np.mean(sharpness_scores)
                if mean_score > 0:
                    return min(score_std / mean_score, 1.0)

        except:
            pass

        return 0.0

    def _detect_jpeg_artifacts(self, image: np.ndarray) -> float:
        """检测JPEG压缩伪影"""
        try:
            # 检测8x8块边界的不连续性
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 计算8的倍数位置的梯度
            block_size = 8
            discontinuities = []

            h, w = gray.shape
            for i in range(block_size, h - block_size, block_size):
                diff = np.abs(gray[i, :] - gray[i-1, :])
                discontinuities.append(np.mean(diff))

            for j in range(block_size, w - block_size, block_size):
                diff = np.abs(gray[:, j] - gray[:, j-1])
                discontinuities.append(np.mean(diff))

            if discontinuities:
                score = np.mean(discontinuities) / 50.0
                return min(score, 1.0)

        except:
            pass

        return 0.0

    def _detect_edge_anomalies(self, image: np.ndarray) -> float:
        """检测边缘异常"""
        try:
            # 使用Canny边缘检测
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)

            # 计算边缘密度
            edge_density = np.sum(edges > 0) / edges.size

            # 异常高或异常低的边缘密度都可疑
            if edge_density < 0.01 or edge_density > 0.3:
                return min(abs(edge_density - 0.15) / 0.15, 1.0)

        except:
            pass

        return 0.0


class TextConsistencyChecker:
    """文本层面一致性校验器

    通过NLP检测文本中的逻辑矛盾：
    - 日期逻辑矛盾
    - 地址信息不一致
    - 关键词异常搭配
    - 非标准术语使用
    """

    def __init__(self):
        """初始化文本检查器"""
        self.standard_terms = {
            'plant': [
                'phytosanitary', 'botanical', 'quarantine', 'plant',
                'ministry of agriculture', 'department of agriculture'
            ],
            'animal': [
                'veterinary', 'animal', 'quarantine', 'inspection',
                'ministry of agriculture', 'health certificate'
            ],
            'food': [
                'food', 'sanitary', 'health', 'inspection',
                'certificate', 'quarantine'
            ]
        }

    def check(self, ocr_text: str, extracted_fields: Dict, certificate_type: str) -> Dict:
        """
        检查文本一致性

        Args:
            ocr_text: OCR文本
            extracted_fields: 提取的字段
            certificate_type: 证件类型

        Returns:
            检查结果字典
        """
        result = {
            'consistency_score': 0.0,
            'issues': [],
            'details': {}
        }

        try:
            text_lower = ocr_text.lower()

            # 1. 检查日期逻辑
            date_score = self._check_date_logic(extracted_fields)
            result['details']['date_consistency'] = date_score
            if date_score > 0.5:
                result['issues'].append(f"日期逻辑异常 (得分: {date_score:.2f})")

            # 2. 检查关键词标准性
            term_score = self._check_terminology(text_lower, certificate_type)
            result['details']['terminology_score'] = term_score
            if term_score > 0.5:
                result['issues'].append(f"术语使用异常 (得分: {term_score:.2f})")

            # 3. 检查字段完整性
            completeness_score = self._check_field_completeness(extracted_fields)
            result['details']['completeness_score'] = completeness_score
            if completeness_score > 0.5:
                result['issues'].append(f"必填字段缺失 (得分: {completeness_score:.2f})")

            # 4. 检查文本格式
            format_score = self._check_text_format(ocr_text)
            result['details']['format_score'] = format_score
            if format_score > 0.5:
                result['issues'].append(f"文本格式异常 (得分: {format_score:.2f})")

            # 综合评分
            result['consistency_score'] = (date_score + term_score + completeness_score + format_score) / 4

            if not result['issues']:
                result['issues'].append("未检测到文本一致性问题")

        except Exception as e:
            result['issues'].append(f"文本检查错误: {str(e)}")

        return result

    def _check_date_logic(self, fields: Dict) -> float:
        """检查日期逻辑"""
        # 简化实现：检查关键日期字段是否存在
        date_fields = ['issue_date', 'inspection_date', 'production_date', 'expiry_date']
        found_dates = sum(1 for field in date_fields if fields.get(field))

        if found_dates == 0:
            return 0.7  # 没有日期字段是可疑的

        return 0.0

    def _check_terminology(self, text: str, cert_type: str) -> float:
        """检查术语标准性"""
        if cert_type not in self.standard_terms:
            return 0.0

        standard = self.standard_terms[cert_type]
        found = sum(1 for term in standard if term in text)

        # 至少应该包含一半的标准术语
        if found < len(standard) * 0.3:
            return 0.6

        return 0.0

    def _check_field_completeness(self, fields: Dict) -> float:
        """检查字段完整性"""
        required_fields = ['issuer', 'goods_name']
        missing = sum(1 for field in required_fields if not fields.get(field))

        if missing > 0:
            return missing / len(required_fields)

        return 0.0

    def _check_text_format(self, text: str) -> float:
        """检查文本格式"""
        # 检查文本长度
        if len(text) < 100:
            return 0.8  # 文本太短

        # 检查是否有足够的字母字符
        alpha_ratio = sum(c.isalpha() for c in text) / len(text)
        if alpha_ratio < 0.3:
            return 0.6

        return 0.0


class StructureValidator:
    """结构与格式层面校验器

    校验证件的结构特征：
    - 字段布局
    - 字体规范
    - 格式模板匹配
    """

    def __init__(self):
        """初始化结构校验器"""
        pass

    def validate(self, ocr_result, certificate_type: str, bbox: List[int]) -> Dict:
        """
        校验证件结构

        Args:
            ocr_result: OCR结果
            certificate_type: 证件类型
            bbox: 证件边界框

        Returns:
            校验结果字典
        """
        result = {
            'structure_score': 0.0,
            'issues': [],
            'details': {}
        }

        try:
            # 1. 检查文本框数量
            text_count_score = self._check_text_count(ocr_result, certificate_type)
            result['details']['text_count_score'] = text_count_score
            if text_count_score > 0.5:
                result['issues'].append(f"文本框数量异常 (得分: {text_count_score:.2f})")

            # 2. 检查布局规范性
            layout_score = self._check_layout(ocr_result, bbox)
            result['details']['layout_score'] = layout_score
            if layout_score > 0.5:
                result['issues'].append(f"布局不规范 (得分: {layout_score:.2f})")

            # 3. 检查文本对齐
            alignment_score = self._check_alignment(ocr_result)
            result['details']['alignment_score'] = alignment_score
            if alignment_score > 0.5:
                result['issues'].append(f"文本对齐异常 (得分: {alignment_score:.2f})")

            # 综合评分
            result['structure_score'] = (text_count_score + layout_score + alignment_score) / 3

            if not result['issues']:
                result['issues'].append("未检测到结构问题")

        except Exception as e:
            result['issues'].append(f"结构校验错误: {str(e)}")

        return result

    def _check_text_count(self, ocr_result, cert_type: str) -> float:
        """检查文本框数量"""
        try:
            if isinstance(ocr_result, list) and len(ocr_result) > 0:
                first_item = ocr_result[0]
                if hasattr(first_item, 'json'):
                    result_json = first_item.json
                    if isinstance(result_json, dict) and 'res' in result_json:
                        res = result_json['res']
                        if 'rec_texts' in res:
                            text_count = len(res['rec_texts'])

                            # 正常证书应该有20-100个文本框
                            if text_count < 20:
                                return 0.7
                            elif text_count > 150:
                                return 0.5
        except:
            pass

        return 0.0

    def _check_layout(self, ocr_result, bbox: List[int]) -> float:
        """检查布局"""
        # 简化实现：检查文本是否分布在整个证书区域
        try:
            if bbox and len(bbox) == 4:
                x, y, w, h = bbox
                aspect_ratio = w / h if h > 0 else 0

                # 证书通常是横向的，宽高比约在1.2-1.8之间
                if aspect_ratio < 0.8 or aspect_ratio > 2.5:
                    return 0.6
        except:
            pass

        return 0.0

    def _check_alignment(self, ocr_result) -> float:
        """检查文本对齐"""
        # 简化实现
        return 0.0


class ForgeryDetectionSystem:
    """证件鉴伪系统主类"""

    def __init__(self):
        """初始化鉴伪系统"""
        self.image_detector = ImageForgeryDetector()
        self.text_checker = TextConsistencyChecker()
        self.structure_validator = StructureValidator()

        # 特征融合权重
        self.weights = {
            'image': 0.4,
            'text': 0.35,
            'structure': 0.25
        }

    def detect(self, image_path: str, ocr_result, ocr_text: str,
               extracted_fields: Dict, certificate_type: str, bbox: List[int]) -> Dict:
        """
        综合检测证件真伪

        Args:
            image_path: 图像路径
            ocr_result: OCR结果
            ocr_text: OCR文本
            extracted_fields: 提取的字段
            certificate_type: 证件类型
            bbox: 边界框

        Returns:
            检测结果字典
        """
        result = {
            'forgery_risk': 'genuine',
            'forgery_score': 0.0,
            'image_score': 0.0,
            'text_score': 0.0,
            'structure_score': 0.0,
            'image_analysis': '',
            'text_analysis': '',
            'structure_analysis': '',
            'recommendation': ''
        }

        try:
            # 1. 图像层面检测
            image_result = self.image_detector.detect(image_path)
            result['image_score'] = image_result['forgery_score']
            result['image_analysis'] = '\n'.join(image_result['analysis'])

            # 2. 文本层面检测
            text_result = self.text_checker.check(ocr_text, extracted_fields, certificate_type)
            result['text_score'] = text_result['consistency_score']
            result['text_analysis'] = '\n'.join(text_result['issues'])

            # 3. 结构层面检测
            structure_result = self.structure_validator.validate(ocr_result, certificate_type, bbox)
            result['structure_score'] = structure_result['structure_score']
            result['structure_analysis'] = '\n'.join(structure_result['issues'])

            # 4. 特征融合
            final_score = (
                result['image_score'] * self.weights['image'] +
                result['text_score'] * self.weights['text'] +
                result['structure_score'] * self.weights['structure']
            )
            result['forgery_score'] = final_score

            # 5. 风险等级判定
            if final_score < 0.5:
                result['forgery_risk'] = 'genuine'
                result['recommendation'] = '证件真实性较高，建议通过'
            elif final_score < 0.8:
                result['forgery_risk'] = 'suspicious'
                result['recommendation'] = '证件存在可疑特征，建议人工复核'
            else:
                result['forgery_risk'] = 'forged'
                result['recommendation'] = '证件伪造风险高，建议拒绝'

        except Exception as e:
            result['recommendation'] = f'检测过程出错: {str(e)}'

        return result


if __name__ == '__main__':
    # 设置控制台编码
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # 测试代码
    from module1_detection import CertificateDetector
    from module2_extraction import CertificateExtractor

    # 初始化所有模块
    detector = CertificateDetector()
    extractor = CertificateExtractor()
    forgery_system = ForgeryDetectionSystem()

    # 测试图像
    test_image = 'books/植物证书/亚洲(东南亚国家涉及木材 重要)/老挝植物检疫证书.jpg'

    print(f"正在处理: {test_image}")
    print("="*80)

    # 步骤1: 检测证件
    detection_result = detector.detect_certificate(test_image)

    if detection_result['has_certificate']:
        print(f"\n[+] 检测到证件: {detection_result['certificate_type']}")

        # 步骤2: 提取结构化信息
        extraction_result = extractor.extract(
            detection_result['ocr_text'],
            detection_result['certificate_type']
        )

        # 步骤3: 鉴伪检测
        forgery_result = forgery_system.detect(
            test_image,
            detection_result['ocr_result'],
            detection_result['ocr_text'],
            extraction_result['extracted_fields'],
            detection_result['certificate_type'],
            detection_result['bbox']
        )

        print("\n鉴伪检测结果:")
        print("-"*80)
        print(f"综合评分: {forgery_result['forgery_score']:.3f}")
        print(f"风险等级: {forgery_result['forgery_risk']}")
        print(f"建议: {forgery_result['recommendation']}")

        print(f"\n图像分析 (得分: {forgery_result['image_score']:.3f}):")
        print(f"  {forgery_result['image_analysis']}")

        print(f"\n文本分析 (得分: {forgery_result['text_score']:.3f}):")
        print(f"  {forgery_result['text_analysis']}")

        print(f"\n结构分析 (得分: {forgery_result['structure_score']:.3f}):")
        print(f"  {forgery_result['structure_analysis']}")
    else:
        print("[-] 未检测到证件")

    print("\n" + "="*80)
