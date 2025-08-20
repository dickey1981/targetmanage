#!/bin/bash
# 腾讯云部署脚本
# Tencent Cloud Deployment Script

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必要的工具
check_requirements() {
    log_info "检查部署环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        log_error "Git 未安装，请先安装 Git"
        exit 1
    fi
    
    log_info "环境检查通过"
}

# 更新代码
update_code() {
    log_info "更新代码..."
    git fetch origin
    git reset --hard origin/main
    log_info "代码更新完成"
}

# 备份数据库
backup_database() {
    log_info "备份数据库..."
    
    # 创建备份目录
    mkdir -p backups
    
    # 生成备份文件名
    BACKUP_FILE="backups/targetmanage_$(date +%Y%m%d_%H%M%S).sql"
    
    # 执行备份
    if [ ! -z "$DATABASE_URL" ]; then
        pg_dump "$DATABASE_URL" > "$BACKUP_FILE"
        log_info "数据库备份完成: $BACKUP_FILE"
    else
        log_warn "未配置数据库URL，跳过备份"
    fi
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."
    
    # 构建后端镜像
    docker-compose -f docker-compose.tencent.yml build backend
    
    # 构建前端镜像
    docker-compose -f docker-compose.tencent.yml build frontend
    
    log_info "镜像构建完成"
}

# 数据库迁移
migrate_database() {
    log_info "执行数据库迁移..."
    
    # 停止当前服务（如果存在）
    docker-compose -f docker-compose.tencent.yml down || true
    
    # 启动数据库依赖服务
    docker-compose -f docker-compose.tencent.yml up -d postgres redis || true
    
    # 等待数据库启动
    sleep 10
    
    # 执行迁移
    docker-compose -f docker-compose.tencent.yml run --rm backend alembic upgrade head
    
    log_info "数据库迁移完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 停止所有服务
    docker-compose -f docker-compose.tencent.yml down
    
    # 启动所有服务
    docker-compose -f docker-compose.tencent.yml up -d
    
    log_info "服务启动完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 等待服务启动
    sleep 30
    
    # 检查后端服务
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "后端服务健康检查通过"
    else
        log_error "后端服务健康检查失败"
        return 1
    fi
    
    # 检查前端服务
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_info "前端服务健康检查通过"
    else
        log_error "前端服务健康检查失败"
        return 1
    fi
    
    log_info "所有服务健康检查通过"
}

# 清理旧镜像
cleanup() {
    log_info "清理旧镜像..."
    
    # 删除无用的镜像
    docker image prune -f
    
    # 删除无用的容器
    docker container prune -f
    
    # 删除无用的网络
    docker network prune -f
    
    log_info "清理完成"
}

# 显示服务状态
show_status() {
    log_info "服务状态："
    docker-compose -f docker-compose.tencent.yml ps
    
    log_info "系统资源使用情况："
    docker stats --no-stream
}

# 主函数
main() {
    log_info "🚀 开始部署目标管理系统到腾讯云..."
    
    # 检查环境
    check_requirements
    
    # 更新代码
    update_code
    
    # 备份数据库
    backup_database
    
    # 构建镜像
    build_images
    
    # 数据库迁移
    migrate_database
    
    # 启动服务
    start_services
    
    # 健康检查
    if health_check; then
        log_info "✅ 部署成功！"
    else
        log_error "❌ 部署失败，请检查日志"
        exit 1
    fi
    
    # 清理旧资源
    cleanup
    
    # 显示状态
    show_status
    
    log_info "🎉 部署完成！"
    log_info "后端服务: http://localhost:8000"
    log_info "前端服务: http://localhost:3000"
    log_info "API文档: http://localhost:8000/docs"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"' ERR

# 执行主函数
main "$@"
