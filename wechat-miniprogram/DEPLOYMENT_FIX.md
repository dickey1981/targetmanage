# 微信小程序部署问题修复指南

## 🐛 遇到的问题

1. **网络错误**：点击微信授权登录提示"网络错误，请重试"
2. **手机号授权不支持**：提示"当前环境不支持手机号授权，请在微信中打开"

## ✅ 已完成的修复

### 1. 修改API地址配置

**文件**: `wechat-miniprogram/config/env.js`

**修改内容**:
```javascript
// 生产环境
production: {
  baseUrl: 'http://106.54.212.67:8000',  // 改为实际服务器地址
  apiVersion: 'v1',
  debug: false
}
```

### 2. 优化授权方式

**文件**: `wechat-miniprogram/pages/index/index.wxml`

**修改内容**:
- 将微信授权登录设为主要方案
- 移除手机号授权强制要求
- 优化授权提示文案

**文件**: `wechat-miniprogram/pages/index/index.js`

**修改内容**:
- 增强用户信息授权的错误处理
- 添加详细的调试日志
- 优化授权失败的用户提示

## 📱 微信小程序平台配置

### ⚠️ 重要：配置服务器域名

在微信小程序后台需要配置以下内容：

1. **登录微信小程序后台**: https://mp.weixin.qq.com/

2. **进入"开发" > "开发管理" > "开发设置"**

3. **配置"服务器域名"**:
   - **request合法域名**: `http://106.54.212.67`
   - **socket合法域名**: 无需配置
   - **uploadFile合法域名**: `http://106.54.212.67`
   - **downloadFile合法域名**: `http://106.54.212.67`

### ⚠️ HTTP域名说明

由于当前使用的是HTTP而非HTTPS，需要在微信开发者工具中进行以下设置：

1. **开发者工具设置**:
   - 点击右上角"详情"
   - 勾选"不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"
   - ⚠️ 注意：这个选项仅在开发和体验版中生效

2. **体验版测试**:
   - 开发者和体验成员可以在体验版中使用HTTP域名
   - 但正式版发布前必须配置HTTPS

### 🔐 后续需要配置HTTPS

为了正式发布，需要：

1. **申请域名**
   - 购买域名（如 `targetmanage.cn`）
   - 将域名解析到服务器IP: `106.54.212.67`

2. **申请SSL证书**
   - 可使用Let's Encrypt免费证书
   - 或购买商业SSL证书

3. **配置Nginx HTTPS**
   ```nginx
   server {
       listen 443 ssl;
       server_name targetmanage.cn;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:8000;
       }
   }
   ```

## 🧪 测试步骤

### 1. 开发环境测试

在微信开发者工具中：

1. 打开项目
2. 勾选"不校验合法域名"
3. 编译运行
4. 测试登录功能

**预期结果**:
- ✅ 点击"微信授权登录"弹出授权弹窗
- ✅ 授权后可以成功登录
- ✅ 可以正常使用语音功能和目标管理

### 2. 体验版测试

1. **上传代码**:
   - 在微信开发者工具中点击"上传"
   - 填写版本号和描述
   - 上传成功后在后台生成体验版

2. **添加体验成员**:
   - 登录小程序后台
   - "成员管理" > "体验成员"
   - 添加测试人员微信号

3. **扫码测试**:
   - 体验成员用微信扫描体验版二维码
   - 测试所有功能

**预期结果**:
- ✅ 可以扫码打开小程序
- ✅ 授权登录功能正常
- ✅ API调用正常

### 3. 验证登录流程

```javascript
// 在控制台查看以下日志
👤 用户信息授权结果: {...}
✅ 获取到用户信息: {...}
🔐 开始登录流程
✅ 获取微信登录code成功
📡 发送登录请求到: http://106.54.212.67:8000/api/auth/wechat-login
✅ 登录成功
```

## 🔍 常见问题排查

### 问题1: 仍然提示"网络错误"

**可能原因**:
- 服务器API服务未运行
- 防火墙阻止了8000端口
- 小程序未配置合法域名（在非开发工具环境）

**解决方法**:
```bash
# 检查API服务
curl http://106.54.212.67:8000/health

# 检查防火墙
sudo ufw status
sudo ufw allow 8000

# 重启服务
cd /path/to/project
docker-compose -f docker-compose.lighthouse.yml restart backend
```

### 问题2: 授权后无响应

**可能原因**:
- 后端登录接口异常
- 数据库连接失败
- 微信AppID/AppSecret未配置

**解决方法**:
```bash
# 查看后端日志
docker logs targetmanage_backend_lighthouse

# 检查环境变量
docker exec targetmanage_backend_lighthouse env | grep WECHAT
```

### 问题3: 开发工具正常，真机不行

**可能原因**:
- 未配置服务器合法域名
- 使用了HTTP而非HTTPS

**解决方法**:
- 在小程序后台配置合法域名
- 或等待配置HTTPS后再进行真机测试

## 📝 配置检查清单

在部署前请确认：

- [ ] 服务器API服务正常运行 (curl http://106.54.212.67:8000/health)
- [ ] 修改了小程序的baseUrl配置
- [ ] 微信开发者工具中勾选"不校验合法域名"
- [ ] 后端配置了WECHAT_APP_ID和WECHAT_APP_SECRET
- [ ] 数据库连接正常
- [ ] 防火墙开放了8000端口

## 🎯 下一步计划

### 短期（当前可用）
- ✅ 使用HTTP + IP地址进行开发测试
- ✅ 体验版可供内部测试使用

### 中期（发布前必须）
- [ ] 申请域名
- [ ] 配置SSL证书
- [ ] 在小程序后台配置HTTPS域名
- [ ] 提交审核发布

### 长期优化
- [ ] 优化登录流程
- [ ] 添加更多授权方式
- [ ] 增强安全性配置

## 📞 技术支持

如遇到其他问题，请检查以下日志：

1. **小程序端**：微信开发者工具控制台
2. **后端日志**：`docker logs targetmanage_backend_lighthouse`
3. **Nginx日志**：`docker logs targetmanage_nginx_lighthouse`

---

**最后更新时间**: 2024-10-16
**修复版本**: v1.0.1

