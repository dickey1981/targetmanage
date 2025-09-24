# Lighthouse 部署指南

## 快速部署步骤

### 1. 连接服务器

```bash
# 使用SSH连接腾讯云Lighthouse服务器
ssh root@106.54.212.67
```

### 2. 进入项目目录

```bash
cd /opt/targetmanage
```

### 3. 更新代码

```bash
# 拉取最新代码
git fetch origin
git reset --hard origin/main
```

### 4. 更新部署

```bash
# 运行更新脚本
chmod +x scripts/lighthouse/update-deployment.sh
./scripts/lighthouse/update-deployment.sh
```

## 手动部署步骤

如果自动脚本有问题，可以手动执行以下步骤：

### 1. 停止服务

```bash
docker-compose -f docker-compose.lighthouse.yml down
```

### 2. 重新构建

```bash
# 清理旧镜像
docker system prune -f

# 重新构建
docker-compose -f docker-compose.lighthouse.yml build --no-cache
```

### 3. 启动服务

```bash
# 启动数据库
docker-compose -f docker-compose.lighthouse.yml up -d postgres redis

# 等待数据库启动
sleep 15

# 执行数据库迁移
docker-compose -f docker-compose.lighthouse.yml run --rm backend alembic upgrade head

# 启动所有服务
docker-compose -f docker-compose.lighthouse.yml up -d
```

### 4. 验证部署

```bash
# 检查服务状态
docker-compose -f docker-compose.lighthouse.yml ps

# 检查健康状态
curl http://localhost:8000/health

# 查看日志
docker-compose -f docker-compose.lighthouse.yml logs -f
```

## 访问地址

- **前端应用**: http://106.54.212.67
- **API文档**: http://106.54.212.67:8000/docs
- **健康检查**: http://106.54.212.67:8000/health

## 常用管理命令

```bash
# 查看服务状态
docker-compose -f docker-compose.lighthouse.yml ps

# 查看日志
docker-compose -f docker-compose.lighthouse.yml logs -f backend
docker-compose -f docker-compose.lighthouse.yml logs -f frontend

# 重启服务
docker-compose -f docker-compose.lighthouse.yml restart

# 停止服务
docker-compose -f docker-compose.lighthouse.yml down

# 进入容器
docker exec -it targetmanage_backend_lighthouse bash
```

## 故障排除

### 1. 服务启动失败

```bash
# 查看详细日志
docker-compose -f docker-compose.lighthouse.yml logs backend

# 检查端口占用
netstat -tlnp | grep :8000
```

### 2. 数据库连接问题

```bash
# 检查数据库状态
docker exec targetmanage_postgres_lighthouse pg_isready -U postgres

# 查看数据库日志
docker-compose -f docker-compose.lighthouse.yml logs postgres
```

### 3. 内存不足

```bash
# 查看内存使用
free -h
docker stats

# 清理Docker缓存
docker system prune -a
```

## 备份和恢复

### 备份数据库

```bash
# 创建备份
docker exec targetmanage_postgres_lighthouse pg_dump -U postgres targetmanage > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 恢复数据库

```bash
# 恢复备份
docker exec -i targetmanage_postgres_lighthouse psql -U postgres targetmanage < backup_file.sql
```

## 环境变量配置

确保以下环境变量已正确配置：

```bash
# 数据库配置
DB_PASSWORD=your_secure_password

# 应用密钥
SECRET_KEY=your_secret_key

# 腾讯云配置（可选）
TENCENT_SECRET_ID=your_secret_id
TENCENT_SECRET_KEY=your_secret_key

# 微信小程序配置（可选）
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret
```

## 安全建议

1. **修改默认密码**: 确保数据库密码足够复杂
2. **配置防火墙**: 只开放必要端口
3. **定期备份**: 设置自动备份任务
4. **监控日志**: 定期检查应用日志
5. **更新系统**: 保持系统和依赖包更新

## 性能优化

1. **资源限制**: 根据服务器配置调整Docker资源限制
2. **缓存配置**: 优化Redis缓存配置
3. **数据库优化**: 根据使用情况调整数据库参数
4. **日志管理**: 定期清理日志文件
