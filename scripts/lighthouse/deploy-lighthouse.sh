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
