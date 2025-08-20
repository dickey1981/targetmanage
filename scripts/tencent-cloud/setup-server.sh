#!/bin/bash
# 腾讯云服务器初始化脚本
# Tencent Cloud Server Setup Script

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
    log_info "更新系统包..."
    apt update && apt upgrade -y
    log_info "系统更新完成"
}

# 安装基础软件
install_basic_tools() {
    log_info "安装基础软件..."
    apt install -y \
        curl \
        wget \
        git \
        vim \
        htop \
        tree \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    log_info "基础软件安装完成"
}

# 安装Docker
install_docker() {
    log_info "安装Docker..."
    
    # 添加Docker官方GPG密钥
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # 添加Docker仓库
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 安装Docker
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io
    
    # 启动Docker服务
    systemctl start docker
    systemctl enable docker
    
    # 添加用户到docker组
    usermod -aG docker $USER
    
    log_info "Docker安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    log_info "安装Docker Compose..."
    
    # 下载Docker Compose
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 设置执行权限
    chmod +x /usr/local/bin/docker-compose
    
    # 创建软链接
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    log_info "Docker Compose安装完成"
}

# 安装Node.js
install_nodejs() {
    log_info "安装Node.js..."
    
    # 添加NodeSource仓库
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    
    # 安装Node.js
    apt install -y nodejs
    
    log_info "Node.js安装完成"
}

# 安装Python
install_python() {
    log_info "安装Python..."
    
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        libpq-dev \
        libffi-dev \
        libssl-dev
    
    # 升级pip
    pip3 install --upgrade pip
    
    log_info "Python安装完成"
}

# 安装Nginx
install_nginx() {
    log_info "安装Nginx..."
    
    apt install -y nginx
    
    # 启动Nginx
    systemctl start nginx
    systemctl enable nginx
    
    log_info "Nginx安装完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    # 启用ufw
    ufw --force enable
    
    # 允许SSH
    ufw allow ssh
    ufw allow 22/tcp
    
    # 允许HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # 允许应用端口（仅内网）
    ufw allow from 10.0.0.0/8 to any port 8000
    ufw allow from 172.16.0.0/12 to any port 8000
    ufw allow from 192.168.0.0/16 to any port 8000
    
    # 允许Redis端口（仅内网）
    ufw allow from 10.0.0.0/8 to any port 6379
    ufw allow from 172.16.0.0/12 to any port 6379
    ufw allow from 192.168.0.0/16 to any port 6379
    
    # 允许Flower监控（仅内网）
    ufw allow from 10.0.0.0/8 to any port 5555
    ufw allow from 172.16.0.0/12 to any port 5555
    ufw allow from 192.168.0.0/16 to any port 5555
    
    log_info "防火墙配置完成"
}

# 创建应用目录
create_app_directories() {
    log_info "创建应用目录..."
    
    # 创建应用根目录
    mkdir -p /opt/targetmanage
    
    # 创建日志目录
    mkdir -p /opt/targetmanage/logs
    mkdir -p /opt/targetmanage/logs/nginx
    
    # 创建上传目录
    mkdir -p /opt/targetmanage/uploads
    
    # 创建备份目录
    mkdir -p /opt/targetmanage/backups
    
    # 创建配置目录
    mkdir -p /opt/targetmanage/config
    
    # 设置权限
    chown -R $USER:$USER /opt/targetmanage
    chmod -R 755 /opt/targetmanage
    
    log_info "应用目录创建完成"
}

# 配置系统优化
optimize_system() {
    log_info "优化系统配置..."
    
    # 优化内核参数
    cat >> /etc/sysctl.conf << EOF

# 网络优化
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 65536 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr

# 文件描述符限制
fs.file-max = 65536

# 虚拟内存优化
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
EOF
    
    # 应用内核参数
    sysctl -p
    
    # 设置文件描述符限制
    cat >> /etc/security/limits.conf << EOF
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
EOF
    
    log_info "系统优化完成"
}

# 安装监控工具
install_monitoring() {
    log_info "安装监控工具..."
    
    # 安装htop, iotop, nethogs
    apt install -y htop iotop nethogs
    
    # 安装腾讯云监控插件
    wget -O - https://raw.githubusercontent.com/tencentcloud/tencentcloud-monitor-grafana-app/master/src/install.sh | bash
    
    log_info "监控工具安装完成"
}

# 配置定时任务
setup_cron_jobs() {
    log_info "配置定时任务..."
    
    # 创建定时备份脚本
    cat > /opt/targetmanage/backup.sh << 'EOF'
#!/bin/bash
# 数据库备份脚本

BACKUP_DIR="/opt/targetmanage/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/targetmanage_$DATE.sql"

# 执行备份
if [ ! -z "$DATABASE_URL" ]; then
    pg_dump "$DATABASE_URL" > "$BACKUP_FILE"
    gzip "$BACKUP_FILE"
    
    # 删除7天前的备份
    find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
fi
EOF
    
    chmod +x /opt/targetmanage/backup.sh
    
    # 添加到crontab（每天凌晨2点备份）
    (crontab -l 2>/dev/null; echo "0 2 * * * /opt/targetmanage/backup.sh") | crontab -
    
    log_info "定时任务配置完成"
}

# 主函数
main() {
    log_info "🚀 开始初始化腾讯云服务器..."
    
    # 检查是否为root用户
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root用户运行此脚本"
        exit 1
    fi
    
    # 执行初始化步骤
    update_system
    install_basic_tools
    install_docker
    install_docker_compose
    install_nodejs
    install_python
    install_nginx
    configure_firewall
    create_app_directories
    optimize_system
    install_monitoring
    setup_cron_jobs
    
    log_info "✅ 服务器初始化完成！"
    log_info "请重新登录以使用户组变更生效"
    log_info "然后可以运行部署脚本进行应用部署"
}

# 错误处理
trap 'log_error "初始化过程中发生错误"' ERR

# 执行主函数
main "$@"
