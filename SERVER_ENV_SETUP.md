# 🚀 服务器环境变量配置指南

## 问题说明

GitHub 阻止了包含密钥的推送，这是正确的安全措施。我们应该在服务器上使用 `.env` 文件来管理密钥。

## 📋 快速配置步骤

### 方法一：在服务器上手动配置（推荐）

在服务器上执行以下命令：

```bash
cd /opt/targetmanage

# 创建 .env 文件
# 注意：请将下面的占位符替换为您的实际密钥值
cat > .env << 'EOF'
TENCENT_SECRET_ID=your_tencent_secret_id_here
TENCENT_SECRET_KEY=your_tencent_secret_key_here
WECHAT_APP_ID=your_wechat_appid_here
WECHAT_APP_SECRET=your_wechat_appsecret_here
SECRET_KEY=lighthouse-secret-key-20241016
COS_BUCKET_NAME=
ASR_DEV_MODE=true
EOF

# 设置文件权限（仅root可读写）
chmod 600 .env

# 验证文件内容
cat .env

# 重启服务
docker-compose -f docker-compose.lighthouse.yml down
docker-compose -f docker-compose.lighthouse.yml up -d

# 等待启动
sleep 15

# 验证环境变量
echo "=== 验证环境变量 ==="
docker exec targetmanage_backend_lighthouse env | grep -E "(TENCENT_SECRET|ASR_DEV_MODE|WECHAT_APP)"

# 查看日志
echo ""
echo "=== 查看启动日志 ==="
docker logs --tail 30 targetmanage_backend_lighthouse
```

### 方法二：使用交互式脚本

```bash
cd /opt/targetmanage

# 下载并运行配置脚本（需要先 git pull）
git pull origin main
chmod +x scripts/lighthouse/setup-env.sh
./scripts/lighthouse/setup-env.sh
```

## ✅ 验证配置成功

成功配置后，日志应该显示：

```
✅ 语音识别服务初始化成功
```

或（如果 ASR_DEV_MODE=true）：

```
🔧 开发模式：使用模拟语音识别
```

## 🔐 本地 Git 操作

在本地，您现在可以安全地提交和推送代码：

1. 点击弹窗的 "Ok" 按钮
2. 在 GitHub Desktop 中点击左下角的 "Undo" 按钮撤销提交
3. 修改的文件会回到 "Changes" 区域
4. 重新提交（现在文件已经不包含密钥了）

## 📝 环境变量说明

| 变量 | 说明 | 示例 |
|------|------|-----|
| `TENCENT_SECRET_ID` | 腾讯云密钥ID | AKID... |
| `TENCENT_SECRET_KEY` | 腾讯云密钥Key | 32位字符串 |
| `WECHAT_APP_ID` | 微信小程序AppID | wx... |
| `WECHAT_APP_SECRET` | 微信小程序AppSecret | 32位字符串 |
| `ASR_DEV_MODE` | ASR开发模式 | true（推荐，使用模拟识别） |

## 🎯 ASR 开发模式

- `ASR_DEV_MODE=true`: 使用模拟识别，不调用真实API，不产生费用
- `ASR_DEV_MODE=false`: 使用真实API，会产生费用

建议先使用 `true` 测试功能，确认无误后再改为 `false`。

## 🔑 获取密钥信息

### 腾讯云密钥
1. 登录腾讯云控制台
2. 访问：https://console.cloud.tencent.com/cam/capi
3. 创建或查看密钥
4. 复制 SecretId 和 SecretKey

### 微信小程序密钥
1. 登录微信公众平台
2. 进入小程序管理后台
3. 开发 → 开发管理 → 开发设置
4. 查看 AppID 和 AppSecret

## 🐛 故障排查

### 环境变量未加载

```bash
# 检查 .env 文件
ls -la /opt/targetmanage/.env
cat /opt/targetmanage/.env

# 完全重启
cd /opt/targetmanage
docker-compose -f docker-compose.lighthouse.yml down
docker-compose -f docker-compose.lighthouse.yml up -d
```

### 语音识别不工作

```bash
# 查看详细日志
docker logs -f targetmanage_backend_lighthouse

# 检查环境变量
docker exec targetmanage_backend_lighthouse env | grep ASR
```

## 📞 联系方式

如需获取实际的密钥值，请联系项目管理员。
