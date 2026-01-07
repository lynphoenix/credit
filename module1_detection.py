"""
模块1: 证件检测与OCR识别
功能：检测图像中是否存在证件，识别证件类型，并进行OCR文本提取
"""
import cv2
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image
import os
from typing import Dict, Tuple, List, Optional
from config import OCR_CONFIG, CERTIFICATE_TYPES


class CertificateDetector:
    """证件检测器"""

    def __init__(self):
        """初始化OCR引擎"""
        self.ocr = PaddleOCR(**OCR_CONFIG)

    def detect_certificate(self, image_path: str) -> Dict:
        """
        检测图像中的证件

        Args:
            image_path: 图像路径

        Returns:
            检测结果字典，包含：
            - has_certificate: 是否存在证件
            - certificate_type: 证件类型
            - confidence: 置信度
            - bbox: 证件边界框
            - ocr_result: OCR识别结果
        """
        result = {
            'has_certificate': False,
            'certificate_type': None,
            'confidence': 0.0,
            'bbox': None,
            'ocr_result': None,
            'ocr_text': ''
        }

        try:
            # 读取图像 - 使用numpy方式处理中文路径
            with open(image_path, 'rb') as f:
                image_data = np.frombuffer(f.read(), np.uint8)
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")

            # 执行OCR识别
            ocr_result = self.ocr.predict(image_path)
            result['ocr_result'] = ocr_result

            # 提取OCR文本
            ocr_text = self._extract_ocr_text(ocr_result)
            result['ocr_text'] = ocr_text

            # 检测证件是否存在
            has_certificate = self._detect_certificate_presence(image, ocr_text)
            result['has_certificate'] = has_certificate

            if has_certificate:
                # 识别证件类型
                cert_type, confidence = self._classify_certificate_type(ocr_text)
                result['certificate_type'] = cert_type
                result['confidence'] = confidence

                # 检测证件边界框
                bbox = self._detect_certificate_bbox(image, ocr_result)
                result['bbox'] = bbox

        except Exception as e:
            print(f"证件检测错误: {str(e)}")
            result['error'] = str(e)

        return result

    def _extract_ocr_text(self, ocr_result) -> str:
        """
        从OCR结果中提取文本

        Args:
            ocr_result: PaddleOCR返回的结果

        Returns:
            提取的文本字符串
        """
        text_lines = []

        try:
            # PaddleX OCRResult对象处理
            if isinstance(ocr_result, list) and len(ocr_result) > 0:
                first_item = ocr_result[0]

                # 检查是否是PaddleX的OCRResult对象
                if hasattr(first_item, 'json'):
                    # PaddleX的OCRResult对象有json方法
                    for result_obj in ocr_result:
                        result_json = result_obj.json
                        # 从json结果中提取文本
                        if isinstance(result_json, dict):
                            # PaddleX格式：{'res': {'rec_texts': [...], 'dt_polys': [...], ...}}
                            if 'res' in result_json:
                                res_dict = result_json['res']
                                if isinstance(res_dict, dict):
                                    if 'rec_texts' in res_dict:
                                        rec_texts = res_dict['rec_texts']
                                        if isinstance(rec_texts, list):
                                            text_lines.extend([str(t) for t in rec_texts])
                                    elif 'rec_text' in res_dict:
                                        rec_texts = res_dict['rec_text']
                                        if isinstance(rec_texts, list):
                                            text_lines.extend([str(t) for t in rec_texts])
                            # 直接格式：{'rec_texts': [...], 'dt_polys': [...], ...}
                            elif 'rec_texts' in result_json:
                                rec_texts = result_json['rec_texts']
                                if isinstance(rec_texts, list):
                                    text_lines.extend([str(t) for t in rec_texts])
                            elif 'rec_text' in result_json:
                                rec_texts = result_json['rec_text']
                                if isinstance(rec_texts, list):
                                    text_lines.extend([str(t) for t in rec_texts])
                            elif 'text' in result_json:
                                text_lines.append(str(result_json['text']))

                # 传统的嵌套列表格式
                elif isinstance(first_item, list) and len(first_item) > 0:
                    for page_result in ocr_result:
                        if isinstance(page_result, list):
                            for line_result in page_result:
                                if isinstance(line_result, list) and len(line_result) >= 2:
                                    text_info = line_result[1]
                                    if isinstance(text_info, (list, tuple)) and len(text_info) >= 1:
                                        text_lines.append(str(text_info[0]))

        except Exception as e:
            print(f"提取OCR文本错误: {str(e)}")
            import traceback
            traceback.print_exc()

        return '\n'.join(text_lines) if text_lines else ''

    def _detect_certificate_presence(self, image: np.ndarray, ocr_text: str) -> bool:
        """
        检测图像中是否存在证件

        Args:
            image: 输入图像
            ocr_text: OCR识别的文本

        Returns:
            是否存在证件
        """
        # 关键词检测
        keywords = [
            '证书', '证明', 'certificate', 'CERTIFICATE',
            '检疫', 'quarantine', 'QUARANTINE',
            '卫生', 'health', 'HEALTH',
            '植物', 'plant', 'PLANT', 'phytosanitary',
            '动物', 'animal', 'ANIMAL', 'veterinary',
            '食品', 'food', 'FOOD'
        ]

        # 检查是否包含关键词
        has_keywords = any(keyword in ocr_text for keyword in keywords)

        # 图像尺寸检测 - 证件通常有标准尺寸
        height, width = image.shape[:2]
        aspect_ratio = width / height
        reasonable_size = (width > 500 and height > 300)

        # 文本长度检查 - 证件通常有一定文本内容
        has_enough_text = len(ocr_text) > 50

        # 综合判断 - 只需要满足关键词和基本尺寸即可
        # 放宽检测条件，降低误判率
        return has_keywords or has_enough_text

    def _classify_certificate_type(self, ocr_text: str) -> Tuple[Optional[str], float]:
        """
        根据OCR文本分类证件类型

        Args:
            ocr_text: OCR识别的文本

        Returns:
            (证件类型, 置信度)
        """
        # 优先级最高：水产品证书（食品类）
        aquatic_keywords = ['水产', '水产品', 'aquatic', 'fishery', 'seafood', '渔业', '鱼类',
                           '虾', '蟹', '贝类', 'fish', 'shrimp', 'crab']
        aquatic_count = sum(1 for keyword in aquatic_keywords if keyword in ocr_text)

        # 如果包含水产品关键词，直接判定为食品证书
        if aquatic_count > 0:
            confidence = min(0.8, 0.3 + aquatic_count * 0.1)  # 基础0.3 + 每个关键词0.1
            return 'food', confidence

        # 动物证书关键词（移除"水产"）
        animal_keywords = ['动物', 'animal', '肉类', '燕窝', 'meat', 'poultry', '家禽',
                          '畜牧', 'livestock', '牛', '羊', '猪', 'cattle', 'sheep', 'pork']

        # 植物证书关键词
        plant_keywords = ['植物', '植检', 'plant', 'phytosanitary', '木材', '种子',
                         'timber', 'seed', '农产品', '粮食', 'grain']

        # 食品证书关键词（扩展）
        food_keywords = ['食品', '中药材', '坚果', '食用', 'food', 'edible', '卫生',
                        'sanitary', 'health', '健康', '营养']

        # 统计匹配的关键词数量
        animal_count = sum(1 for keyword in animal_keywords if keyword in ocr_text)
        plant_count = sum(1 for keyword in plant_keywords if keyword in ocr_text)
        food_count = sum(1 for keyword in food_keywords if keyword in ocr_text)

        # 计算置信度
        if animal_count > plant_count and animal_count > food_count:
            confidence = animal_count / len(animal_keywords)
            return 'animal', confidence
        elif plant_count > animal_count and plant_count > food_count:
            confidence = plant_count / len(plant_keywords)
            return 'plant', confidence
        elif food_count > 0:
            confidence = food_count / len(food_keywords)
            return 'food', confidence
        else:
            # 默认返回动物证书类型
            return 'animal', 0.3

    def _detect_certificate_bbox(self, image: np.ndarray, ocr_result) -> Optional[List[int]]:
        """
        检测证件的边界框

        Args:
            image: 输入图像
            ocr_result: OCR结果

        Returns:
            边界框 [x, y, width, height]
        """
        try:
            all_points = []

            # PaddleX OCRResult对象处理
            if isinstance(ocr_result, list) and len(ocr_result) > 0:
                first_item = ocr_result[0]

                # 检查是否是PaddleX的OCRResult对象
                if hasattr(first_item, 'json'):
                    for result_obj in ocr_result:
                        result_json = result_obj.json
                        if isinstance(result_json, dict):
                            # PaddleX格式：{'res': {'dt_polys': [...], ...}}
                            if 'res' in result_json:
                                res_dict = result_json['res']
                                if isinstance(res_dict, dict) and 'dt_polys' in res_dict:
                                    dt_polys = res_dict['dt_polys']
                                    if isinstance(dt_polys, list):
                                        for poly in dt_polys:
                                            if isinstance(poly, (list, np.ndarray)):
                                                all_points.extend(poly)
                            # 直接格式：{'dt_polys': [...], ...}
                            elif 'dt_polys' in result_json:
                                dt_polys = result_json['dt_polys']
                                if isinstance(dt_polys, list):
                                    for poly in dt_polys:
                                        if isinstance(poly, (list, np.ndarray)):
                                            all_points.extend(poly)

                # 传统列表格式
                elif isinstance(first_item, list):
                    for page_result in ocr_result:
                        if isinstance(page_result, list):
                            for line_result in page_result:
                                if isinstance(line_result, list) and len(line_result) >= 1:
                                    bbox = line_result[0]
                                    if isinstance(bbox, (list, np.ndarray)):
                                        all_points.extend(bbox)

            if not all_points:
                return None

            # 计算最小外接矩形
            points = np.array(all_points, dtype=np.float32)
            if points.shape[0] == 0 or points.shape[1] < 2:
                return None

            x_min = int(np.min(points[:, 0]))
            y_min = int(np.min(points[:, 1]))
            x_max = int(np.max(points[:, 0]))
            y_max = int(np.max(points[:, 1]))

            return [x_min, y_min, x_max - x_min, y_max - y_min]
        except Exception as e:
            print(f"检测边界框错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def extract_certificate_region(self, image_path: str, bbox: List[int], output_path: str) -> bool:
        """
        提取证件区域并保存

        Args:
            image_path: 原始图像路径
            bbox: 边界框 [x, y, width, height]
            output_path: 输出路径

        Returns:
            是否成功
        """
        try:
            # 读取图像 - 使用numpy方式处理中文路径
            with open(image_path, 'rb') as f:
                image_data = np.frombuffer(f.read(), np.uint8)
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

            if image is None:
                return False

            x, y, w, h = bbox
            certificate_region = image[y:y+h, x:x+w]

            # 保存图像 - 处理中文路径
            success, encoded_image = cv2.imencode('.jpg', certificate_region)
            if success:
                with open(output_path, 'wb') as f:
                    f.write(encoded_image.tobytes())
                return True
            return False
        except Exception as e:
            print(f"提取证件区域错误: {str(e)}")
            return False


if __name__ == '__main__':
    # 测试代码
    detector = CertificateDetector()

    # 测试图像 - 使用实际的证书图片
    test_images = [
        'books/植物证书/亚洲(东南亚国家涉及木材 重要)/老挝植物检疫证书.jpg',
    ]

    for test_image in test_images:
        if os.path.exists(test_image):
            print(f"正在检测: {test_image}")
            result = detector.detect_certificate(test_image)

            print("\n检测结果:")
            print(f"存在证件: {result['has_certificate']}")
            print(f"证件类型: {result['certificate_type']}")
            print(f"置信度: {result['confidence']:.2f}")
            print(f"边界框: {result['bbox']}")
            print(f"\nOCR文本(前500字符):\n{result['ocr_text'][:500]}...")
            print("\n" + "="*80 + "\n")
        else:
            print(f"测试图像不存在: {test_image}")
