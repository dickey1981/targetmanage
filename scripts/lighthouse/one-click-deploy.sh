#!/bin/bash
# Lighthouse 一键部署脚本
# 适用于全新的 Lighthouse 服务器

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 显示欢迎信息
show_welcome() {
    clear
    echo -e "${BLUE}"
    echo "=================================================="
    echo "    目标管理系统 Lighthouse 一键部署脚本"
    echo "=================================================="
    echo -e "${NC}"
    echo "本脚本将自动完成以下操作："
    echo "1. 初始化 Lighthouse 服务器环境"
    echo "2. 安装 Docker 和相关依赖"
    echo "3. 下载项目代码"
    echo "4. 配置环境变量"
    echo "5. 构建和启动服务"
    echo "6. 验证部署结果"
    echo ""
    echo -e "${YELLOW}预计用时: 10-15分钟${NC}"
    echo ""
    read -p "按 Enter 键开始部署，或 Ctrl+C 取消..."
}

# 收集配置信息
collect_config() {
    log_step "收集配置信息"
    
    echo "请提供以下必要配置信息："
    
    # 数据库密码
    while true; do
        read -s -p "数据库密码 (至少8位): " DB_PASSWORD
        echo
        if [ ${#DB_PASSWORD} -ge 8 ]; then
            break
        else
            echo "密码长度至少8位，请重新输入"
        fi
    done
    
    # 应用密钥
    read -p "应用密钥 (留空自动生成): " SECRET_KEY
    if [ -z "$SECRET_KEY" ]; then
        SECRET_KEY=$(openssl rand -hex 32)
        echo "已生成随机密钥: ${SECRET_KEY:0:16}..."
    fi
    
    # 腾讯云配置
    echo ""
    echo "腾讯云服务配置 (可选，用于AI功能):"
    read -p "腾讯云 Secret ID (可选): " TENCENT_SECRET_ID
    read -p "腾讯云 Secret Key (可选): " TENCENT_SECRET_KEY
    
    # 微信小程序配置
    echo ""
    echo "微信小程序配置 (可选):"
    read -p "微信 App ID (可选): " WECHAT_APP_ID
    read -p "微信 App Secret (可选): " WECHAT_APP_SECRET
    
    log_info "配置信息收集完成"
}

# 检查系统环境
check_environment() {
    log_step "检查系统环境"
    
    # 检查操作系统
    if [ ! -f /etc/ubuntu-release ] && [ ! -f /etc/debian_version ]; then
        log_warn "建议使用 Ubuntu 20.04 LTS"
    fi
    
    # 检查内存
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ $TOTAL_MEM -lt 3500 ]; then
        log_warn "内存小于4GB，建议升级套餐"
    else
        log_info "内存: ${TOTAL_MEM}MB ✓"
    fi
    
    # 检查磁盘空间
    DISK_FREE=$(df / | awk 'NR==2{printf "%.0f", $4/1024}')
    if [ $DISK_FREE -lt 10240 ]; then
        log_warn "可用磁盘空间小于10GB"
    else
        log_info "磁盘空间: ${DISK_FREE}MB ✓"
    fi
}

# 初始化服务器
initialize_server() {
    log_step "初始化服务器环境"
    
    # 更新系统
    log_info "更新系统包..."
    apt update && apt upgrade -y
    
    # 安装基础软件
    log_info "安装基础软件..."
    apt install -y curl wget git vim htop tree unzip openssl
    
    # 安装Docker
    log_info "安装Docker..."
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
    fi
    
    # 安装Docker Compose
    log_info "安装Docker Compose..."
    if ! command -v docker-compose &> /dev/null; then
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    # 配置防火墙
    log_info "配置防火墙..."
    ufw --force enable
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # 创建应用目录
    log_info "创建应用目录..."
    mkdir -p /opt/targetmanage/{logs,uploads,backups,nginx/ssl}
    
    log_info "服务器初始化完成 ✓"
}

# 下载项目代码
download_project() {
    log_step "下载项目代码"
    
    cd /opt/targetmanage
    
    # 如果目录不为空，先备份
    if [ "$(ls -A .)" ]; then
        log_warn "目录不为空，创建备份..."
        tar -czf "backup_$(date +%Y%m%d_%H%M%S).tar.gz" * 2>/dev/null || true
    fi
    
    # 克隆项目
    log_info "克隆项目代码..."
    git clone https://github.com/your-repo/targetmanage.git temp_repo
    mv temp_repo/* .
    mv temp_repo/.* . 2>/dev/null || true
    rm -rf temp_repo
    
    log_info "项目代码下载完成 ✓"
}

# 配置环境变量
configure_environment() {
    log_step "配置环境变量"
    
    # 创建环境变量文件
    cat > backend/.env << EOF
# Lighthouse 部署配置 - 自动生成
# 生成时间: $(date)

# 基础配置
APP_NAME=目标管理系统
VERSION=1.0.0
DEBUG=False
HOST=0.0.0.0
PORT=8000

# 安全配置
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/targetmanage
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_TTL=3600

# 腾讯云配置
TENCENT_SECRET_ID=${TENCENT_SECRET_ID}
TENCENT_SECRET_KEY=${TENCENT_SECRET_KEY}
TENCENT_REGION=ap-beijing

# 微信小程序配置
WECHAT_APP_ID=${WECHAT_APP_ID}
WECHAT_APP_SECRET=${WECHAT_APP_SECRET}

# 轻量化配置
MAX_FILE_SIZE=5242880
UPLOAD_DIR=uploads
LOG_LEVEL=INFO
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
WORKER_PROCESSES=2

# CORS配置
ALLOWED_HOSTS=["*"]
EOF

    # 设置Docker Compose环境变量
    cat > .env << EOF
DB_PASSWORD=${DB_PASSWORD}
SECRET_KEY=${SECRET_KEY}
TENCENT_SECRET_ID=${TENCENT_SECRET_ID}
TENCENT_SECRET_KEY=${TENCENT_SECRET_KEY}
WECHAT_APP_ID=${WECHAT_APP_ID}
WECHAT_APP_SECRET=${WECHAT_APP_SECRET}
EOF
    
    log_info "环境变量配置完成 ✓"
}

# 构建和启动服务
deploy_services() {
    log_step "构建和启动服务"
    
    # 构建镜像
    log_info "构建Docker镜像..."
    docker-compose -f docker-compose.lighthouse.yml build --no-cache
    
    # 启动数据库服务
    log_info "启动数据库服务..."
    docker-compose -f docker-compose.lighthouse.yml up -d postgres redis
    
    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 15
    
    # 执行数据库迁移
    log_info "执行数据库迁移..."
    docker-compose -f docker-compose.lighthouse.yml run --rm backend alembic upgrade head
    
    # 启动所有服务
    log_info "启动所有服务..."
    docker-compose -f docker-compose.lighthouse.yml up -d
    
    log_info "服务部署完成 ✓"
}

# 验证部署
verify_deployment() {
    log_step "验证部署结果"
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 获取服务器IP
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "localhost")
    
    # 检查服务状态
    log_info "检查服务状态..."
    
    # 检查后端健康
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "✅ 后端服务正常"
        BACKEND_OK=true
    else
        log_error "❌ 后端服务异常"
        BACKEND_OK=false
    fi
    
    # 检查前端
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_info "✅ 前端服务正常"
        FRONTEND_OK=true
    else
        log_error "❌ 前端服务异常"
        FRONTEND_OK=false
    fi
    
    # 检查数据库
    if docker exec targetmanage_postgres_lighthouse pg_isready -U postgres > /dev/null 2>&1; then
        log_info "✅ 数据库服务正常"
        DATABASE_OK=true
    else
        log_error "❌ 数据库服务异常"
        DATABASE_OK=false
    fi
    
    # 显示部署结果
    echo ""
    echo -e "${BLUE}=================================================="
    echo "              部署完成！"
    echo -e "==================================================${NC}"
    echo ""
    
    if [ "$BACKEND_OK" = true ] && [ "$FRONTEND_OK" = true ] && [ "$DATABASE_OK" = true ]; then
        echo -e "${GREEN}🎉 所有服务部署成功！${NC}"
        echo ""
        echo "访问地址："
        echo "- 前端应用: http://${SERVER_IP}"
        echo "- API文档:  http://${SERVER_IP}:8000/docs"
        echo "- 健康检查: http://${SERVER_IP}:8000/health"
        echo ""
        echo "管理命令："
        echo "- 查看状态: docker-compose -f docker-compose.lighthouse.yml ps"
        echo "- 查看日志: docker-compose -f docker-compose.lighthouse.yml logs -f"
        echo "- 重启服务: docker-compose -f docker-compose.lighthouse.yml restart"
        echo ""
        echo -e "${YELLOW}重要提醒：${NC}"
        echo "1. 请及时配置域名和SSL证书"
        echo "2. 修改默认密码和密钥"
        echo "3. 配置微信小程序服务器域名"
        echo "4. 定期备份数据库数据"
        
    else
        echo -e "${RED}❌ 部署过程中出现问题${NC}"
        echo ""
        echo "请检查以下日志："
        echo "- 后端日志: docker-compose -f docker-compose.lighthouse.yml logs backend"
        echo "- 数据库日志: docker-compose -f docker-compose.lighthouse.yml logs postgres"
        echo ""
        echo "常见解决方案："
        echo "1. 检查防火墙设置"
        echo "2. 确认端口未被占用"
        echo "3. 检查系统资源是否充足"
        exit 1
    fi
}

# 配置定时任务
setup_cron() {
    log_step "配置定时任务"
    
    # 创建备份脚本
    cat > /opt/targetmanage/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/targetmanage/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
docker exec targetmanage_postgres_lighthouse pg_dump -U postgres targetmanage > "$BACKUP_DIR/db_$DATE.sql"
gzip "$BACKUP_DIR/db_$DATE.sql"
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
echo "Backup completed: db_$DATE.sql.gz"
EOF
    
    chmod +x /opt/targetmanage/backup.sh
    
    # 添加定时任务
    (crontab -l 2>/dev/null; echo "0 3 * * * /opt/targetmanage/backup.sh") | crontab -
    
    log_info "定时备份任务已配置 ✓"
}

# 主函数
main() {
    # 检查root权限
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root用户运行此脚本"
        exit 1
    fi
    
    show_welcome
    collect_config
    check_environment
    initialize_server
    download_project
    configure_environment
    deploy_services
    setup_cron
    verify_deployment
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"
