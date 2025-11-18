# 📱 微信小程序部署检查清单

## ✅ 代码检查

### API 请求检查
所有页面的 API 请求都已使用 `app.globalData.baseUrl`：

- ✅ **pages/index/index.js** - 首页
  - 登录验证
  - 今日目标加载
  - 语音识别
  - 拍照记录

- ✅ **pages/goals/goals.js** - 目标管理
  - 目标列表加载
  - 语音创建目标
  - 目标更新
  - 目标删除

- ✅ **pages/goal-detail/goal-detail.js** - 目标详情
  - 目标详情加载
  - 进度更新
  - 记录添加
  - 数据分析

- ✅ **pages/create-goal/create-goal.js** - 创建目标
  - 语音解析
  - 目标创建

- ✅ **pages/record/record.js** - 过程记录
  - 记录列表
  - 语音记录
  - 拍照记录
  - 文字记录

- ✅ **pages/record-detail/record-detail.js** - 记录详情
  - 记录详情加载
  - 目标列表
  - 记录删除

- ✅ **pages/process-record/process-record.js** - 记录处理
  - 记录加载
  - 语音识别
  - 目标建议
  - 记录保存

- ✅ **pages/timeline/timeline.js** - 时间线
  - 时间线数据
  - 统计数据

- ✅ **pages/profile/profile.js** - 个人中心
  - 用户统计
  - 通知设置
  - 数据同步

- ✅ **pages/login/login.js** - 登录
  - 手机号解密

### 环境配置检查

```javascript
// config/env.js
✅ development.baseUrl = 'http://localhost:8000'  // 开发者工具
✅ production.baseUrl = 'https://targetmanage.cn' // 真机环境
✅ 自动环境切换逻辑正确
```

## 🔧 部署步骤

### 1. 拉取最新代码
```bash
# 在你的开发机器上
cd /path/to/targetmanage
git pull origin main
```

### 2. 微信开发者工具
1. 打开微信开发者工具
2. 选择 `wechat-miniprogram` 目录
3. 点击"编译"按钮
4. 检查控制台是否有错误

### 3. 真机调试
1. 点击"真机调试"按钮
2. 扫码在手机上打开
3. 测试以下功能：
   - [ ] 登录功能
   - [ ] 创建目标
   - [ ] 语音识别
   - [ ] 拍照记录
   - [ ] 查看时间线

### 4. 上传代码
1. 点击"上传"按钮
2. 填写版本号和备注
3. 提交审核

## 🧪 测试清单

### 基础功能测试
- [ ] **登录**
  - [ ] 微信授权登录
  - [ ] Token 存储和验证
  
- [ ] **目标管理**
  - [ ] 查看目标列表
  - [ ] 创建新目标
  - [ ] 编辑目标
  - [ ] 删除目标
  - [ ] 更新进度

- [ ] **语音功能**
  - [ ] 语音创建目标
  - [ ] 语音记录
  - [ ] 识别结果准确性（真实识别，非模拟数据）

- [ ] **拍照功能**
  - [ ] 拍照识别
  - [ ] OCR 文字提取
  - [ ] 自动关联目标

- [ ] **记录管理**
  - [ ] 查看记录列表
  - [ ] 创建文字记录
  - [ ] 查看记录详情
  - [ ] 删除记录

- [ ] **时间线**
  - [ ] 查看所有记录
  - [ ] 按类型筛选
  - [ ] 按时间筛选
  - [ ] 查看统计数据

### 网络测试
- [ ] **HTTPS 连接**
  - [ ] 所有 API 请求使用 HTTPS
  - [ ] SSL 证书验证通过
  - [ ] 无混合内容警告

- [ ] **错误处理**
  - [ ] 网络错误提示
  - [ ] 超时处理
  - [ ] 服务器错误提示

### 性能测试
- [ ] **加载速度**
  - [ ] 首页加载 < 2秒
  - [ ] 目标列表加载 < 1秒
  - [ ] 语音识别响应 < 5秒

- [ ] **流畅度**
  - [ ] 页面切换流畅
  - [ ] 滚动流畅
  - [ ] 无卡顿

## 🐛 常见问题排查

### 问题1: 连接被拒绝 (ERR_CONNECTION_REFUSED)
**原因**: 小程序使用了 localhost 地址
**解决**: 
1. 检查 `app.globalData.baseUrl` 是否正确
2. 确认环境切换逻辑是否正常
3. 查看控制台输出的 baseUrl

### 问题2: 语音识别返回模拟数据
**原因**: 后端 `ASR_DEV_MODE` 未正确设置
**解决**:
```bash
# 在服务器上检查
docker exec targetmanage_backend_lighthouse env | grep ASR_DEV_MODE
# 应该输出: ASR_DEV_MODE=false
```

### 问题3: SSL 证书错误
**原因**: 微信小程序要求 HTTPS
**解决**:
1. 确认域名已备案
2. 确认 SSL 证书已配置
3. 在小程序后台配置合法域名

### 问题4: 请求超时
**原因**: 服务器响应慢或网络问题
**解决**:
1. 检查服务器负载
2. 查看后端日志
3. 增加请求超时时间

## 📊 监控指标

### 服务器监控
```bash
# 查看容器状态
docker-compose -f docker-compose.lighthouse.yml ps

# 查看资源使用
docker stats

# 查看日志
docker-compose -f docker-compose.lighthouse.yml logs -f backend
```

### 关键指标
- [ ] CPU 使用率 < 80%
- [ ] 内存使用率 < 80%
- [ ] 磁盘使用率 < 80%
- [ ] API 响应时间 < 1秒
- [ ] 错误率 < 1%

## 🔄 回滚方案

如果部署后发现问题，可以快速回滚：

```bash
# 在服务器上
cd /opt/targetmanage

# 回滚到上一个版本
git log --oneline -5  # 查看最近的提交
git reset --hard <commit-hash>  # 回滚到指定版本

# 重新构建
docker-compose -f docker-compose.lighthouse.yml down
docker-compose -f docker-compose.lighthouse.yml up -d --build
```

## ✅ 部署完成确认

部署完成后，确认以下所有项目都已完成：

- [ ] 代码已拉取到最新版本
- [ ] 微信开发者工具编译无错误
- [ ] 真机调试功能正常
- [ ] 所有测试用例通过
- [ ] 服务器监控正常
- [ ] 日志无异常错误
- [ ] 已通知相关人员

---

**检查人**: _____________  
**检查日期**: _____________  
**部署版本**: _____________  
**备注**: _____________

