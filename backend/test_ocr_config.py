#!/usr/bin/env python3
"""测试OCR配置"""

import os

print("=" * 60)
print("环境变量检查")
print("=" * 60)

# 检查环境变量
ocr_dev_mode = os.getenv('OCR_DEV_MODE', 'not_set')
asr_dev_mode = os.getenv('ASR_DEV_MODE', 'not_set')
debug = os.getenv('DEBUG', 'not_set')

print(f"OCR_DEV_MODE: {ocr_dev_mode}")
print(f"ASR_DEV_MODE: {asr_dev_mode}")
print(f"DEBUG: {debug}")

print("\n" + "=" * 60)
print("开发模式检查")
print("=" * 60)

is_ocr_dev = os.getenv('OCR_DEV_MODE', 'false').lower() == 'true'
print(f"OCR开发模式启用: {is_ocr_dev}")

if is_ocr_dev:
    print("✅ 将使用模拟OCR数据")
else:
    print("❌ 将尝试使用真实OCR服务")

print("\n" + "=" * 60)
print("导入OCR服务测试")
print("=" * 60)

try:
    from app.services.tencent_ocr_service import ocr_service
    print(f"OCR服务client状态: {ocr_service.client is not None}")
except Exception as e:
    print(f"导入OCR服务失败: {e}")

