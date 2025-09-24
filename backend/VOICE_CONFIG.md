# 语音功能配置说明

## 🎤 语音识别服务配置

### 腾讯云ASR服务配置

1. **获取腾讯云凭证**
   - 访问 [腾讯云控制台](https://console.cloud.tencent.com/)
   - 创建或使用现有账号
   - 在 [访问管理](https://console.cloud.tencent.com/cam) 中创建API密钥

2. **配置环境变量**
   在 `backend/.env` 文件中添加以下配置：
   ```bash
   # 腾讯云语音识别服务配置
   TENCENT_SECRET_ID=your_secret_id_here
   TENCENT_SECRET_KEY=your_secret_key_here
   ```

3. **开通语音识别服务**
   - 访问 [腾讯云ASR](https://console.cloud.tencent.com/asr)
   - 开通实时语音识别服务
   - 选择适合的计费方式

## 🔧 功能特性

### 支持的语音指令类型

#### 目标创建类
```
"我要在3个月内减重10斤"
"半年内学会游泳"
"这个季度要完成5个项目"
"下个月开始学习Python编程"
```

#### 进度更新类
```
"今天跑了5公里，用时30分钟"
"这周读完了一本书"
"项目完成了80%"
"今天体重70.5公斤"
```

#### 过程记录类
```
"今天感觉比上周轻松多了"
"发现早上跑步效果更好"
"遇到困难需要调整计划"
"今天学习效率很高"
```

### 语音处理流程

1. **录音** → 微信小程序录音API
2. **上传** → 上传到后端服务器
3. **识别** → 腾讯云ASR语音转文字
4. **解析** → NLP解析为结构化数据
5. **验证** → SMART目标验证
6. **创建** → 保存到数据库

## 📱 前端集成

### 微信小程序录音配置

在 `app.json` 中确保已配置录音权限：
```json
{
  "permission": {
    "scope.record": {
      "desc": "用于语音创建目标"
    }
  }
}
```

### 录音参数配置

```javascript
// 录音配置
recorderManager.start({
  duration: 60000, // 最长60秒
  sampleRate: 16000, // 16k采样率
  numberOfChannels: 1, // 单声道
  encodeBitRate: 96000, // 编码码率
  format: 'mp3' // 格式
})
```

## 🧪 测试验证

### 运行测试脚本

```bash
# 测试语音功能
python test_voice_goal_creation.py

# 完整集成测试
python test_voice_integration.py
```

### 测试用例

1. **基础语音解析测试**
   - 输入: "我要在3个月内减重10斤"
   - 预期: 解析出健康类别、10斤目标、3个月时间

2. **复杂语音解析测试**
   - 输入: "这个季度要完成5个项目，包括前端和后端开发"
   - 预期: 解析出工作类别、5个项目目标

3. **时间表达式测试**
   - 输入: "下个月开始学习Python编程"
   - 预期: 解析出学习类别、下个月时间范围

## 🔍 故障排除

### 常见问题

1. **语音识别失败**
   - 检查腾讯云凭证配置
   - 确认ASR服务已开通
   - 检查网络连接

2. **解析结果不准确**
   - 检查语音质量
   - 确认语音内容清晰
   - 查看解析器日志

3. **目标验证失败**
   - 检查目标数据完整性
   - 确认时间设置合理
   - 查看验证规则

### 调试方法

1. **查看日志**
   ```bash
   # 查看后端日志
   tail -f logs/app.log
   ```

2. **测试API端点**
   ```bash
   # 测试语音解析API
   curl -X POST http://localhost:8000/api/goals/parse-voice \
     -H "Content-Type: application/json" \
     -d '{"voice_text": "我要在3个月内减重10斤"}'
   ```

3. **检查服务状态**
   ```bash
   # 检查语音识别服务
   python -c "from app.services.voice_recognition import voice_recognition_service; print(voice_recognition_service.is_available())"
   ```

## 📈 性能优化

### 优化建议

1. **录音质量**
   - 使用16k采样率
   - 单声道录音
   - 控制录音时长

2. **网络优化**
   - 压缩音频文件
   - 使用CDN加速
   - 优化上传策略

3. **解析优化**
   - 缓存常用解析结果
   - 优化正则表达式
   - 并行处理多个请求

## 🔒 安全考虑

1. **数据隐私**
   - 音频文件临时存储
   - 识别后立即删除
   - 加密传输

2. **访问控制**
   - 用户身份验证
   - API访问限制
   - 敏感信息过滤

3. **错误处理**
   - 优雅降级
   - 错误日志记录
   - 用户友好提示

## 📚 相关文档

- [腾讯云ASR文档](https://cloud.tencent.com/document/product/1093)
- [微信小程序录音API](https://developers.weixin.qq.com/miniprogram/dev/api/media/recorder/RecorderManager.html)
- [FastAPI文件上传](https://fastapi.tiangolo.com/tutorial/request-files/)
