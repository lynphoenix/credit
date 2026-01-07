"""
模块4: Web端服务系统
功能：提供Web API接口，整合前三个模块
"""
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import traceback
import json
from datetime import datetime

# 导入前面的模块
from module1_detection import CertificateDetector
from module2_extraction import CertificateExtractor
from module3_forgery import ForgeryDetectionSystem
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH


# 创建Flask应用
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
CORS(app)

# 确保上传文件夹存在
UPLOAD_FOLDER.mkdir(exist_ok=True)

# 初始化所有模块
detector = CertificateDetector()
extractor = CertificateExtractor()
forgery_system = ForgeryDetectionSystem()


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>海关证件识别与鉴伪系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .upload-section {
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 30px;
        }

        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 50px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }

        .upload-area:hover {
            background: #f8f9ff;
            border-color: #764ba2;
        }

        .upload-area.dragover {
            background: #f0f0ff;
            border-color: #764ba2;
        }

        .upload-icon {
            font-size: 4em;
            color: #667eea;
            margin-bottom: 20px;
        }

        input[type="file"] {
            display: none;
        }

        .upload-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            margin-top: 20px;
            transition: transform 0.2s;
        }

        .upload-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .upload-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .results-section {
            display: none;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        .result-card {
            background: #f8f9ff;
            border-left: 5px solid #667eea;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }

        .result-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        .field-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .field-item {
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .field-label {
            font-weight: bold;
            color: #666;
            margin-bottom: 5px;
        }

        .field-value {
            color: #333;
        }

        .risk-indicator {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.2em;
        }

        .risk-genuine {
            background: #4caf50;
            color: white;
        }

        .risk-suspicious {
            background: #ff9800;
            color: white;
        }

        .risk-forged {
            background: #f44336;
            color: white;
        }

        .score-bar {
            background: #e0e0e0;
            border-radius: 10px;
            height: 30px;
            margin-top: 10px;
            overflow: hidden;
            position: relative;
        }

        .score-fill {
            height: 100%;
            background: linear-gradient(90deg, #4caf50 0%, #ff9800 50%, #f44336 100%);
            transition: width 0.5s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }

        .error-message {
            background: #f44336;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛂 海关证件识别与鉴伪系统</h1>

        <div class="upload-section">
            <h2 style="margin-bottom: 20px; color: #667eea;">上传证件图片</h2>
            <div class="upload-area" id="uploadArea">
                <div class="upload-icon">📄</div>
                <p style="font-size: 1.2em; color: #666;">拖拽图片到这里，或点击选择文件</p>
                <p style="color: #999; margin-top: 10px;">支持格式: JPG, PNG, PDF</p>
                <input type="file" id="fileInput" accept="image/*,.pdf">
            </div>
            <div style="text-align: center;">
                <button class="upload-btn" id="uploadBtn" disabled>开始识别</button>
            </div>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 15px; color: #667eea;">正在处理中，请稍候...</p>
            </div>

            <div class="error-message" id="errorMessage"></div>
        </div>

        <div class="results-section" id="resultsSection">
            <h2 style="margin-bottom: 20px; color: #667eea;">识别结果</h2>

            <!-- 基本信息 -->
            <div class="result-card">
                <h3>📋 基本信息</h3>
                <div class="field-grid">
                    <div class="field-item">
                        <div class="field-label">证件类型</div>
                        <div class="field-value" id="certType">-</div>
                    </div>
                    <div class="field-item">
                        <div class="field-label">证书编号</div>
                        <div class="field-value" id="certNumber">-</div>
                    </div>
                    <div class="field-item">
                        <div class="field-label">签发机构</div>
                        <div class="field-value" id="issuer">-</div>
                    </div>
                    <div class="field-item">
                        <div class="field-label">签发日期</div>
                        <div class="field-value" id="issueDate">-</div>
                    </div>
                </div>
            </div>

            <!-- 货物信息 -->
            <div class="result-card">
                <h3>📦 货物信息</h3>
                <div class="field-grid">
                    <div class="field-item">
                        <div class="field-label">货物名称</div>
                        <div class="field-value" id="goodsName">-</div>
                    </div>
                    <div class="field-item">
                        <div class="field-label">货物数量</div>
                        <div class="field-value" id="goodsQuantity">-</div>
                    </div>
                    <div class="field-item">
                        <div class="field-label">产地</div>
                        <div class="field-value" id="origin">-</div>
                    </div>
                    <div class="field-item">
                        <div class="field-label">目的地</div>
                        <div class="field-value" id="destination">-</div>
                    </div>
                </div>
            </div>

            <!-- 鉴伪结果 -->
            <div class="result-card">
                <h3>🔍 鉴伪检测</h3>
                <div style="text-align: center; margin: 20px 0;">
                    <span class="risk-indicator" id="riskIndicator">-</span>
                </div>

                <div>
                    <strong>综合评分:</strong>
                    <div class="score-bar">
                        <div class="score-fill" id="scoreFill" style="width: 0%">0%</div>
                    </div>
                </div>

                <div style="margin-top: 20px;">
                    <div style="margin-bottom: 10px;">
                        <strong>图像分析 (权重40%):</strong> <span id="imageScore">-</span>
                        <div style="color: #666; margin-top: 5px;" id="imageAnalysis"></div>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong>文本分析 (权重35%):</strong> <span id="textScore">-</span>
                        <div style="color: #666; margin-top: 5px;" id="textAnalysis"></div>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong>结构分析 (权重25%):</strong> <span id="structureScore">-</span>
                        <div style="color: #666; margin-top: 5px;" id="structureAnalysis"></div>
                    </div>
                </div>

                <div style="margin-top: 20px; padding: 15px; background: #fff; border-radius: 5px;">
                    <strong>建议:</strong>
                    <p id="recommendation" style="margin-top: 10px; color: #333;">-</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const uploadBtn = document.getElementById('uploadBtn');
        const loading = document.getElementById('loading');
        const resultsSection = document.getElementById('resultsSection');
        const errorMessage = document.getElementById('errorMessage');

        let selectedFile = null;

        // 点击上传区域
        uploadArea.addEventListener('click', () => fileInput.click());

        // 文件选择
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                selectedFile = e.target.files[0];
                uploadArea.querySelector('p').textContent = '已选择: ' + selectedFile.name;
                uploadBtn.disabled = false;
            }
        });

        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            if (e.dataTransfer.files.length > 0) {
                selectedFile = e.dataTransfer.files[0];
                fileInput.files = e.dataTransfer.files;
                uploadArea.querySelector('p').textContent = '已选择: ' + selectedFile.name;
                uploadBtn.disabled = false;
            }
        });

        // 上传并处理
        uploadBtn.addEventListener('click', async () => {
            if (!selectedFile) return;

            const formData = new FormData();
            formData.append('file', selectedFile);

            loading.style.display = 'block';
            uploadBtn.disabled = true;
            resultsSection.style.display = 'none';
            errorMessage.style.display = 'none';

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    displayResults(data.result);
                } else {
                    showError(data.error || '处理失败');
                }
            } catch (error) {
                showError('网络错误: ' + error.message);
            } finally {
                loading.style.display = 'none';
                uploadBtn.disabled = false;
            }
        });

        function displayResults(result) {
            // 基本信息
            document.getElementById('certType').textContent = formatCertType(result.certificate_type);
            document.getElementById('certNumber').textContent = result.extracted_fields.certificate_number || '-';
            document.getElementById('issuer').textContent = result.extracted_fields.issuer || '-';
            document.getElementById('issueDate').textContent = result.extracted_fields.issue_date || '-';

            // 货物信息
            document.getElementById('goodsName').textContent = result.extracted_fields.goods_name || '-';
            document.getElementById('goodsQuantity').textContent = result.extracted_fields.goods_quantity || '-';
            document.getElementById('origin').textContent = result.extracted_fields.origin || '-';
            document.getElementById('destination').textContent = result.extracted_fields.destination || '-';

            // 鉴伪结果
            const riskIndicator = document.getElementById('riskIndicator');
            const forgeryScore = result.forgery_result.forgery_score;
            const forgeryRisk = result.forgery_result.forgery_risk;

            riskIndicator.textContent = formatRisk(forgeryRisk);
            riskIndicator.className = 'risk-indicator risk-' + forgeryRisk;

            const scorePercent = (forgeryScore * 100).toFixed(1);
            const scoreFill = document.getElementById('scoreFill');
            scoreFill.style.width = scorePercent + '%';
            scoreFill.textContent = scorePercent + '%';

            document.getElementById('imageScore').textContent = (result.forgery_result.image_score * 100).toFixed(1) + '%';
            document.getElementById('textScore').textContent = (result.forgery_result.text_score * 100).toFixed(1) + '%';
            document.getElementById('structureScore').textContent = (result.forgery_result.structure_score * 100).toFixed(1) + '%';

            document.getElementById('imageAnalysis').textContent = result.forgery_result.image_analysis || '正常';
            document.getElementById('textAnalysis').textContent = result.forgery_result.text_analysis || '正常';
            document.getElementById('structureAnalysis').textContent = result.forgery_result.structure_analysis || '正常';

            document.getElementById('recommendation').textContent = result.forgery_result.recommendation;

            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }

        function formatCertType(type) {
            const types = {
                'plant': '植物证书',
                'animal': '动物证书',
                'food': '食品证书'
            };
            return types[type] || type;
        }

        function formatRisk(risk) {
            const risks = {
                'genuine': '真实',
                'suspicious': '疑似',
                'forged': '伪造'
            };
            return risks[risk] || risk;
        }

        function showError(message) {
            errorMessage.textContent = '错误: ' + message;
            errorMessage.style.display = 'block';
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/analyze', methods=['POST'])
def analyze_certificate():
    """
    分析证件接口

    输入: 上传的图片文件
    输出: JSON格式的分析结果
    """
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件上传'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'})

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件类型'})

        # 保存文件 - 处理中文文件名
        original_filename = file.filename
        # 提取文件扩展名（从原始文件名）
        name, ext = os.path.splitext(original_filename)
        # 如果没有扩展名，拒绝
        if not ext:
            return jsonify({'success': False, 'error': '文件必须有扩展名'})
        # 生成安全的文件名：时间戳 + 扩展名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')  # 加微秒避免冲突
        filename = f"{timestamp}{ext.lower()}"  # 使用小写扩展名
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))

        # 步骤1: 检测证件
        detection_result = detector.detect_certificate(str(filepath))

        if not detection_result['has_certificate']:
            return jsonify({
                'success': False,
                'error': '未检测到证件，请确认上传的是证件图片'
            })

        # 步骤2: 提取结构化信息
        extraction_result = extractor.extract(
            detection_result['ocr_text'],
            detection_result['certificate_type']
        )

        # 步骤3: 鉴伪检测
        forgery_result = forgery_system.detect(
            str(filepath),
            detection_result['ocr_result'],
            detection_result['ocr_text'],
            extraction_result['extracted_fields'],
            detection_result['certificate_type'],
            detection_result['bbox']
        )

        # 返回结果
        result = {
            'certificate_type': detection_result['certificate_type'],
            'confidence': detection_result['confidence'],
            'extracted_fields': extraction_result['extracted_fields'],
            'forgery_result': {
                'forgery_score': forgery_result['forgery_score'],
                'forgery_risk': forgery_result['forgery_risk'],
                'image_score': forgery_result['image_score'],
                'text_score': forgery_result['text_score'],
                'structure_score': forgery_result['structure_score'],
                'image_analysis': forgery_result['image_analysis'],
                'text_analysis': forgery_result['text_analysis'],
                'structure_analysis': forgery_result['structure_analysis'],
                'recommendation': forgery_result['recommendation']
            }
        }

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'处理错误: {str(e)}'
        })


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("="*80)
    print("海关证件识别与鉴伪系统")
    print("="*80)
    print(f"服务启动中...")
    print(f"访问地址: http://localhost:5000")
    print(f"上传文件夹: {UPLOAD_FOLDER}")
    print("="*80)

    app.run(host='0.0.0.0', port=5000, debug=True)
