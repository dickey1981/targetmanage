# 目标管理项目目录结构规划

## 项目整体架构
```
targetmanage/
├── backend/                    # Python后端服务
├── wechat-miniprogram/        # 微信小程序
├── admin-frontend/            # PC后台管理前端
├── shared/                    # 共享资源和配置
├── docs/                      # 项目文档
├── scripts/                   # 部署和工具脚本
├── docker/                    # Docker配置文件
├── README.md                  # 项目说明
├── .gitignore                # Git忽略文件
└── docker-compose.yml        # Docker编排文件
```

## 1. 后端服务 (backend/)
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI应用入口
│   ├── config/                # 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py        # 应用配置
│   │   └── database.py        # 数据库配置
│   ├── api/                   # API路由
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # 认证相关API
│   │   │   ├── users.py       # 用户管理API
│   │   │   ├── goals.py       # 目标管理API
│   │   │   ├── tasks.py       # 任务管理API
│   │   │   ├── progress.py    # 进度跟踪API
│   │   │   ├── ai_services.py # AI服务API (图片识别、语音转文字)
│   │   │   └── admin.py       # 后台管理API
│   │   └── dependencies.py    # API依赖
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py           # 用户模型
│   │   ├── goal.py           # 目标模型
│   │   ├── task.py           # 任务模型
│   │   ├── progress.py       # 进度模型
│   │   └── base.py           # 基础模型
│   ├── schemas/               # Pydantic模式
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── goal.py
│   │   ├── task.py
│   │   └── progress.py
│   ├── services/              # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── auth_service.py    # 认证服务
│   │   ├── user_service.py    # 用户服务
│   │   ├── goal_service.py    # 目标服务
│   │   ├── task_service.py    # 任务服务
│   │   ├── progress_service.py # 进度服务
│   │   ├── wechat_service.py  # 微信服务集成
│   │   ├── ocr_service.py     # 图片识别服务
│   │   └── speech_service.py  # 语音转文字服务
│   ├── utils/                 # 工具函数
│   │   ├── __init__.py
│   │   ├── security.py        # 安全相关工具
│   │   ├── validators.py      # 验证器
│   │   ├── file_handler.py    # 文件处理
│   │   └── common.py          # 通用工具
│   ├── middleware/            # 中间件
│   │   ├── __init__.py
│   │   ├── cors.py           # CORS中间件
│   │   ├── auth.py           # 认证中间件
│   │   └── logging.py        # 日志中间件
│   └── tests/                 # 测试代码
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_goals.py
│       └── test_services.py
├── requirements.txt           # Python依赖
├── requirements-dev.txt       # 开发依赖
├── alembic/                   # 数据库迁移
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── Dockerfile                 # Docker配置
├── .env.example              # 环境变量示例
└── pytest.ini               # 测试配置
```

## 2. 微信小程序 (wechat-miniprogram/)
```
wechat-miniprogram/
├── pages/                     # 页面
│   ├── index/                # 首页
│   │   ├── index.js
│   │   ├── index.json
│   │   ├── index.wxml
│   │   └── index.wxss
│   ├── goals/                # 目标管理
│   │   ├── list/             # 目标列表
│   │   ├── detail/           # 目标详情
│   │   ├── create/           # 创建目标
│   │   └── edit/             # 编辑目标
│   ├── tasks/                # 任务管理
│   │   ├── list/
│   │   ├── detail/
│   │   └── create/
│   ├── progress/             # 进度跟踪
│   │   ├── overview/         # 进度概览
│   │   ├── detail/           # 详细进度
│   │   └── report/           # 进度报告
│   ├── profile/              # 个人中心
│   │   ├── index/
│   │   ├── settings/
│   │   └── about/
│   └── auth/                 # 认证页面
│       ├── login/
│       └── register/
├── components/               # 组件
│   ├── goal-card/           # 目标卡片
│   ├── task-item/           # 任务项
│   ├── progress-chart/      # 进度图表
│   ├── voice-input/         # 语音输入组件
│   ├── image-upload/        # 图片上传组件
│   └── common/              # 通用组件
├── utils/                   # 工具函数
│   ├── request.js           # 网络请求
│   ├── auth.js              # 认证工具
│   ├── storage.js           # 本地存储
│   ├── date.js              # 日期处理
│   └── common.js            # 通用工具
├── services/                # 服务层
│   ├── api.js               # API接口
│   ├── goal.js              # 目标服务
│   ├── task.js              # 任务服务
│   ├── progress.js          # 进度服务
│   └── upload.js            # 上传服务
├── styles/                  # 样式
│   ├── common.wxss          # 通用样式
│   ├── variables.wxss       # 变量定义
│   └── mixins.wxss          # 混合样式
├── images/                  # 图片资源
├── app.js                   # 应用入口
├── app.json                 # 应用配置
├── app.wxss                 # 全局样式
├── sitemap.json             # 站点地图
└── project.config.json      # 项目配置
```

## 3. PC后台管理前端 (admin-frontend/)
```
admin-frontend/
├── public/                  # 静态资源
│   ├── index.html
│   ├── favicon.ico
│   └── logo.png
├── src/
│   ├── main.js             # 应用入口
│   ├── App.vue             # 根组件
│   ├── router/             # 路由配置
│   │   ├── index.js
│   │   └── modules/
│   ├── store/              # 状态管理 (Pinia)
│   │   ├── index.js
│   │   ├── modules/
│   │   │   ├── auth.js
│   │   │   ├── user.js
│   │   │   ├── goal.js
│   │   │   └── dashboard.js
│   │   └── plugins/
│   ├── views/              # 页面视图
│   │   ├── Dashboard/      # 仪表板
│   │   ├── Users/          # 用户管理
│   │   │   ├── UserList.vue
│   │   │   ├── UserDetail.vue
│   │   │   └── UserEdit.vue
│   │   ├── Goals/          # 目标管理
│   │   │   ├── GoalList.vue
│   │   │   ├── GoalDetail.vue
│   │   │   └── GoalAnalytics.vue
│   │   ├── Tasks/          # 任务管理
│   │   ├── Progress/       # 进度管理
│   │   ├── Analytics/      # 数据分析
│   │   ├── Settings/       # 系统设置
│   │   └── Auth/           # 认证页面
│   ├── components/         # 组件
│   │   ├── Layout/         # 布局组件
│   │   │   ├── Header.vue
│   │   │   ├── Sidebar.vue
│   │   │   └── Footer.vue
│   │   ├── Charts/         # 图表组件
│   │   ├── Tables/         # 表格组件
│   │   ├── Forms/          # 表单组件
│   │   └── Common/         # 通用组件
│   ├── api/                # API接口
│   │   ├── index.js        # API配置
│   │   ├── auth.js
│   │   ├── users.js
│   │   ├── goals.js
│   │   └── analytics.js
│   ├── utils/              # 工具函数
│   │   ├── request.js      # 请求拦截
│   │   ├── auth.js         # 认证工具
│   │   ├── validators.js   # 表单验证
│   │   └── helpers.js      # 辅助函数
│   ├── styles/             # 样式
│   │   ├── main.scss       # 主样式
│   │   ├── variables.scss  # 变量
│   │   └── components/     # 组件样式
│   └── assets/             # 静态资源
│       ├── images/
│       ├── icons/
│       └── fonts/
├── package.json            # 依赖配置
├── vite.config.js          # Vite配置
├── tailwind.config.js      # Tailwind配置
├── .env.development        # 开发环境变量
├── .env.production         # 生产环境变量
└── Dockerfile              # Docker配置
```

## 4. 共享资源 (shared/)
```
shared/
├── constants/              # 常量定义
│   ├── api.js             # API常量
│   ├── status.js          # 状态常量
│   └── messages.js        # 消息常量
├── types/                 # 类型定义
│   ├── user.ts
│   ├── goal.ts
│   └── task.ts
├── utils/                 # 共享工具
│   ├── date.js
│   ├── validation.js
│   └── formatters.js
└── schemas/               # 数据模式
    ├── api-schemas.json
    └── validation-schemas.json
```

## 5. 文档 (docs/)
```
docs/
├── api/                   # API文档
│   ├── README.md
│   ├── authentication.md
│   ├── goals.md
│   └── tasks.md
├── deployment/            # 部署文档
│   ├── docker.md
│   ├── production.md
│   └── monitoring.md
├── development/           # 开发文档
│   ├── setup.md
│   ├── contributing.md
│   └── testing.md
└── architecture/          # 架构文档
    ├── overview.md
    ├── database.md
    └── security.md
```

## 6. 脚本和配置 (scripts/, docker/)
```
scripts/
├── setup.sh              # 环境搭建脚本
├── deploy.sh              # 部署脚本
├── backup.sh              # 备份脚本
└── test.sh                # 测试脚本

docker/
├── backend/
│   └── Dockerfile
├── frontend/
│   └── Dockerfile
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf
└── docker-compose.yml
```

## 主要技术栈选择

### 后端 (Python)
- **框架**: FastAPI (高性能、自动文档生成)
- **数据库**: PostgreSQL + Redis (缓存)
- **ORM**: SQLAlchemy
- **认证**: JWT + OAuth2
- **图片识别**: 百度OCR API / 腾讯云OCR
- **语音转文字**: 百度语音API / 腾讯云语音
- **任务队列**: Celery + Redis
- **部署**: Docker + Nginx

### 微信小程序
- **框架**: 原生微信小程序
- **状态管理**: 小程序自带状态管理
- **UI组件**: WeUI / Vant Weapp
- **图表**: ECharts for 微信小程序

### PC后台管理
- **框架**: Vue 3 + Vite
- **UI组件**: Element Plus / Ant Design Vue
- **状态管理**: Pinia
- **图表**: ECharts / Chart.js
- **样式**: Tailwind CSS + SCSS
