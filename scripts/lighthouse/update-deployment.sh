#!/bin/bash
# Lighthouse 更新部署脚本
# 用于更新现有部署到最新版本

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
    echo "    目标管理系统 Lighthouse 更新部署脚本"
    echo "=================================================="
    echo -e "${NC}"
    echo "本脚本将完成以下操作："
    echo "1. 备份当前部署"
    echo "2. 拉取最新代码"
    echo "3. 重新构建镜像"
    echo "4. 更新服务"
    echo "5. 验证部署结果"
    echo ""
    echo -e "${YELLOW}预计用时: 5-10分钟${NC}"
    echo ""
    read -p "按 Enter 键开始更新，或 Ctrl+C 取消..."
}

# 检查当前部署状态
check_current_deployment() {
    log_step "检查当前部署状态"
    
    # 检查是否在正确的目录
    if [ ! -f "docker-compose.lighthouse.yml" ]; then
        log_error "未找到 docker-compose.lighthouse.yml 文件"
        log_error "请确保在项目根目录运行此脚本"
        exit 1
    fi
    
    # 检查Docker服务状态
    if ! docker-compose -f docker-compose.lighthouse.yml ps | grep -q "Up"; then
        log_warn "当前没有运行的服务，将进行全新部署"
        return 1
    fi
    
    log_info "当前部署状态正常 ✓"
    return 0
}

# 备份当前部署
backup_current_deployment() {
    log_step "备份当前部署"
    
    # 创建备份目录
    BACKUP_DIR="/opt/targetmanage/backups/update_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份数据库
    log_info "备份数据库..."
    docker exec targetmanage_postgres_lighthouse pg_dump -U postgres targetmanage > "$BACKUP_DIR/database.sql"
    
    # 备份配置文件
    log_info "备份配置文件..."
    cp -r backend/.env "$BACKUP_DIR/" 2>/dev/null || true
    cp .env "$BACKUP_DIR/" 2>/dev/null || true
    
    # 备份上传文件
    log_info "备份上传文件..."
    cp -r uploads "$BACKUP_DIR/" 2>/dev/null || true
    
    log_info "备份完成: $BACKUP_DIR ✓"
}

# 拉取最新代码
pull_latest_code() {
    log_step "拉取最新代码"
    
    # 检查git状态
    if [ -d ".git" ]; then
        log_info "拉取最新代码..."
        git fetch origin
        git reset --hard origin/main
        log_info "代码更新完成 ✓"
    else
        log_warn "当前目录不是git仓库，跳过代码更新"
    fi
}

# 更新环境配置
update_environment() {
    log_step "更新环境配置"
    
    # 检查环境变量文件
    if [ ! -f ".env" ]; then
        log_warn "未找到 .env 文件，请手动配置环境变量"
        return 1
    fi
    
    # 检查后端环境变量
    if [ ! -f "backend/.env" ]; then
        log_warn "未找到 backend/.env 文件，请手动配置"
        return 1
    fi
    
    log_info "环境配置检查完成 ✓"
}

# 重新构建和部署
rebuild_and_deploy() {
    log_step "重新构建和部署"
    
    # 停止服务
    log_info "停止当前服务..."
    docker-compose -f docker-compose.lighthouse.yml down
    
    # 清理旧镜像
    log_info "清理旧镜像..."
    docker system prune -f
    
    # 重新构建镜像
    log_info "重新构建镜像..."
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
    echo "              更新完成！"
    echo -e "==================================================${NC}"
    echo ""
    
    if [ "$BACKEND_OK" = true ] && [ "$FRONTEND_OK" = true ] && [ "$DATABASE_OK" = true ]; then
        echo -e "${GREEN}🎉 所有服务更新成功！${NC}"
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
        
    else
        echo -e "${RED}❌ 更新过程中出现问题${NC}"
        echo ""
        echo "请检查以下日志："
        echo "- 后端日志: docker-compose -f docker-compose.lighthouse.yml logs backend"
        echo "- 数据库日志: docker-compose -f docker-compose.lighthouse.yml logs postgres"
        echo ""
        echo "如需回滚，请使用备份文件恢复"
        exit 1
    fi
}

# 主函数
main() {
    # 检查root权限
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root用户运行此脚本"
        exit 1
    fi
    
    show_welcome
    
    # 检查当前部署
    if check_current_deployment; then
        backup_current_deployment
    fi
    
    pull_latest_code
    update_environment
    rebuild_and_deploy
    verify_deployment
}

# 错误处理
trap 'log_error "更新过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"
