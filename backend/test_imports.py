#!/usr/bin/env python3
"""测试所有导入是否正常"""

print("测试导入...")

try:
    print("1. 测试 qcloud_cos...")
    from qcloud_cos import CosConfig, CosS3Client
    print("   ✅ qcloud_cos 导入成功")
except Exception as e:
    print(f"   ❌ qcloud_cos 导入失败: {e}")

try:
    print("2. 测试 tencentcloud...")
    from tencentcloud.common import credential
    from tencentcloud.asr.v20190614 import asr_client, models
    print("   ✅ tencentcloud 导入成功")
except Exception as e:
    print(f"   ❌ tencentcloud 导入失败: {e}")

try:
    print("3. 测试 app.config.tencent_cloud...")
    from app.config.tencent_cloud import tencent_cloud
    print("   ✅ tencent_cloud 导入成功")
except Exception as e:
    print(f"   ❌ tencent_cloud 导入失败: {e}")

try:
    print("4. 测试 app.services.tencent_ocr_service...")
    from app.services.tencent_ocr_service import ocr_service
    print("   ✅ ocr_service 导入成功")
except Exception as e:
    print(f"   ❌ ocr_service 导入失败: {e}")

try:
    print("5. 测试 app.api.photo_records...")
    from app.api import photo_records
    print("   ✅ photo_records 导入成功")
except Exception as e:
    print(f"   ❌ photo_records 导入失败: {e}")

try:
    print("6. 测试 app.main...")
    from app.main import app
    print("   ✅ app.main 导入成功")
    print("\n🎉 所有导入测试通过！")
except Exception as e:
    print(f"   ❌ app.main 导入失败: {e}")
    import traceback
    traceback.print_exc()

