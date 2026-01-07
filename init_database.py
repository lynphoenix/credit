"""
数据库初始化和管理脚本
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database.models import init_database, Base, Certificate, CertificateTemplate
from config import DATABASE_CONFIG
from sqlalchemy import text


def create_tables():
    """创建数据库表"""
    print("="*80)
    print("数据库表初始化")
    print("="*80)

    print("\n数据库配置:")
    print(f"  主机: {DATABASE_CONFIG['host']}")
    print(f"  端口: {DATABASE_CONFIG['port']}")
    print(f"  用户: {DATABASE_CONFIG['user']}")
    print(f"  数据库: {DATABASE_CONFIG['database']}")

    try:
        # 初始化数据库
        Session = init_database(DATABASE_CONFIG)
        print("\n✓ 数据库连接成功")
        print("✓ 数据表创建成功")

        # 测试连接
        session = Session()
        result = session.execute(text("SELECT 1"))
        print("✓ 数据库连接测试通过")
        session.close()

        print("\n已创建的表:")
        print("  - certificates (证书信息表)")
        print("  - certificate_templates (证书模板表)")

        return True

    except Exception as e:
        print(f"\n✗ 数据库初始化失败: {str(e)}")
        print("\n请检查:")
        print("  1. MySQL服务是否已启动")
        print("  2. 数据库配置是否正确（config.py）")
        print("  3. 数据库用户是否有创建表的权限")
        print("  4. 数据库是否已存在（需要手动创建数据库）")

        print("\n创建数据库的SQL命令:")
        print(f"  CREATE DATABASE IF NOT EXISTS {DATABASE_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")

        return False


def test_database_operations():
    """测试数据库操作"""
    print("\n" + "="*80)
    print("数据库操作测试")
    print("="*80)

    try:
        Session = init_database(DATABASE_CONFIG)
        session = Session()

        # 测试插入
        print("\n测试插入数据...")
        from database.models import CertificateType, ForgeryRisk

        test_cert = Certificate(
            certificate_type=CertificateType.PLANT,
            certificate_number="TEST-2024-001",
            country="China",
            region="Asia",
            issuer="Test Ministry",
            goods_name="Test Goods",
            origin="Test Origin",
            destination="Test Destination",
            ocr_text="Test OCR Text",
            forgery_score=0.3,
            forgery_risk=ForgeryRisk.GENUINE,
            image_score=0.2,
            text_score=0.3,
            structure_score=0.4
        )

        session.add(test_cert)
        session.commit()
        print("✓ 插入测试数据成功")

        # 测试查询
        print("\n测试查询数据...")
        cert = session.query(Certificate).filter_by(certificate_number="TEST-2024-001").first()
        if cert:
            print("✓ 查询测试数据成功")
            print(f"  ID: {cert.id}")
            print(f"  证书编号: {cert.certificate_number}")
            print(f"  证书类型: {cert.certificate_type.value}")
            print(f"  伪造风险: {cert.forgery_risk.value}")

        # 清理测试数据
        print("\n清理测试数据...")
        session.delete(cert)
        session.commit()
        print("✓ 清理测试数据成功")

        session.close()

        print("\n✓ 所有数据库操作测试通过")
        return True

    except Exception as e:
        print(f"\n✗ 数据库操作测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def show_database_info():
    """显示数据库信息"""
    print("\n" + "="*80)
    print("数据库表结构")
    print("="*80)

    print("\n表1: certificates (证书信息表)")
    print("-"*80)
    print("字段说明:")
    print("  id                   - 主键ID")
    print("  certificate_type     - 证书类型（动物/植物/食品）")
    print("  certificate_number   - 证书编号")
    print("  country              - 国家")
    print("  region               - 地区")
    print("  category             - 类别")
    print("  ocr_text             - OCR识别文本")
    print("  issuer               - 签发机构")
    print("  issue_date           - 签发日期")
    print("  valid_date           - 有效日期")
    print("  applicant            - 申请人")
    print("  goods_name           - 货物名称")
    print("  goods_quantity       - 货物数量")
    print("  origin               - 产地")
    print("  destination          - 目的地")
    print("  additional_info      - 其他信息(JSON)")
    print("  forgery_score        - 伪造风险评分(0-1)")
    print("  forgery_risk         - 伪造风险等级（真/疑似/伪造）")
    print("  image_score          - 图像层面评分")
    print("  text_score           - 文本层面评分")
    print("  structure_score      - 结构层面评分")
    print("  image_analysis       - 图像分析结果")
    print("  text_analysis        - 文本分析结果")
    print("  structure_analysis   - 结构分析结果")
    print("  image_path           - 图像文件路径")
    print("  created_at           - 创建时间")
    print("  updated_at           - 更新时间")

    print("\n表2: certificate_templates (证书模板表)")
    print("-"*80)
    print("字段说明:")
    print("  id                     - 主键ID")
    print("  certificate_type       - 证书类型")
    print("  country                - 国家")
    print("  category               - 类别")
    print("  template_image_path    - 模板图像路径")
    print("  layout_features        - 布局特征(JSON)")
    print("  font_features          - 字体特征(JSON)")
    print("  watermark_features     - 水印特征(JSON)")
    print("  required_fields        - 必需字段列表(JSON)")
    print("  created_at             - 创建时间")
    print("  updated_at             - 更新时间")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='数据库管理工具')
    parser.add_argument('--action',
                        choices=['create', 'test', 'info', 'all'],
                        default='all',
                        help='操作: create(创建表), test(测试), info(显示信息), all(全部)')

    args = parser.parse_args()

    if args.action == 'create' or args.action == 'all':
        success = create_tables()
        if not success:
            print("\n提示: 如果数据库不存在，请先手动创建数据库")
            sys.exit(1)

    if args.action == 'info' or args.action == 'all':
        show_database_info()

    if args.action == 'test':
        if not test_database_operations():
            sys.exit(1)

    print("\n" + "="*80)
    print("✓ 数据库配置完成")
    print("="*80)
