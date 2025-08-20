# Lighthouse 快速部署指南 - 15分钟上线

本指南将帮助你在15分钟内使用腾讯云轻量应用服务器部署目标管理系统，成本仅需 **¥24/月**！

## 🚀 超快速部署 (15分钟)

### 第一步：创建 Lighthouse 实例 (3分钟)

1. **登录腾讯云控制台**
   - 访问 [轻量应用服务器控制台](https://console.cloud.tencent.com/lighthouse)

2. **创建实例**
   ```
   实例配置推荐:
   ┌─────────────────┬──────────────────────┐
   │ 套餐            │ 通用型 2核4GB 80GB   │
   │ 操作系统        │ Ubuntu 20.04 LTS     │  
   │ 带宽            │ 4Mbps                │
   │ 流量            │ 300GB/月             │
   │ 价格            │ ¥45/月 (年付¥24/月) │
   └─────────────────┴──────────────────────┘
   ```

3. **配置防火墙**
   - 开放端口：22 (SSH), 80 (HTTP), 443 (HTTPS)

### 第二步：初始化服务器 (5分钟)

1. **SSH连接服务器**
   ```bash
   ssh root@your-lighthouse-ip
   ```

2. **一键初始化**
   ```bash
   # 下载并运行初始化脚本
   curl -fsSL https://raw.githubusercontent.com/your-repo/targetmanage/main/scripts/lighthouse/setup-lighthouse.sh | bash
   
   # 重新登录使Docker生效
   exit
   ssh root@your-lighthouse-ip
   ```

### 第三步：部署应用 (5分钟)

1. **克隆项目**
   ```bash
   cd /opt/targetmanage
   git clone https://github.com/your-repo/targetmanage.git .
   ```

2. **配置环境变量**
   ```bash
   # 复制配置文件
   cp backend/.env.lighthouse backend/.env
   
   # 编辑配置 (至少设置以下必要参数)
   vim backend/.env
   ```
   
   **必要配置项**：
   ```env
   SECRET_KEY=your-unique-secret-key-here
   DB_PASSWORD=your-database-password
   TENCENT_SECRET_ID=your-tencent-secret-id
   TENCENT_SECRET_KEY=your-tencent-secret-key
   ```

3. **一键部署**
   ```bash
   chmod +x scripts/lighthouse/deploy-lighthouse.sh
   ./scripts/lighthouse/deploy-lighthouse.sh
   ```

### 第四步：验证部署 (2分钟)

1. **检查服务状态**
   ```bash
   docker-compose -f docker-compose.lighthouse.yml ps
   ```

2. **访问应用**
   - 前端：`http://your-lighthouse-ip`
   - API文档：`http://your-lighthouse-ip:8000/docs`
   - 健康检查：`http://your-lighthouse-ip:8000/health`

## 🎯 一键部署脚本

为了更快速部署，我们提供了一键部署脚本：

```bash
#!/bin/bash
# 一键部署脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/targetmanage/main/scripts/lighthouse/one-click-deploy.sh | bash
```

## 📱 微信小程序配置

部署完成后，需要配置微信小程序：

1. **在微信开发者工具中配置服务器域名**
   ```
   request合法域名: https://your-domain.com
   或临时使用IP: http://your-lighthouse-ip
   ```

2. **更新小程序配置**
   ```javascript
   // wechat-miniprogram/app.js
   globalData: {
     baseUrl: 'http://your-lighthouse-ip:8000/api/v1'
   }
   ```

## 🔧 常用操作命令

### 服务管理
```bash
# 查看服务状态
docker-compose -f docker-compose.lighthouse.yml ps

# 重启服务
docker-compose -f docker-compose.lighthouse.yml restart

# 查看日志
docker-compose -f docker-compose.lighthouse.yml logs -f backend

# 停止服务
docker-compose -f docker-compose.lighthouse.yml down

# 启动服务
docker-compose -f docker-compose.lighthouse.yml up -d
```

### 数据库管理
```bash
# 连接数据库
docker exec -it targetmanage_postgres_lighthouse psql -U postgres -d targetmanage

# 备份数据库
./backup.sh

# 查看备份文件
ls -la /opt/targetmanage/backups/
```

### 系统监控
```bash
# 查看系统资源
htop

# 查看磁盘使用
df -h

# 查看Docker资源使用
docker stats
```

## 🚨 故障排除

### 常见问题及解决方案

1. **服务启动失败**
   ```bash
   # 检查日志
   docker-compose -f docker-compose.lighthouse.yml logs backend
   
   # 检查端口占用
   netstat -tlnp | grep :8000
   
   # 重启服务
   docker-compose -f docker-compose.lighthouse.yml restart
   ```

2. **内存不足**
   ```bash
   # 查看内存使用
   free -h
   
   # 清理Docker资源
   docker system prune -f
   
   # 重启服务释放内存
   docker-compose -f docker-compose.lighthouse.yml restart
   ```

3. **磁盘空间不足**
   ```bash
   # 查看磁盘使用
   df -h
   
   # 清理日志文件
   find /opt/targetmanage/logs -name "*.log" -mtime +7 -delete
   
   # 清理Docker镜像
   docker image prune -a -f
   ```

4. **数据库连接失败**
   ```bash
   # 检查数据库容器状态
   docker ps | grep postgres
   
   # 重启数据库
   docker-compose -f docker-compose.lighthouse.yml restart postgres
   
   # 检查数据库日志
   docker logs targetmanage_postgres_lighthouse
   ```

## 🔒 安全配置

### 基础安全设置

1. **修改默认密码**
   ```bash
   # 修改root密码
   passwd root
   
   # 修改数据库密码
   vim backend/.env  # 更新DB_PASSWORD
   ```

2. **配置SSH密钥登录**
   ```bash
   # 生成SSH密钥对（在本地机器）
   ssh-keygen -t rsa -b 4096
   
   # 上传公钥到服务器
   ssh-copy-id root@your-lighthouse-ip
   
   # 禁用密码登录
   vim /etc/ssh/sshd_config
   # 设置: PasswordAuthentication no
   systemctl restart sshd
   ```

3. **配置防火墙**
   ```bash
   # 查看防火墙状态
   ufw status
   
   # 只允许必要端口
   ufw allow 22/tcp
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw deny 8000/tcp  # 生产环境关闭直接访问
   ```

## 📈 性能优化

### 资源优化配置

1. **数据库优化**
   ```bash
   # 编辑PostgreSQL配置
   docker exec -it targetmanage_postgres_lighthouse bash
   
   # 在容器内编辑配置
   echo "shared_buffers = 128MB" >> /var/lib/postgresql/data/postgresql.conf
   echo "effective_cache_size = 512MB" >> /var/lib/postgresql/data/postgresql.conf
   
   # 重启数据库
   docker-compose -f docker-compose.lighthouse.yml restart postgres
   ```

2. **Redis优化**
   ```bash
   # Redis已配置最大内存128MB和LRU淘汰策略
   # 查看Redis配置
   docker exec targetmanage_redis_lighthouse redis-cli CONFIG GET maxmemory
   ```

3. **应用优化**
   ```bash
   # 限制后端worker数量（已在Dockerfile中配置为2）
   # 启用gzip压缩（已在nginx配置中启用）
   # 静态文件缓存（已配置1年缓存）
   ```

## 💰 成本控制

### 进一步降低成本

1. **选择年付套餐**
   - 月付：¥45/月
   - 年付：¥24/月 (节省47%)

2. **监控流量使用**
   ```bash
   # 查看流量使用情况
   # 在Lighthouse控制台查看流量监控
   ```

3. **优化资源使用**
   ```bash
   # 定期清理无用文件
   find /opt/targetmanage -name "*.log" -mtime +7 -delete
   docker system prune -f
   
   # 压缩日志文件
   gzip /opt/targetmanage/logs/*.log
   ```

## 🔄 升级和迁移

### 应用更新
```bash
# 更新代码
cd /opt/targetmanage
git pull origin main

# 重新部署
./scripts/lighthouse/deploy-lighthouse.sh
```

### 数据迁移
```bash
# 导出数据
./backup.sh

# 如需迁移到更高配置，可以使用备份文件恢复数据
```

---

🎉 **恭喜！** 你的目标管理系统已成功部署在 Lighthouse 上！

**总成本**: 仅需 ¥24/月 (年付)，相比传统云服务器方案节省90%成本！

**下一步建议**:
1. 配置域名和SSL证书
2. 完善微信小程序配置
3. 添加监控和告警
4. 根据使用情况优化性能
