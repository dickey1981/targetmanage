# 微信小程序配置说明

## 🔑 获取微信小程序AppID和AppSecret

### 步骤1：登录微信公众平台
1. 访问 [微信公众平台](https://mp.weixin.qq.com/)
2. 使用小程序管理员账号登录

### 步骤2：获取AppID
1. 在左侧菜单选择"开发" → "开发管理" → "开发设置"
2. 在"开发者ID"部分可以看到 `AppID(小程序ID)`
3. 复制这个AppID

### 步骤3：获取AppSecret
1. 在同一个页面，点击 `AppSecret(小程序密钥)` 旁边的"重置"按钮
2. 输入管理员密码确认
3. 复制新生成的AppSecret

## ⚙️ 配置后端

### 更新配置文件
编辑 `backend/app/config/settings.py`：

```python
# 微信小程序配置
WECHAT_APP_ID: str = "wx1234567890abcdef"  # 替换为您的实际AppID
WECHAT_APP_SECRET: str = "abcdef1234567890abcdef1234567890"  # 替换为您的实际AppSecret
```

### 或者使用环境变量
创建 `.env` 文件：

```bash
WECHAT_APP_ID=wx1234567890abcdef
WECHAT_APP_SECRET=abcdef1234567890abcdef1234567890
```

## 🧪 测试配置

### 1. 更新数据库表结构
```bash
cd backend
python scripts/update_database.py
```

### 2. 重启后端服务
```bash
python start_dev.py
```

### 3. 测试登录功能
在微信开发者工具中测试登录，应该能看到：
- 成功获取微信code
- 成功调用微信API获取openId
- 成功创建或更新用户

## ⚠️ 注意事项

1. **AppSecret保密**：不要将AppSecret提交到代码仓库
2. **域名配置**：确保在微信公众平台配置了合法域名
3. **HTTPS要求**：生产环境必须使用HTTPS
4. **IP白名单**：如果使用IP白名单，需要添加服务器IP

## 🔍 常见问题

### 错误：invalid appid
- 检查AppID是否正确
- 确认AppSecret是否匹配
- 验证小程序是否已发布

### 错误：invalid code
- 检查code是否过期（5分钟内有效）
- 确认code是否重复使用
- 验证小程序环境是否正确

## 📞 技术支持

如果遇到问题，请：
1. 检查微信公众平台的错误日志
2. 查看后端控制台的详细错误信息
3. 确认网络连接和防火墙设置
