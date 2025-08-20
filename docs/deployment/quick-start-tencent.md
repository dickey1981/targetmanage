# 腾讯云快速部署指南

本指南将帮助你在30分钟内将目标管理系统部署到腾讯云。

## 🚀 快速部署步骤

### 第一步：准备腾讯云账号和服务

1. **注册腾讯云账号**
   - 访问 [腾讯云官网](https://cloud.tencent.com/) 注册账号
   - 完成实名认证

2. **开通所需服务**
   ```bash
   # 需要开通的服务
   - 云服务器 CVM
   - 云数据库 PostgreSQL
   - 云数据库 Redis  
   - 对象存储 COS
   - 文字识别 OCR
   - 语音识别 ASR
   ```

3. **获取API密钥**
   - 访问 [API密钥管理](https://console.cloud.tencent.com/cam/capi)
   - 创建密钥，记录 `SecretId` 和 `SecretKey`

### 第二步：创建云服务器

```bash
# 推荐配置
实例类型: 标准型S5.LARGE8
CPU: 4核
内存: 8GB
系统盘: 50GB SSD
操作系统: Ubuntu 20.04 LTS
网络: VPC网络，分配公网IP
```

### 第三步：初始化服务器

1. **连接服务器**
   ```bash
   ssh root@your-server-ip
   ```

2. **运行初始化脚本**
   ```bash
   # 下载项目代码
   git clone https://github.com/your-repo/targetmanage.git
   cd targetmanage
   
   # 运行服务器初始化脚本
   chmod +x scripts/tencent-cloud/setup-server.sh
   ./scripts/tencent-cloud/setup-server.sh
   
   # 重新登录以应用用户组变更
   exit
   ssh root@your-server-ip
   ```

### 第四步：创建数据库

1. **创建PostgreSQL实例**
   ```bash
   # 通过腾讯云控制台创建，或使用CLI
   tccli postgres CreateInstances \
       --region ap-beijing \
       --zone ap-beijing-3 \
       --dbversion 13.3 \
       --storage 50 \
       --memory 2 \
       --instancecount 1 \
       --adminname postgres \
       --adminpassword "YourDBPassword123!" \
       --vpcid "vpc-xxxxxxxx" \
       --subnetid "subnet-xxxxxxxx"
   ```

2. **创建Redis实例**
   ```bash
   # 通过控制台创建1GB Redis实例
   # 记录连接地址和密码
   ```

### 第五步：配置环境变量

1. **复制配置文件**
   ```bash
   cd /opt/targetmanage
   cp backend/.env.example backend/.env.production
   ```

2. **编辑配置文件**
   ```bash
   vim backend/.env.production
   ```

3. **填入配置信息**
   ```env
   # 基础配置
   DEBUG=False
   SECRET_KEY=your-production-secret-key-change-this
   
   # 数据库配置
   DATABASE_URL=postgresql://postgres:YourDBPassword123!@your-db-host:5432/targetmanage
   REDIS_URL=redis://:YourRedisPassword@your-redis-host:6379/0
   
   # 腾讯云配置
   TENCENT_SECRET_ID=your-secret-id
   TENCENT_SECRET_KEY=your-secret-key
   TENCENT_REGION=ap-beijing
   
   # 微信小程序配置
   WECHAT_APP_ID=your-wechat-app-id
   WECHAT_APP_SECRET=your-wechat-app-secret
   
   # 域名配置
   ALLOWED_HOSTS=["https://your-domain.com"]
   ```

### 第六步：部署应用

1. **运行部署脚本**
   ```bash
   chmod +x scripts/tencent-cloud/deploy.sh
   ./scripts/tencent-cloud/deploy.sh
   ```

2. **等待部署完成**
   - 脚本会自动构建镜像
   - 执行数据库迁移
   - 启动所有服务

### 第七步：配置域名和SSL

1. **配置域名解析**
   ```bash
   # 将域名A记录指向服务器公网IP
   your-domain.com -> your-server-ip
   admin.your-domain.com -> your-server-ip
   ```

2. **申请SSL证书**
   - 在腾讯云控制台申请免费SSL证书
   - 下载证书文件到服务器

3. **配置Nginx**
   ```bash
   # 将SSL证书放到指定目录
   mkdir -p /opt/targetmanage/nginx/ssl
   # 上传证书文件到该目录
   
   # 重启Nginx
   docker-compose -f docker-compose.tencent.yml restart nginx
   ```

## 🔧 验证部署

### 检查服务状态
```bash
# 查看所有服务状态
docker-compose -f docker-compose.tencent.yml ps

# 检查日志
docker-compose -f docker-compose.tencent.yml logs backend
docker-compose -f docker-compose.tencent.yml logs frontend
```

### 访问应用
- **后端API**: `https://your-domain.com/api/v1/health`
- **API文档**: `https://your-domain.com/docs`
- **管理后台**: `https://admin.your-domain.com`
- **监控面板**: `https://your-domain.com:5555`

### 健康检查
```bash
# 后端健康检查
curl https://your-domain.com/api/v1/health

# 数据库连接检查
docker-compose -f docker-compose.tencent.yml exec backend python -c "
from app.config.database import test_db_connection
import asyncio
result = asyncio.run(test_db_connection())
print('Database:', 'OK' if result else 'Failed')
"
```

## 📱 微信小程序配置

1. **配置服务器域名**
   ```javascript
   // 在微信开发者工具中配置
   request合法域名: https://your-domain.com
   uploadFile合法域名: https://your-domain.com
   downloadFile合法域名: https://your-domain.com
   ```

2. **更新小程序配置**
   ```javascript
   // wechat-miniprogram/app.js
   globalData: {
     baseUrl: 'https://your-domain.com/api/v1'
   }
   ```

## 🔍 监控和维护

### 日志查看
```bash
# 查看应用日志
tail -f /opt/targetmanage/logs/app.log

# 查看Nginx日志
tail -f /opt/targetmanage/logs/nginx/access.log
tail -f /opt/targetmanage/logs/nginx/error.log
```

### 备份数据库
```bash
# 手动备份
/opt/targetmanage/backup.sh

# 查看备份文件
ls -la /opt/targetmanage/backups/
```

### 更新应用
```bash
# 拉取最新代码并重新部署
cd /opt/targetmanage
git pull origin main
./scripts/tencent-cloud/deploy.sh
```

## 🚨 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 检查Docker日志
   docker-compose -f docker-compose.tencent.yml logs --tail=50 backend
   
   # 检查环境变量
   cat backend/.env.production
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库网络连通性
   telnet your-db-host 5432
   
   # 检查安全组规则
   # 确保数据库安全组允许服务器IP访问5432端口
   ```

3. **微信小程序无法连接**
   ```bash
   # 检查域名配置
   # 确保在微信开发者工具中配置了正确的服务器域名
   
   # 检查SSL证书
   curl -I https://your-domain.com/api/v1/health
   ```

### 性能优化

1. **数据库优化**
   ```sql
   -- 创建索引
   CREATE INDEX idx_goals_user_id ON goals(user_id);
   CREATE INDEX idx_tasks_goal_id ON tasks(goal_id);
   CREATE INDEX idx_progress_user_id ON progresses(user_id);
   ```

2. **Redis缓存优化**
   ```bash
   # 配置Redis最大内存
   redis-cli CONFIG SET maxmemory 256mb
   redis-cli CONFIG SET maxmemory-policy allkeys-lru
   ```

## 💰 成本优化

### 按量计费转包年包月
```bash
# 当应用稳定后，可以将按量计费实例转为包年包月
# 通过控制台操作，通常可以节省30-50%的成本
```

### 监控资源使用
- 定期检查CPU、内存使用率
- 根据实际使用情况调整实例规格
- 清理不必要的日志和备份文件

---

🎉 **恭喜！** 你的目标管理系统已经成功部署到腾讯云！

如有问题，请参考详细的部署文档或联系技术支持。
