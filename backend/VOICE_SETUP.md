# 🎤 语音目标创建功能配置说明

## 📋 功能概述

本系统已集成语音识别和目标创建功能，用户可以通过语音快速创建符合SMART原则的目标。

## 🔧 配置步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要新增依赖：
- `tencentcloud-sdk-python==3.0.1035` - 腾讯云SDK

### 2. 配置腾讯云ASR服务

#### 2.1 获取腾讯云凭证
1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 进入 [访问管理](https://console.cloud.tencent.com/cam) → API密钥管理
3. 创建新的SecretId和SecretKey

#### 2.2 配置环境变量
创建 `.env` 文件并添加以下配置：

```bash
# 腾讯云配置
TENCENT_SECRET_ID=your-secret-id-here
TENCENT_SECRET_KEY=your-secret-key-here
```

### 3. 启动服务

```bash
python start_dev.py
```

## 🚀 API端点

### 语音识别
- **POST** `/api/goals/recognize-voice`
  - 功能：上传音频文件进行语音识别
  - 参数：`audio` (音频文件)
  - 返回：识别结果文本

### 语音解析
- **POST** `/api/goals/parse-voice`
  - 功能：解析语音文本为目标数据
  - 参数：`{"voice_text": "语音文本"}`
  - 返回：解析后的目标数据 + 验证结果

### 语音创建目标
- **POST** `/api/goals/create-from-voice`
  - 功能：通过语音直接创建目标
  - 参数：`{"voice_text": "语音文本"}`
  - 返回：创建成功的目标信息

## 🧪 测试功能

运行测试脚本验证功能：

```bash
python test_voice_goal.py
```

测试用例包括：
- "我要在3个月内减重10斤"
- "半年内学会游泳"
- "这个季度要完成5个项目"
- "下个月开始学习Python编程"

## 🎯 支持的语音模式

### 时间表达式
- `3个月内` → 自动计算开始和结束时间
- `半年内` → 180天
- `下个月` → 下个月1号开始
- `下周` → 下周一开始

### 量化指标
- `减重10斤` → 目标值: 10, 单位: 斤
- `学习5本书` → 目标值: 5, 单位: 本书
- `完成3个项目` → 目标值: 3, 单位: 个项目

### 智能分类
- 健康：减重、运动、健身等
- 学习：学习、读书、技能等
- 工作：项目、任务、业绩等
- 生活：旅行、理财、兴趣等

## 🔍 验证规则

系统会自动验证目标是否符合SMART原则：

1. **Specific (具体)** - 目标描述是否清晰
2. **Measurable (可测量)** - 是否有明确的数值和单位
3. **Achievable (可实现)** - 目标是否合理可行
4. **Relevant (相关)** - 目标类别是否合适
5. **Time-bound (有时限)** - 是否有明确的时间范围

## 📱 前端集成

前端可以通过以下方式调用语音功能：

```javascript
// 1. 语音识别
const formData = new FormData()
formData.append('audio', audioFile)
const response = await fetch('/api/goals/recognize-voice', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
})

// 2. 语音解析
const parseResponse = await fetch('/api/goals/parse-voice', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ voice_text: '我要在3个月内减重10斤' })
})

// 3. 直接创建目标
const createResponse = await fetch('/api/goals/create-from-voice', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ voice_text: '我要在3个月内减重10斤' })
})
```

## ⚠️ 注意事项

1. **音频文件限制**：最大10MB，支持mp3、wav、m4a等格式
2. **识别准确率**：建议在安静环境下录音，语速适中
3. **网络要求**：需要稳定的网络连接访问腾讯云服务
4. **费用说明**：腾讯云ASR按调用次数收费，建议设置使用限制

## 🐛 故障排除

### 常见问题

1. **语音识别服务不可用**
   - 检查腾讯云凭证配置
   - 确认网络连接正常
   - 查看服务日志

2. **识别结果不准确**
   - 检查音频质量
   - 确认语音内容清晰
   - 尝试重新录音

3. **目标创建失败**
   - 检查语音文本是否符合规范
   - 查看验证错误信息
   - 按照建议调整目标设置

## 📞 技术支持

如遇到问题，请：
1. 查看后端日志输出
2. 运行测试脚本验证功能
3. 检查环境变量配置
4. 确认腾讯云服务状态
