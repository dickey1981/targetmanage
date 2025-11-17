# 腾讯云OCR服务开通指南

## 📋 目录
1. [服务开通](#1-服务开通)
2. [验证服务](#2-验证服务)
3. [配置启用](#3-配置启用)
4. [测试OCR](#4-测试ocr)
5. [费用说明](#5-费用说明)

---

## 1. 服务开通

### 步骤1：登录腾讯云控制台
访问：https://console.cloud.tencent.com/

### 步骤2：进入OCR服务
- 方式1：在控制台顶部搜索框输入 **"OCR"** 或 **"文字识别"**
- 方式2：直接访问 https://console.cloud.tencent.com/ocr/overview

### 步骤3：开通服务
1. 点击 **"立即开通"** 按钮
2. 阅读并同意《文字识别服务等级协议》
3. 选择计费方式（推荐按量付费）
4. 点击确认开通

### 步骤4：查看服务状态
开通后在控制台可以看到：
- ✅ 服务状态：已开通
- 📊 本月用量统计
- 💰 账单明细

---

## 2. 验证服务

### 在线体验
访问：https://console.cloud.tencent.com/ocr/general

可以在线上传图片测试OCR识别效果

### 检查API密钥
确认已配置腾讯云API密钥（与ASR语音识别共用）：
- `TENCENT_SECRET_ID`
- `TENCENT_SECRET_KEY`

---

## 3. 配置启用

### 方式1：本地开发环境

修改 `backend/app/config/settings.py`：

```python
# OCR识别开发模式配置
OCR_DEV_MODE: bool = False  # 改为False启用真实OCR
```

**重启后端服务**：
```bash
cd backend
python start_dev.py
```

### 方式2：服务器生产环境

#### 步骤1：修改环境变量文件
在服务器上编辑 `/opt/targetmanage/.env`：

```bash
# 修改OCR开发模式配置
OCR_DEV_MODE=false
```

#### 步骤2：确认docker-compose配置
`docker-compose.lighthouse.yml` 中应该有：

```yaml
environment:
  - OCR_DEV_MODE=${OCR_DEV_MODE:-false}
```

#### 步骤3：重启服务
```bash
cd /opt/targetmanage
docker-compose -f docker-compose.lighthouse.yml restart backend
```

#### 步骤4：验证配置
```bash
# 查看后端日志
docker-compose -f docker-compose.lighthouse.yml logs backend -f
```

应该能看到服务正常启动，没有"OCR服务未配置"的警告。

---

## 4. 测试OCR

### 本地测试脚本

创建测试文件 `backend/test_ocr_real.py`：

```python
"""测试真实OCR识别"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import base64
from app.services.tencent_ocr_service import ocr_service

async def test_ocr():
    # 测试文本（base64编码的图片）
    test_image_path = "test_image.jpg"  # 替换为你的测试图片路径
    
    if not os.path.exists(test_image_path):
        print("❌ 测试图片不存在，请准备一张包含文字的图片")
        return
    
    # 读取并编码图片
    with open(test_image_path, 'rb') as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    print("🔍 开始OCR识别...")
    
    # 调用OCR服务
    results = await ocr_service.general_basic_ocr(image_base64)
    
    if results:
        print(f"✅ 识别成功！识别到 {len(results)} 个文本块：\n")
        for i, block in enumerate(results, 1):
            print(f"{i}. {block['text']} (置信度: {block['confidence']:.2f})")
    else:
        print("❌ 识别失败")

if __name__ == "__main__":
    asyncio.run(test_ocr())
```

运行测试：
```bash
python test_ocr_real.py
```

### 小程序测试

1. **确保后端已启用真实OCR**（`OCR_DEV_MODE=False`）
2. **在小程序中点击拍照按钮**
3. **选择或拍摄一张包含文字的图片**
4. **查看识别结果**

---

## 5. 费用说明

### 免费额度（每月）
- **通用印刷体识别**：1,000 次/月
- **通用印刷体识别（高精度版）**：1,000 次/月
- **手写体识别**：1,000 次/月

### 按量计费（超出免费额度后）

| 接口名称 | 0-1万次 | 1万-10万次 | 10万-100万次 | >100万次 |
|---------|---------|-----------|-------------|----------|
| 通用印刷体识别 | 0.15元/次 | 0.10元/次 | 0.06元/次 | 0.03元/次 |
| 通用印刷体识别（高精度版）| 0.50元/次 | 0.35元/次 | 0.20元/次 | 0.15元/次 |
| 手写体识别 | 0.15元/次 | 0.10元/次 | 0.06元/次 | 0.03元/次 |

### 费用优化建议

1. **优先使用免费额度**
   - 每月1000次免费调用足够小规模使用
   
2. **选择合适的接口**
   - 普通场景：使用**通用印刷体识别**（便宜）
   - 要求高精度：使用**通用印刷体识别（高精度版）**
   - 手写内容：使用**手写体识别**

3. **设置费用告警**
   - 在腾讯云控制台设置费用告警
   - 推荐设置：每月超过10元时发送通知

4. **监控使用量**
   - 定期查看OCR控制台的用量统计
   - 关注异常调用

---

## 📝 常见问题

### Q1: 开通后提示"服务未开通"？
**A**: 检查以下几点：
1. 确认在OCR控制台显示"已开通"
2. 确认API密钥配置正确
3. 确认 `OCR_DEV_MODE=false`
4. 重启后端服务

### Q2: 识别失败或超时？
**A**: 可能的原因：
1. 网络连接问题（检查服务器是否能访问腾讯云API）
2. 图片过大（建议压缩到5MB以内）
3. 图片格式不支持（支持JPG、PNG、BMP）
4. API配额用完（查看控制台用量）

### Q3: 识别准确率低？
**A**: 优化建议：
1. 使用高精度版接口（`general_accurate_ocr`）
2. 确保图片清晰、光线充足
3. 文字大小适中、对比度高
4. 避免倾斜、扭曲的文字

### Q4: 如何临时切换到开发模式？
**A**: 
```bash
# 本地：修改 settings.py
OCR_DEV_MODE: bool = True

# 服务器：修改 .env 文件
OCR_DEV_MODE=true

# 重启服务后生效
```

---

## 🔗 相关链接

- [腾讯云OCR产品文档](https://cloud.tencent.com/document/product/866)
- [OCR控制台](https://console.cloud.tencent.com/ocr/overview)
- [API文档](https://cloud.tencent.com/document/product/866/33515)
- [价格说明](https://cloud.tencent.com/document/product/866/17619)
- [最佳实践](https://cloud.tencent.com/document/product/866/45583)

---

## 📞 技术支持

如有问题，请联系：
- 腾讯云工单系统
- 技术支持热线：95716

---

**更新时间**: 2025-11-06

