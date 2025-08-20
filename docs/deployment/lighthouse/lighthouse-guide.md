# 腾讯云轻量应用服务器 Lighthouse 部署指南

本指南专为小规模业务验证阶段设计，使用腾讯云轻量应用服务器 Lighthouse 进行快速、低成本部署。

## 🌟 Lighthouse 优势

### 相比传统CVM的优势
- **成本更低**: 套餐价格包含带宽，性价比更高
- **配置简单**: 预装应用模板，一键部署
- **管理方便**: 集成防火墙、监控、快照等功能
- **快速启动**: 秒级创建，即开即用
- **适合小规模**: 专为轻量应用设计

### 适用场景
- ✅ 业务验证阶段
- ✅ 小型项目部署
- ✅ 开发测试环境
- ✅ 个人项目
- ✅ MVP产品验证

## 🏗️ Lighthouse 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    腾讯云 Lighthouse 架构                    │
├─────────────────────────────────────────────────────────────┤
│  轻量应用服务器 (2核4GB)                                   │
│    ├── Docker 容器化部署                                   │
│    ├── Nginx (前端 + 反向代理)                             │
│    ├── FastAPI 后端服务                                    │
│    ├── PostgreSQL (本地数据库)                             │
│    └── Redis (本地缓存)                                    │
├─────────────────────────────────────────────────────────────┤
│  腾讯云服务集成                                             │
│    ├── COS 对象存储 (文件存储)                             │
│    ├── OCR 文字识别                                        │
│    └── ASR 语音识别                                        │
├─────────────────────────────────────────────────────────────┤
│  域名和SSL                                                  │
│    ├── 免费域名或自有域名                                   │
│    └── Let's Encrypt 免费SSL证书                           │
└─────────────────────────────────────────────────────────────┘
```

## 💰 成本对比分析

### Lighthouse vs CVM 成本对比 (月度)

| 项目 | Lighthouse方案 | CVM方案 | 节省 |
|------|---------------|---------|------|
| 服务器 | ¥24-45 (2核4GB) | ¥200-300 (4核8GB) | ¥175-255 |
| 数据库 | ¥0 (本地部署) | ¥150-250 (云数据库) | ¥150-250 |
| Redis | ¥0 (本地部署) | ¥50-100 (云Redis) | ¥50-100 |
| 带宽 | ¥0 (包含) | ¥50-100 | ¥50-100 |
| **总计** | **¥24-45** | **¥450-750** | **¥425-705** |

**成本节省**: 约 **90%** 的成本节省！

## 🚀 快速部署步骤

### 第一步：创建 Lighthouse 实例

#### 推荐配置
```
套餐: 通用型 2核4GB 80GB SSD
系统: Ubuntu 20.04 LTS
带宽: 4Mbps (包含)
流量: 300GB/月
价格: ¥45/月 (年付¥24/月)
```

#### 通过控制台创建
1. 登录腾讯云控制台
2. 进入"轻量应用服务器"
3. 选择"自定义配置"
4. 配置实例参数
5. 设置密码并创建

#### 通过CLI创建
```bash
# 安装腾讯云CLI
pip install tccli

# 配置CLI
tccli configure set secretId your-secret-id
tccli configure set secretKey your-secret-key
tccli configure set region ap-beijing

# 创建Lighthouse实例
tccli lighthouse CreateInstances \
    --region ap-beijing \
    --bundleid bundle_ent_linux_02 \
    --period 1 \
    --instancecount 1 \
    --instancenames "targetmanage-lighthouse" \
    --loginpassword "YourPassword123!"
```

### 第二步：配置防火墙规则

```bash
# 开放必要端口
# HTTP: 80
# HTTPS: 443
# SSH: 22
# 自定义应用端口: 8000 (仅开发调试用)
```

### 第三步：连接服务器并初始化

```bash
# SSH连接服务器
ssh root@your-lighthouse-ip

# 运行初始化脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/targetmanage/main/scripts/lighthouse/setup-lighthouse.sh | bash
```

## 📦 Lighthouse 专用部署配置

### Docker Compose 轻量配置

创建 `docker-compose.lighthouse.yml`：

```yaml
version: '3.8'

services:
  # PostgreSQL 数据库 (本地部署)
  postgres:
    image: postgres:13-alpine
    container_name: targetmanage_postgres_lighthouse
    environment:
      POSTGRES_DB: targetmanage
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    restart: unless-stopped
    # 资源限制
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  # Redis 缓存 (本地部署)
  redis:
    image: redis:7-alpine
    container_name: targetmanage_redis_lighthouse
    command: redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 128M

  # Python后端服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.lighthouse
    container_name: targetmanage_backend_lighthouse
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/targetmanage
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=False
      - TENCENT_SECRET_ID=${TENCENT_SECRET_ID}
      - TENCENT_SECRET_KEY=${TENCENT_SECRET_KEY}
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  # 前端服务
  frontend:
    build:
      context: ./admin-frontend
      dockerfile: Dockerfile.lighthouse
    container_name: targetmanage_frontend_lighthouse
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256M

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: targetmanage_nginx_lighthouse
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.lighthouse.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./uploads:/var/www/uploads
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 128M

volumes:
  postgres_data:
  redis_data:
```

### 轻量化 Dockerfile

创建 `backend/Dockerfile.lighthouse`：

```dockerfile
# 轻量化Python后端Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 安装系统依赖 (最小化)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建目录
RUN mkdir -p uploads logs

# 非root用户
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=60s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### 前端轻量化配置

创建 `admin-frontend/Dockerfile.lighthouse`：

```dockerfile
# 轻量化前端Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production --no-audit
COPY . .
RUN npm run build

# 生产阶段 - 使用更小的nginx镜像
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.lighthouse.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🛠️ Lighthouse 专用脚本

### 服务器初始化脚本

创建 `scripts/lighthouse/setup-lighthouse.sh`：

```bash
#!/bin/bash
# Lighthouse 服务器初始化脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 更新系统
update_system() {
    log_info "更新系统..."
    apt update && apt upgrade -y
}

# 安装基础软件
install_basics() {
    log_info "安装基础软件..."
    apt install -y curl wget git vim htop tree unzip
}

# 安装Docker (轻量版)
install_docker() {
    log_info "安装Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker $USER
    
    # 安装Docker Compose
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
}

# 配置防火墙 (Lighthouse 内置)
configure_firewall() {
    log_info "配置防火墙..."
    # Lighthouse 使用控制台配置防火墙，这里只做基础配置
    ufw --force enable
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
}

# 创建应用目录
create_directories() {
    log_info "创建应用目录..."
    mkdir -p /opt/targetmanage/{logs,uploads,backups,nginx/ssl}
    chown -R $USER:$USER /opt/targetmanage
}

# 优化系统 (轻量化)
optimize_system() {
    log_info "优化系统配置..."
    
    # 基础优化
    cat >> /etc/sysctl.conf << EOF
# 轻量服务器优化
vm.swappiness = 10
net.core.rmem_max = 8388608
net.core.wmem_max = 8388608
EOF
    
    sysctl -p
}

# 安装监控工具 (轻量版)
install_monitoring() {
    log_info "安装监控工具..."
    apt install -y htop iotop
}

# 配置自动备份
setup_backup() {
    log_info "配置备份脚本..."
    
    cat > /opt/targetmanage/backup.sh << 'EOF'
#!/bin/bash
# 轻量数据库备份脚本
BACKUP_DIR="/opt/targetmanage/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份PostgreSQL
docker exec targetmanage_postgres_lighthouse pg_dump -U postgres targetmanage > "$BACKUP_DIR/db_$DATE.sql"
gzip "$BACKUP_DIR/db_$DATE.sql"

# 删除7天前的备份
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: db_$DATE.sql.gz"
EOF
    
    chmod +x /opt/targetmanage/backup.sh
    
    # 添加定时任务 (每天凌晨3点)
    (crontab -l 2>/dev/null; echo "0 3 * * * /opt/targetmanage/backup.sh") | crontab -
}

# 主函数
main() {
    log_info "🚀 开始初始化 Lighthouse 服务器..."
    
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root用户运行此脚本"
        exit 1
    fi
    
    update_system
    install_basics
    install_docker
    configure_firewall
    create_directories
    optimize_system
    install_monitoring
    setup_backup
    
    log_info "✅ Lighthouse 服务器初始化完成！"
    log_info "请重新登录以使Docker用户组生效"
    log_info "然后运行: cd /opt/targetmanage && git clone your-repo ."
}

# 错误处理
trap 'log_error "初始化过程中发生错误"' ERR

main "$@"
```

### Lighthouse 部署脚本

创建 `scripts/lighthouse/deploy-lighthouse.sh`：

```bash
#!/bin/bash
# Lighthouse 专用部署脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查资源使用情况
check_resources() {
    log_info "检查系统资源..."
    
    # 检查内存
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ $TOTAL_MEM -lt 3500 ]; then
        log_warn "内存不足4GB，建议升级套餐"
    fi
    
    # 检查磁盘空间
    DISK_USAGE=$(df / | awk 'NR==2{print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 80 ]; then
        log_warn "磁盘使用率超过80%，请清理空间"
    fi
    
    log_info "系统资源检查完成"
}

# 更新代码
update_code() {
    log_info "更新代码..."
    git fetch origin
    git reset --hard origin/main
}

# 备份数据库
backup_database() {
    log_info "备份数据库..."
    if docker ps | grep -q targetmanage_postgres_lighthouse; then
        /opt/targetmanage/backup.sh
    else
        log_warn "数据库容器未运行，跳过备份"
    fi
}

# 构建镜像 (优化版)
build_images() {
    log_info "构建Docker镜像..."
    
    # 清理旧镜像释放空间
    docker image prune -f
    
    # 构建后端
    docker-compose -f docker-compose.lighthouse.yml build backend
    
    # 构建前端
    docker-compose -f docker-compose.lighthouse.yml build frontend
    
    log_info "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 停止现有服务
    docker-compose -f docker-compose.lighthouse.yml down
    
    # 启动数据库服务
    docker-compose -f docker-compose.lighthouse.yml up -d postgres redis
    
    # 等待数据库启动
    sleep 10
    
    # 执行数据库迁移
    docker-compose -f docker-compose.lighthouse.yml run --rm backend alembic upgrade head
    
    # 启动所有服务
    docker-compose -f docker-compose.lighthouse.yml up -d
    
    log_info "服务启动完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    sleep 30
    
    # 检查后端服务
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "✅ 后端服务正常"
    else
        log_error "❌ 后端服务异常"
        return 1
    fi
    
    # 检查前端服务
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_info "✅ 前端服务正常"
    else
        log_error "❌ 前端服务异常"
        return 1
    fi
    
    log_info "所有服务健康检查通过"
}

# 清理资源
cleanup() {
    log_info "清理系统资源..."
    
    # 清理Docker资源
    docker system prune -f
    
    # 清理日志 (保留最近7天)
    find /opt/targetmanage/logs -name "*.log" -mtime +7 -delete
    
    log_info "资源清理完成"
}

# 显示服务状态
show_status() {
    log_info "=== 服务状态 ==="
    docker-compose -f docker-compose.lighthouse.yml ps
    
    log_info "=== 资源使用情况 ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    
    log_info "=== 系统资源 ==="
    free -h
    df -h /
}

# 主函数
main() {
    log_info "🚀 开始 Lighthouse 部署..."
    
    check_resources
    update_code
    backup_database
    build_images
    start_services
    
    if health_check; then
        log_info "✅ 部署成功！"
    else
        log_error "❌ 部署失败"
        exit 1
    fi
    
    cleanup
    show_status
    
    log_info "🎉 Lighthouse 部署完成！"
    log_info "访问地址:"
    log_info "- 前端: http://$(curl -s ifconfig.me)"
    log_info "- API: http://$(curl -s ifconfig.me):8000"
    log_info "- 文档: http://$(curl -s ifconfig.me):8000/docs"
}

# 错误处理
trap 'log_error "部署过程中发生错误"' ERR

main "$@"
```

## 🔧 环境变量配置

创建 `backend/.env.lighthouse`：

```env
# Lighthouse 轻量部署配置

# 基础配置
APP_NAME=目标管理系统
VERSION=1.0.0
DEBUG=False
HOST=0.0.0.0
PORT=8000

# 安全配置
SECRET_KEY=lighthouse-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 本地数据库配置
DATABASE_URL=postgresql://postgres:lighthouse_db_password@postgres:5432/targetmanage
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_TTL=3600

# 腾讯云服务配置 (仅AI服务)
TENCENT_SECRET_ID=your-secret-id
TENCENT_SECRET_KEY=your-secret-key
TENCENT_REGION=ap-beijing

# COS配置 (用于文件存储)
COS_BUCKET_NAME=targetmanage-lighthouse-bucket
COS_REGION=ap-beijing

# 微信小程序配置
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret

# 轻量化配置
MAX_FILE_SIZE=5242880  # 5MB (降低文件大小限制)
UPLOAD_DIR=uploads
LOG_LEVEL=INFO

# 性能优化配置
DB_POOL_SIZE=5         # 降低连接池大小
DB_MAX_OVERFLOW=10
WORKER_PROCESSES=2     # 限制worker进程数

# CORS配置
ALLOWED_HOSTS=["*"]  # 开发阶段允许所有域名
```

这样配置后，你的目标管理系统就可以在腾讯云轻量应用服务器上以极低的成本运行，非常适合业务验证阶段使用！

<function_calls>
<invoke name="todo_write">
<parameter name="merge">true
