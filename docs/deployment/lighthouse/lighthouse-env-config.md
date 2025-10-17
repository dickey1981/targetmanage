# Lighthouse 环境变量配置指南

## 📋 概述

为了安全起见，敏感信息（如API密钥）不应直接写入代码仓库，而应通过环境变量配置。

## 🔧 服务器端配置步骤

### 1. 创建 .env 文件

在服务器上的 `/opt/targetmanage/` 目录创建 `.env` 文件：

```bash
cd /opt/targetmanage

cat > .env << 'EOF'
# 腾讯云配置（ASR语音识别服务）
TENCENT_SECRET_ID=你的腾讯云SecretId
TENCENT_SECRET_KEY=你的腾讯云SecretKey

# 微信小程序配置
WECHAT_APP_ID=你的微信AppId
WECHAT_APP_SECRET=你的微信AppSecret

# 应用密钥
SECRET_KEY=lighthouse-secret-key-20241016

# 腾讯云COS配置（可选）
COS_BUCKET_NAME=

# ASR开发模式（true=使用模拟识别，不调用真实API；false=使用真实API）
ASR_DEV_MODE=true
EOF

# 设置文件权限（仅root可读写）
chmod 600 .env
```

### 2. 重启服务

```bash
cd /opt/targetmanage

# 重启所有服务以加载新的环境变量
docker-compose -f docker-compose.lighthouse.yml down
docker-compose -f docker-compose.lighthouse.yml up -d

# 等待服务启动
sleep 15

# 验证环境变量是否加载成功
docker exec targetmanage_backend_lighthouse env | grep -E "(TENCENT_SECRET|ASR_DEV_MODE|WECHAT)"
```

### 3. 验证配置

```bash
# 查看后端启动日志
docker logs --tail 30 targetmanage_backend_lighthouse

# 应该看到类似以下内容：
# ✅ 语音识别服务初始化成功
# 或
# 🔧 开发模式：使用模拟语音识别
```

## 🔐 安全说明

### ✅ 正确做法
- `.env` 文件只存在于服务器上，不提交到 Git
- `.env` 文件权限设置为 `600`（仅所有者可读写）
- 使用 `.env.example` 作为配置模板提交到 Git

### ❌ 错误做法
- 不要将密钥直接写入 `docker-compose.yml`
- 不要将 `.env` 文件提交到 Git
- 不要在公开的脚本中包含密钥

## 📝 环境变量说明

| 变量名 | 说明 | 必需 | 示例值 |
|--------|------|------|--------|
| `TENCENT_SECRET_ID` | 腾讯云 API 密钥 ID | 否* | AKIDxxxx |
| `TENCENT_SECRET_KEY` | 腾讯云 API 密钥 Key | 否* | xxxxxxxx |
| `WECHAT_APP_ID` | 微信小程序 AppID | 是 | wx1234567890 |
| `WECHAT_APP_SECRET` | 微信小程序 AppSecret | 是 | xxxxxxxx |
| `SECRET_KEY` | 应用加密密钥 | 是 | 随机字符串 |
| `ASR_DEV_MODE` | ASR 开发模式开关 | 否 | true/false |
| `COS_BUCKET_NAME` | 腾讯云 COS 存储桶 | 否 | mybucket-123 |

\* 如果 `ASR_DEV_MODE=true`，则腾讯云密钥可以不配置

## 🎯 ASR 开发模式说明

### 开启开发模式（`ASR_DEV_MODE=true`）
- ✅ 不调用真实的腾讯云 ASR API
- ✅ 返回预设的模拟识别结果
- ✅ 不产生 API 调用费用
- ✅ 可以正常测试语音输入流程

### 关闭开发模式（`ASR_DEV_MODE=false`）
- 使用真实的腾讯云 ASR API
- 需要配置 `TENCENT_SECRET_ID` 和 `TENCENT_SECRET_KEY`
- 会产生 API 调用费用（按实际使用量计费）
- 提供真实的语音识别能力

## 🔄 更新配置后重启

每次修改 `.env` 文件后，需要重启服务：

```bash
cd /opt/targetmanage
docker-compose -f docker-compose.lighthouse.yml restart backend
```

## 📞 获取腾讯云密钥

1. 登录腾讯云控制台
2. 访问：https://console.cloud.tencent.com/cam/capi
3. 创建或查看密钥
4. 复制 `SecretId` 和 `SecretKey`

## 🐛 故障排查

### 问题：环境变量未加载

```bash
# 检查 .env 文件是否存在
ls -la /opt/targetmanage/.env

# 检查 .env 文件内容
cat /opt/targetmanage/.env

# 检查容器内的环境变量
docker exec targetmanage_backend_lighthouse env | grep TENCENT
```

### 问题：语音识别失败

```bash
# 查看后端日志
docker logs --tail 50 targetmanage_backend_lighthouse | grep -i "asr\|voice\|recognition"

# 检查是否启用了开发模式
docker exec targetmanage_backend_lighthouse env | grep ASR_DEV_MODE
```

