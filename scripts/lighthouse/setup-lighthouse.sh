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
