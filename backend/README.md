# 智能目标管理系统 - 后端服务

## 🚀 快速启动

### 方法1：使用启动脚本（推荐）

#### Windows用户：
```bash
# 双击运行
start_dev.bat

# 或在命令行中运行
start_dev.bat
```

#### 所有用户：
```bash
python start_dev.py
```

### 方法2：手动启动

1. **安装依赖**：
```bash
pip install -r requirements.txt
```

2. **启动服务器**：
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📍 服务地址

- **API服务**：http://localhost:8000
- **API文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

## 🔧 环境要求

- Python 3.8+
- pip
- MySQL 5.7+

## 📦 主要依赖

- FastAPI - Web框架
- SQLAlchemy - ORM
- PyMySQL - MySQL驱动
- Redis - 缓存
- JWT - 认证

## 🐛 常见问题

### 1. 端口被占用
```bash
# 查看端口占用
netstat -ano | findstr :8000

# 使用其他端口
python -m uvicorn app.main:app --port 8001
```

### 2. 依赖安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 3. 数据库连接失败
检查 `app/config/settings.py` 中的数据库配置：
- 确保MySQL服务正在运行
- 检查数据库连接字符串
- 验证用户名和密码

## 📝 开发说明

- 服务启动后会自动重载代码变更
- 修改代码后保存即可看到效果
- 日志会显示在控制台中
- 使用 `Ctrl+C` 停止服务

## 🔗 相关链接

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [微信小程序开发文档](https://developers.weixin.qq.com/miniprogram/dev/)
