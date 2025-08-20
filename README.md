# 目标管理系统 (Target Management System)

一个提供目标管理、目标拆分、目标实现和实现跟踪的完整产品服务系统。

## 🚀 项目简介

本项目是一个全栈目标管理系统，包含：
- **微信小程序端**：面向C端用户的移动应用
- **PC后台管理**：面向管理员的Web管理后台
- **Python后端服务**：提供API服务和AI功能
- **AI服务集成**：图片识别和语音转文字功能

## 📁 项目结构

```
targetmanage/
├── backend/                    # Python后端服务 (FastAPI)
│   ├── app/                   # 应用核心代码
│   ├── requirements.txt       # Python依赖
│   ├── Dockerfile            # Docker配置
│   └── .env                  # 环境变量
├── wechat-miniprogram/        # 微信小程序
│   ├── pages/                # 小程序页面
│   ├── components/           # 组件
│   ├── utils/                # 工具函数
│   └── app.js               # 小程序入口
├── admin-frontend/            # PC后台管理 (Vue 3)
│   ├── src/                  # 源码目录
│   ├── package.json         # 前端依赖
│   └── vite.config.js       # Vite配置
├── shared/                    # 共享资源
├── docs/                      # 项目文档
├── docker/                    # Docker配置
├── scripts/                   # 脚本文件
└── docker-compose.yml        # Docker编排
```

## 🛠 技术栈

### 后端技术
- **框架**: FastAPI (Python 3.11+)
- **数据库**: PostgreSQL + Redis
- **ORM**: SQLAlchemy + Alembic
- **认证**: JWT + OAuth2
- **任务队列**: Celery + Redis
- **AI服务**: 百度OCR + 百度语音API

### 前端技术
- **微信小程序**: 原生小程序开发
- **PC管理后台**: Vue 3 + Vite + Element Plus
- **状态管理**: Pinia
- **HTTP客户端**: Axios
- **图表库**: ECharts

### 基础设施
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **监控**: Flower (Celery监控)

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (可选)

### 本地开发环境启动

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd targetmanage
   ```

2. **配置环境变量**
   ```bash
   cp backend/.env.example backend/.env
   # 编辑 backend/.env 文件，配置数据库和API密钥
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

4. **访问应用**
   - 后端API文档: http://localhost:8000/docs
   - PC管理后台: http://localhost:3000
   - Flower监控: http://localhost:5555

### 腾讯云轻量服务器部署（推荐小规模验证）

💰 **超低成本**: 仅需 ¥24/月，节省90%成本！

1. **15分钟一键部署**
   ```bash
   # 创建 Lighthouse 实例 (2核4GB)
   # SSH连接服务器后运行：
   curl -fsSL https://raw.githubusercontent.com/your-repo/targetmanage/main/scripts/lighthouse/one-click-deploy.sh | bash
   ```

2. **适用场景**
   - ✅ 业务验证阶段
   - ✅ 小规模用户测试
   - ✅ MVP产品演示
   - ✅ 个人项目部署

3. **详细指南**
   - 🚀 [Lighthouse 15分钟快速部署](docs/deployment/lighthouse/quick-start.md)
   - 📖 [Lighthouse 完整部署指南](docs/deployment/lighthouse/lighthouse-guide.md)

### 腾讯云CVM生产环境部署（大规模生产）

💪 **高性能**: 适合大规模生产环境

1. **准备腾讯云服务**
   - 云服务器CVM (4核8GB)
   - PostgreSQL数据库
   - Redis缓存
   - 对象存储COS
   - OCR和ASR服务

2. **一键部署**
   ```bash
   # 初始化服务器
   ./scripts/tencent-cloud/setup-server.sh
   
   # 配置环境变量
   cp backend/.env.example backend/.env.production
   # 编辑配置文件，填入腾讯云服务信息
   
   # 执行部署
   ./scripts/tencent-cloud/deploy.sh
   ```

3. **详细部署指南**
   - 📖 [腾讯云CVM部署详细文档](docs/deployment/tencent-cloud.md)
   - 🚀 [CVM快速部署指南](docs/deployment/quick-start-tencent.md)
   - 🗄️ [数据库配置指南](docs/deployment/database-setup.md)

### 手动启动

#### 1. 启动后端服务
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 启动PC管理后台
```bash
cd admin-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 3. 微信小程序开发
使用微信开发者工具导入 `wechat-miniprogram` 目录。

## 📖 功能特性

### 核心功能
- ✅ **用户认证**: 支持账号密码和微信登录
- ✅ **目标管理**: 创建、编辑、删除、分类管理目标
- ✅ **任务拆分**: 将大目标拆分为可执行的小任务
- ✅ **进度跟踪**: 实时记录和展示目标完成进度
- ✅ **数据分析**: 提供目标完成情况的统计分析

### AI增强功能
- 🔄 **图片识别**: 通过拍照自动识别和记录进度
- 🔄 **语音转文字**: 语音输入目标和任务描述
- 🔄 **智能提醒**: 基于用户行为的智能提醒系统

### 管理功能
- ✅ **用户管理**: 用户信息管理和权限控制
- ✅ **数据统计**: 系统使用情况和用户行为分析
- ✅ **内容审核**: 用户生成内容的审核管理

## 🔧 开发指南

### 后端开发
```bash
cd backend

# 创建数据库迁移
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head

# 运行测试
pytest

# 代码格式化
black app/
isort app/
```

### 前端开发
```bash
cd admin-frontend

# 代码检查
npm run lint

# 构建生产版本
npm run build
```

## 📚 API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

如有问题或建议，请通过以下方式联系：
- 项目Issues: [GitHub Issues](https://github.com/your-repo/targetmanage/issues)
- 邮箱: your-email@example.com

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！
