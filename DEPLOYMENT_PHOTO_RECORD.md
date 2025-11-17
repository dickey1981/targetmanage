# 📷 拍照记录功能部署指南

## 📋 部署清单

### 新增文件

#### 后端文件
- ✅ `backend/app/api/photo_records.py` - 拍照记录API接口
- ✅ `backend/app/main.py` - 已更新（注册新路由）

#### 小程序文件
- ✅ `wechat-miniprogram/pages/index/index.js` - 已更新（拍照功能）
- ✅ `wechat-miniprogram/components/photo-result-modal/photo-result-modal.js`
- ✅ `wechat-miniprogram/components/photo-result-modal/photo-result-modal.wxml`
- ✅ `wechat-miniprogram/components/photo-result-modal/photo-result-modal.wxss`
- ✅ `wechat-miniprogram/components/photo-result-modal/photo-result-modal.json`

#### 配置文件
- ✅ `docker-compose.lighthouse.yml` - 已更新（添加OCR_DEV_MODE）

#### 文档文件
- ✅ `wechat-miniprogram/PHOTO_RECORD_FEATURE.md` - 功能说明文档
- ✅ `PHOTO_RECORD_IMPLEMENTATION_SUMMARY.md` - 实现总结
- ✅ `test_photo_record_api.py` - API测试脚本
- ✅ `DEPLOYMENT_PHOTO_RECORD.md` - 本文档

## 🚀 部署步骤

### 步骤1: 提交代码到Git

在本地开发环境（Windows）：

```bash
# 使用Git GUI或GitHub Desktop提交以下文件：

# 后端文件
backend/app/api/photo_records.py
backend/app/main.py

# 小程序文件
wechat-miniprogram/pages/index/index.js
wechat-miniprogram/components/photo-result-modal/*

# 配置文件
docker-compose.lighthouse.yml

# 文档和测试
wechat-miniprogram/PHOTO_RECORD_FEATURE.md
PHOTO_RECORD_IMPLEMENTATION_SUMMARY.md
test_photo_record_api.py
DEPLOYMENT_PHOTO_RECORD.md

# 提交信息
feat: 实现拍照记录功能

- 添加照片OCR识别API接口
- 实现智能内容分析
- 完善小程序拍照上传功能
- 创建识别结果展示组件
- 支持自动匹配目标和更新进度
- 添加开发模式支持
```

### 步骤2: 服务器端部署

SSH连接到服务器：

```bash
ssh root@106.54.212.67
```

进入项目目录并更新代码：

```bash
cd /opt/targetmanage

# 备份当前配置
cp docker-compose.lighthouse.yml docker-compose.lighthouse.yml.backup-$(date +%Y%m%d)

# 拉取最新代码
git pull origin main

# 查看更新的文件
git log --oneline -5
git diff HEAD~1 HEAD --name-only
```

### 步骤3: 配置环境变量

编辑 `.env` 文件：

```bash
nano .env
```

确认包含以下配置：

```bash
# 腾讯云配置
TENCENT_SECRET_ID=你的腾讯云SecretId
TENCENT_SECRET_KEY=你的腾讯云SecretKey

# 微信配置
WECHAT_APP_ID=你的微信小程序AppId
WECHAT_APP_SECRET=你的微信小程序AppSecret

# 开发模式配置
ASR_DEV_MODE=true   # 语音识别开发模式
OCR_DEV_MODE=true   # OCR识别开发模式（新增）

# 其他配置
SECRET_KEY=lighthouse-secret-key-20241016
COS_BUCKET_NAME=
```

保存并退出（Ctrl+X, Y, Enter）

### 步骤4: 重启后端服务

```bash
# 重启后端容器
docker-compose -f docker-compose.lighthouse.yml restart backend

# 等待服务启动
sleep 10

# 检查容器状态
docker-compose -f docker-compose.lighthouse.yml ps

# 查看启动日志
docker logs targetmanage_backend_lighthouse --tail 50
```

### 步骤5: 验证部署

#### 5.1 健康检查

```bash
curl http://106.54.212.67/health
```

预期输出：
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z",
  "service": "智能目标管理系统",
  "version": "1.0.0"
}
```

#### 5.2 测试API端点

```bash
# 测试照片识别端点（预期返回401或422，说明端点存在）
curl -X POST http://106.54.212.67/api/photo-records/recognize

# 测试照片记录创建端点
curl -X POST http://106.54.212.67/api/photo-records/recognize-and-create
```

#### 5.3 查看API文档

在浏览器中访问：
```
http://106.54.212.67/docs
```

查找新增的接口：
- `/api/photo-records/recognize`
- `/api/photo-records/create`
- `/api/photo-records/recognize-and-create`

### 步骤6: 小程序端测试

#### 6.1 微信开发者工具配置

1. 打开微信开发者工具
2. 打开项目：`wechat-miniprogram`
3. 点击右上角"详情"
4. 选择"本地设置"标签
5. ✅ 勾选"不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"
6. 点击"清缓存" → "清除全部缓存"
7. 点击"编译"按钮

#### 6.2 功能测试

1. **登录测试**
   - 点击"微信授权"按钮
   - 确认登录成功

2. **拍照记录测试**
   - 点击首页的"拍照记录"按钮
   - 选择"从相册选择"（开发者工具中）
   - 选择一张包含文字的图片
   - 观察控制台日志
   - 等待识别完成
   - 查看识别结果弹窗

3. **预期结果**
   ```
   📷 选择图片成功: wxfile://tmp_...
   📤 开始上传图片
   API URL: http://106.54.212.67/api/photo-records/recognize-and-create
   图片路径: wxfile://tmp_...
   📤 上传响应: {...}
   📤 解析后的数据: {success: true, ...}
   📸 照片识别结果:
   记录: {id: 123, content: "...", ...}
   分析: {record_type: "progress", ...}
   ```

4. **验证功能**
   - ✅ 图片上传成功
   - ✅ OCR识别成功（开发模式返回模拟数据）
   - ✅ 智能分析完成
   - ✅ 记录创建成功
   - ✅ 结果弹窗显示正常
   - ✅ 目标列表刷新

### 步骤7: 运行自动化测试

在本地或服务器上运行测试脚本：

```bash
# 确保已安装Python和依赖
pip install requests pillow

# 运行测试
python test_photo_record_api.py
```

预期输出：
```
============================================================
📷 拍照记录API测试
============================================================
...
============================================================
📊 测试总结
============================================================
✅ 通过 - API端点检查
✅ 通过 - 开发模式状态
✅ 通过 - 照片识别接口
✅ 通过 - 照片识别并创建记录

------------------------------------------------------------
总计: 4/4 通过
✅ 🎉 所有测试通过！拍照记录API工作正常
============================================================
```

## 🔍 故障排查

### 问题1: 后端启动失败

**检查日志**:
```bash
docker logs targetmanage_backend_lighthouse --tail 100
```

**常见原因**:
- 导入错误：检查 `photo_records.py` 是否正确
- 路由冲突：检查 `main.py` 中的路由注册
- 依赖缺失：检查 `requirements.txt`

**解决方法**:
```bash
# 重新构建镜像
docker-compose -f docker-compose.lighthouse.yml build backend

# 重启服务
docker-compose -f docker-compose.lighthouse.yml up -d backend
```

### 问题2: API返回404

**检查**:
1. 确认路由已注册
2. 查看API文档 `/docs`
3. 检查URL拼写

**解决**:
```bash
# 查看后端日志
docker logs targetmanage_backend_lighthouse | grep photo

# 重启后端
docker-compose -f docker-compose.lighthouse.yml restart backend
```

### 问题3: 小程序上传失败

**检查**:
1. 是否关闭域名校验
2. 网络是否正常
3. Token是否有效
4. API地址是否正确

**解决**:
```javascript
// 在控制台测试
console.log('baseUrl:', app.globalData.baseUrl)
console.log('token:', wx.getStorageSync('token'))
```

### 问题4: OCR识别失败

**开发模式**:
- 确认 `OCR_DEV_MODE=true`
- 开发模式会返回模拟数据

**生产模式**:
- 检查腾讯云OCR服务配置
- 确认 `TENCENT_SECRET_ID` 和 `TENCENT_SECRET_KEY`
- 查看后端日志

## 📊 监控和日志

### 实时日志监控

```bash
# 实时查看后端日志
docker logs -f targetmanage_backend_lighthouse

# 过滤照片相关日志
docker logs -f targetmanage_backend_lighthouse | grep -E "photo|OCR|照片"
```

### 关键日志标记

```
📷 - 照片相关操作
📤 - 上传操作
✅ - 成功操作
❌ - 失败操作
⚠️  - 警告信息
```

## ✅ 部署验证清单

部署完成后，请确认以下所有项：

### 后端验证
- [ ] 后端容器正常运行
- [ ] 健康检查接口正常
- [ ] API文档显示新接口
- [ ] 后端日志无错误

### 小程序验证
- [ ] 代码已更新
- [ ] 域名校验已关闭
- [ ] 登录功能正常
- [ ] 拍照按钮可见
- [ ] 图片选择正常
- [ ] 上传功能正常
- [ ] 识别结果显示
- [ ] 记录创建成功

### 功能验证
- [ ] OCR识别正常（开发模式）
- [ ] 智能分析准确
- [ ] 记录保存成功
- [ ] 目标进度更新
- [ ] 结果弹窗美观

## 📝 部署记录

请记录部署信息：

```
部署日期: _______________
部署人员: _______________
Git Commit: _______________
服务器IP: 106.54.212.67
部署版本: v1.0.0

测试结果:
□ 后端API测试通过
□ 小程序功能测试通过
□ 自动化测试通过

备注:
_________________________________
_________________________________
_________________________________
```

## 🎯 下一步

部署完成后：

1. **通知团队**
   - 新功能已上线
   - 使用说明文档位置
   - 测试方法

2. **收集反馈**
   - 用户体验反馈
   - 功能改进建议
   - Bug报告

3. **持续优化**
   - 监控性能指标
   - 优化识别准确度
   - 改进用户界面

## 📞 技术支持

如遇问题，请：

1. 查看本文档的故障排查部分
2. 查看 `PHOTO_RECORD_FEATURE.md` 的常见问题
3. 检查后端日志和控制台输出
4. 联系开发团队

---

**文档版本**: v1.0.0  
**最后更新**: 2025-01-01  
**维护人员**: 目标管理系统开发团队

