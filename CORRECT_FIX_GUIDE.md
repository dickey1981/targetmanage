# 正确的修复方案

## 📋 问题重新分析

### 实际情况
1. ✅ 域名 `targetmanage.cn` 已购买并解析到 `106.54.212.67`
2. ❌ Nginx未配置域名反向代理，导致API无法通过域名访问
3. ✅ 手机号授权是业务必需功能，不能移除

### 错误理解（之前）
- ❌ 以为域名没有解析
- ❌ 以为手机号授权可以去掉
- ❌ 建议使用IP地址代替域名

## ✅ 正确的解决方案

### 步骤1: 配置Nginx支持域名访问

已创建 `admin-frontend/nginx.lighthouse-http.conf` 文件，配置了：
- 域名: `targetmanage.cn`, `www.targetmanage.cn`, `106.54.212.67`
- API代理: `/api/` → `backend:8000`
- 前端代理: `/` → `frontend:80`
- 健康检查: `/health`

### 步骤2: 部署新配置

**在服务器上执行以下命令**：

```bash
# SSH连接到服务器
ssh root@106.54.212.67

# 进入项目目录
cd /opt/targetmanage  # 或你的实际路径

# 拉取最新代码
git pull

# 重启Nginx容器
docker-compose -f docker-compose.lighthouse.yml restart nginx

# 查看Nginx日志
docker logs targetmanage_nginx_lighthouse

# 测试配置
curl http://targetmanage.cn/health
curl http://targetmanage.cn/api/test
```

### 步骤3: 配置微信小程序合法域名

1. **登录微信小程序后台**: https://mp.weixin.qq.com/

2. **进入"开发" > "开发管理" > "开发设置"**

3. **配置"服务器域名"**:
   - **request合法域名**: 
     - `http://targetmanage.cn`
     - `http://106.54.212.67`
   - **uploadFile合法域名**: 
     - `http://targetmanage.cn`
     - `http://106.54.212.67`
   - **downloadFile合法域名**: 
     - `http://targetmanage.cn`

### 步骤4: 测试手机号授权

#### 重要说明：手机号授权的限制

**手机号授权 (`getPhoneNumber`) 要求**：
1. ✅ 小程序必须已认证（个人小程序不支持）
2. ✅ 在真机环境中测试（开发工具可能不支持）
3. ✅ 使用HTTPS域名（长期方案）

**当前测试方案**：
- 在开发工具中：使用"微信授权登录"（备用方案）
- 在真机体验版：测试手机号授权

## 🔧 手机号授权的两种实现方式

### 方式1: getPhoneNumber（推荐，但有限制）

```xml
<button open-type="getPhoneNumber" bindgetphonenumber="onGetPhoneNumber">
  授权获取手机号
</button>
```

**限制**：
- 需要企业认证的小程序
- 开发工具中可能不弹出授权窗口
- 必须在真机上测试

### 方式2: 手机号输入（备用方案）

如果无法使用 `getPhoneNumber`，可以：
1. 让用户手动输入手机号
2. 发送验证码验证
3. 完成登录

## 📱 测试流程

### 开发环境测试

1. **配置开发工具**
   - 勾选"不校验合法域名"
   - 勾选"不校验TLS版本"

2. **测试步骤**
   ```
   点击"授权获取手机号" 
   → 如果弹出授权窗口 → 点击允许 → 登录成功
   → 如果没有弹出 → 使用"微信授权登录"备用方案
   ```

### 真机测试（体验版）

1. **上传代码生成体验版**
   
2. **扫码打开小程序**
   
3. **测试手机号授权**
   - 应该能弹出授权窗口
   - 授权后可以正常登录

## ⚠️ 关于HTTP vs HTTPS

### 当前状态（HTTP）

**优点**：
- ✅ 快速部署
- ✅ 开发测试方便
- ✅ 体验版可用

**缺点**：
- ❌ 无法正式发布
- ❌ 手机号授权可能受限
- ❌ 安全性较低

### 长期方案（HTTPS）

**必须完成以下步骤才能正式发布**：

#### 1. 申请SSL证书

##### 选项A: Let's Encrypt 免费证书

```bash
# 安装certbot
sudo apt install certbot

# 申请证书
sudo certbot certonly --standalone -d targetmanage.cn -d www.targetmanage.cn

# 证书位置
# /etc/letsencrypt/live/targetmanage.cn/fullchain.pem
# /etc/letsencrypt/live/targetmanage.cn/privkey.pem
```

##### 选项B: 腾讯云SSL证书（推荐）

1. 登录腾讯云控制台
2. 进入"SSL证书"服务
3. 申请免费DV证书
4. 填写域名: `targetmanage.cn`
5. 验证域名所有权（DNS验证）
6. 下载证书文件

#### 2. 配置SSL证书

```bash
# 创建证书目录
mkdir -p nginx/ssl

# 上传证书文件
# cert.pem - 证书文件
# key.pem - 私钥文件

# 修改docker-compose.yml，使用HTTPS配置
# 将 nginx.lighthouse-http.conf 改为 nginx.lighthouse.conf
```

#### 3. 更新Docker配置

```bash
# 停止服务
docker-compose -f docker-compose.lighthouse.yml down

# 启动服务（使用HTTPS配置）
docker-compose -f docker-compose.lighthouse.yml up -d

# 测试HTTPS
curl https://targetmanage.cn/health
```

#### 4. 更新小程序配置

```javascript
// wechat-miniprogram/config/env.js
production: {
  baseUrl: 'https://targetmanage.cn',  // 改为HTTPS
  apiVersion: 'v1',
  debug: false
}
```

#### 5. 更新微信小程序后台

在小程序后台配置HTTPS域名：
- `https://targetmanage.cn`

## 🧪 快速验证脚本

在服务器上创建并运行：

```bash
#!/bin/bash
# test-deployment.sh

echo "🔍 检查域名解析..."
nslookup targetmanage.cn

echo ""
echo "🔍 检查80端口..."
curl -I http://targetmanage.cn

echo ""
echo "🔍 检查API健康..."
curl http://targetmanage.cn/health

echo ""
echo "🔍 检查API测试接口..."
curl http://targetmanage.cn/api/test

echo ""
echo "🔍 检查Docker容器..."
docker ps | grep targetmanage

echo ""
echo "✅ 检查完成"
```

## 📞 如果仍然有问题

### 问题1: 域名无法访问API

**检查**：
```bash
# 1. 检查Nginx配置是否生效
docker exec targetmanage_nginx_lighthouse cat /etc/nginx/nginx.conf

# 2. 检查Nginx错误日志
docker logs targetmanage_nginx_lighthouse

# 3. 测试内部网络
docker exec targetmanage_nginx_lighthouse wget -O- http://backend:8000/health
```

### 问题2: 手机号授权不弹窗

**原因**：
- 小程序未认证（个人小程序不支持）
- 在开发工具中测试（不支持）

**解决**：
1. 确认小程序类型（企业认证）
2. 在真机上测试
3. 或使用备用的"微信授权登录"

### 问题3: 体验版提示网络错误

**检查**：
1. 是否在小程序后台配置了合法域名
2. 域名是否可以正常访问
3. 是否需要关闭"校验合法域名"

## 📝 部署检查清单

部署前请确认：

- [ ] Nginx配置文件已更新
- [ ] Docker Compose配置已更新
- [ ] 在服务器上拉取了最新代码
- [ ] 重启了Nginx容器
- [ ] 可以通过域名访问健康检查接口
- [ ] 在小程序后台配置了合法域名
- [ ] 手机号授权功能已测试（真机）
- [ ] 微信授权登录备用方案正常

## 🎯 总结

### 短期方案（当前）
1. ✅ 使用HTTP协议
2. ✅ 配置Nginx域名反向代理
3. ✅ 保留手机号授权功能
4. ✅ 提供微信授权备用方案
5. ✅ 体验版可供内部测试

### 长期方案（正式发布前）
1. ⏳ 申请SSL证书
2. ⏳ 配置HTTPS
3. ⏳ 更新小程序域名配置
4. ⏳ 提交审核发布

---

**更新时间**: 2024-10-16
**版本**: v2.0 (正确版本)

