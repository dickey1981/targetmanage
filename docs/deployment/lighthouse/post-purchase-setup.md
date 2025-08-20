# Lighthouse Docker CE 购买后操作指南

恭喜你购买了Docker CE模板的轻量应用服务器！现在让我们一步步完成系统部署。

## 🚀 第一步：连接服务器 (2分钟)

### 获取服务器信息

1. **登录腾讯云控制台**
   - 访问 [轻量应用服务器控制台](https://console.cloud.tencent.com/lighthouse)
   - 找到你刚购买的实例

2. **获取连接信息**
   ```
   服务器IP: xxx.xxx.xxx.xxx
   用户名: root
   密码: 你设置的密码
   ```

### 连接方式选择

#### 方式一：使用腾讯云控制台 (推荐新手)
1. 在控制台点击实例名称
2. 点击"登录"按钮
3. 选择"立即登录"，在浏览器中打开终端

#### 方式二：使用SSH客户端 (推荐)
```bash
# Windows用户可以使用PowerShell、PuTTY或Windows Terminal
# Mac/Linux用户使用终端
ssh root@your-server-ip
```

## 🔧 第二步：验证环境 (1分钟)

连接成功后，先验证Docker环境：

```bash
# 检查系统信息
uname -a

# 检查Docker版本
docker --version

# 检查Docker Compose版本
docker-compose --version

# 如果docker-compose未安装，执行：
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**期望输出示例**：
```
Docker version 20.10.x
docker-compose version 1.29.x
```

## 🚀 第三步：一键部署系统 (10-15分钟)

现在运行我们的一键部署脚本：

```bash
# 下载并运行一键部署脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/targetmanage/main/scripts/lighthouse/one-click-deploy.sh | bash
```

### 部署过程中的交互

脚本会询问以下信息，请准备好：

1. **数据库密码** (必填)
   ```
   请输入数据库密码 (至少8位): your_secure_password
   ```

2. **应用密钥** (可选，留空自动生成)
   ```
   应用密钥 (留空自动生成): [按Enter跳过]
   ```

3. **腾讯云配置** (可选，用于AI功能)
   ```
   腾讯云 Secret ID: your_secret_id
   腾讯云 Secret Key: your_secret_key
   ```

4. **微信小程序配置** (可选)
   ```
   微信 App ID: your_wechat_app_id
   微信 App Secret: your_wechat_app_secret
   ```

### 部署进度监控

部署过程中你会看到类似输出：
```
[INFO] 🚀 开始 Lighthouse 部署...
[INFO] 检查系统资源...
[INFO] 更新代码...
[INFO] 构建Docker镜像...
[INFO] 启动服务...
[INFO] 执行健康检查...
[INFO] ✅ 部署成功！
```

## ✅ 第四步：验证部署结果 (2分钟)

### 检查服务状态

```bash
# 查看所有服务状态
docker-compose -f docker-compose.lighthouse.yml ps

# 期望看到所有服务都是 "Up" 状态
```

### 访问应用

1. **获取服务器IP**
   ```bash
   curl ifconfig.me
   ```

2. **访问应用**
   - 前端应用: `http://your-server-ip`
   - API文档: `http://your-server-ip:8000/docs`
   - 健康检查: `http://your-server-ip:8000/health`

### 测试功能

在浏览器中访问 `http://your-server-ip`，你应该能看到：
- ✅ 前端页面正常加载
- ✅ 可以注册/登录用户
- ✅ API接口正常响应

## 🔧 第五步：基础安全配置 (5分钟)

### 配置SSH密钥登录 (推荐)

1. **在本地生成SSH密钥** (如果还没有)
   ```bash
   # 在本地电脑运行
   ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
   ```

2. **上传公钥到服务器**
   ```bash
   # 在本地电脑运行
   ssh-copy-id root@your-server-ip
   ```

3. **测试密钥登录**
   ```bash
   # 应该无需输入密码即可登录
   ssh root@your-server-ip
   ```

### 配置防火墙

```bash
# 检查防火墙状态
ufw status

# 如果需要，可以限制8000端口的访问（生产环境建议）
ufw deny 8000/tcp
# 这样API只能通过Nginx反向代理访问
```

### 修改默认密码

```bash
# 修改root密码
passwd root
# 输入新的强密码
```

## 📱 第六步：配置微信小程序 (可选)

如果你要开发微信小程序，需要配置服务器域名：

### 临时测试配置

在微信开发者工具中：
```
request合法域名: http://your-server-ip:8000
```

### 生产环境配置 (推荐)

1. **购买域名并解析**
   ```
   A记录: your-domain.com -> your-server-ip
   ```

2. **配置SSL证书** (后续步骤)

## 🔍 常用管理命令

### 服务管理

```bash
# 查看服务状态
docker-compose -f docker-compose.lighthouse.yml ps

# 查看服务日志
docker-compose -f docker-compose.lighthouse.yml logs -f backend

# 重启服务
docker-compose -f docker-compose.lighthouse.yml restart

# 停止所有服务
docker-compose -f docker-compose.lighthouse.yml down

# 启动所有服务
docker-compose -f docker-compose.lighthouse.yml up -d
```

### 数据库管理

```bash
# 连接数据库
docker exec -it targetmanage_postgres_lighthouse psql -U postgres -d targetmanage

# 手动备份数据库
/opt/targetmanage/backup.sh

# 查看备份文件
ls -la /opt/targetmanage/backups/
```

### 系统监控

```bash
# 查看系统资源使用
htop

# 查看磁盘使用情况
df -h

# 查看Docker容器资源使用
docker stats
```

## 🚨 故障排除

### 如果部署失败

1. **查看错误日志**
   ```bash
   # 查看部署日志
   docker-compose -f docker-compose.lighthouse.yml logs

   # 查看特定服务日志
   docker-compose -f docker-compose.lighthouse.yml logs backend
   ```

2. **重新部署**
   ```bash
   # 清理环境
   docker-compose -f docker-compose.lighthouse.yml down
   docker system prune -f

   # 重新运行部署脚本
   cd /opt/targetmanage
   ./scripts/lighthouse/deploy-lighthouse.sh
   ```

### 如果服务无法访问

1. **检查防火墙**
   ```bash
   # 检查Lighthouse控制台的防火墙设置
   # 确保开放了80和443端口
   ```

2. **检查服务状态**
   ```bash
   # 确保所有容器都在运行
   docker ps
   ```

3. **检查端口占用**
   ```bash
   netstat -tlnp | grep :80
   netstat -tlnp | grep :8000
   ```

## 📈 下一步建议

1. **配置域名和SSL** - 为生产环境配置HTTPS
2. **设置监控告警** - 配置系统监控
3. **优化性能** - 根据使用情况调整配置
4. **数据备份策略** - 设置定期备份
5. **安全加固** - 进一步提升系统安全性

## 🎉 部署成功！

恭喜你成功部署了目标管理系统！现在你拥有：

- ✅ 完整的后端API服务
- ✅ 现代化的管理后台
- ✅ 自动化的数据库备份
- ✅ 容器化的服务架构
- ✅ 仅需¥24/月的运营成本

如果在操作过程中遇到任何问题，请随时联系技术支持！
