# 🔒 安全问题修复指南

## ⚠️ 问题：Git提交中包含敏感信息

GitHub检测到提交中包含**腾讯云Secret ID**，这是严重的安全风险！

---

## 🛠️ 立即修复步骤

### 1. 点击 GitHub 提示中的 "Bypass" 按钮
- 暂时绕过这次提交
- **但不要将包含密钥的文件推送到GitHub！**

### 2. 检查并移除敏感信息

如果你有包含密钥的文档文件，请检查并移除：

```bash
# 查找可能包含密钥的文件
grep -r "Secret" *.md
grep -r "AKID" *.md
grep -r "腾讯云" *.md
```

### 3. 确保 .env 文件未被提交

```bash
# 检查 .env 是否在 git 中
git ls-files | grep ".env"

# 如果有输出，说明 .env 被跟踪了，需要移除
git rm --cached .env
git rm --cached backend/.env
git commit -m "移除敏感环境变量文件"
```

### 4. 使用环境变量

所有敏感信息应该通过环境变量传递，而不是写在代码或文档中：

**✅ 正确做法：**
```yaml
# docker-compose.lighthouse.yml
environment:
  - TENCENT_SECRET_ID=${TENCENT_SECRET_ID}
  - TENCENT_SECRET_KEY=${TENCENT_SECRET_KEY}
```

**❌ 错误做法：**
```yaml
# 不要这样做！
environment:
  - TENCENT_SECRET_ID=AKID1234567890abcdef  # 硬编码密钥
```

---

## 🔐 安全最佳实践

### 1. 永远不要提交这些文件到Git：
- `.env`
- `*.key`
- `*.pem`（除非是公钥）
- 包含密码、密钥的配置文件

### 2. 使用 .gitignore

确保以下内容在 `.gitignore` 中：
```
# 环境变量
.env
.env.local
.env.*.local

# 密钥文件
*.key
*.pem
secrets/

# SSL证书（私钥）
nginx/ssl/*.key
```

### 3. 文档中使用占位符

**✅ 正确：**
```bash
export TENCENT_SECRET_ID="your-secret-id-here"
export TENCENT_SECRET_KEY="your-secret-key-here"
```

**❌ 错误：**
```bash
export TENCENT_SECRET_ID="AKID1234567890abcdef"
```

---

## 🚨 如果密钥已泄露

### 立即行动：

1. **重新生成API密钥**
   - 登录腾讯云控制台
   - 访问控制 → 访问密钥 → API密钥管理
   - 禁用泄露的密钥
   - 创建新密钥

2. **更新服务器上的环境变量**
   ```bash
   ssh lighthouse@106.54.212.67
   cd /home/lighthouse/targetmanage
   nano .env  # 更新密钥
   docker-compose -f docker-compose.lighthouse.yml restart
   ```

3. **检查是否有异常使用**
   - 腾讯云控制台 → 费用中心 → 账单详情
   - 查看最近的API调用记录

---

## ✅ 现在可以安全提交

完成以上检查后，你可以安全地提交代码：

```bash
git add .
git commit -m "切换到HTTPS生产环境（已移除敏感信息）"
git push origin main
```

---

## 📝 当前项目的敏感信息管理

### 服务器上的 .env 文件位置
```
/home/lighthouse/targetmanage/.env
```

### 包含的敏感信息
- `TENCENT_SECRET_ID` - 腾讯云密钥ID
- `TENCENT_SECRET_KEY` - 腾讯云密钥
- `WECHAT_APP_ID` - 微信小程序AppID
- `WECHAT_APP_SECRET` - 微信小程序密钥
- `SECRET_KEY` - JWT密钥

### 这些信息应该：
- ✅ 保存在服务器的 `.env` 文件中
- ✅ 在 Docker Compose 中通过 `${变量名}` 引用
- ❌ 永远不要提交到 Git
- ❌ 永远不要写在文档中

---

**记住：密钥就像你家的钥匙，不要随便给别人！** 🔑

