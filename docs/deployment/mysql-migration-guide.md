# 🚀 PostgreSQL到MySQL迁移指南

本文档介绍如何将目标管理系统从PostgreSQL迁移到MySQL数据库。

## 📋 迁移概述

### 为什么选择MySQL？

1. **成本优势**: 腾讯云MySQL价格更实惠
2. **生态支持**: MySQL生态更成熟，社区支持更好
3. **性能表现**: 对于中小型应用，MySQL性能完全满足需求
4. **运维简单**: MySQL运维相对简单，学习成本低

### 迁移内容

- 数据库连接配置
- 数据模型定义
- 数据库迁移文件
- 应用代码适配

## 🔧 迁移步骤

### 1. 环境准备

#### 安装MySQL驱动
```bash
# 卸载PostgreSQL驱动
pip uninstall psycopg2-binary asyncpg

# 安装MySQL驱动
pip install pymysql cryptography
```

#### 更新requirements.txt
```txt
# 替换
# psycopg2-binary==2.9.9
# asyncpg==0.29.0

# 为
pymysql==1.1.0
cryptography==41.0.7
```

### 2. 数据库配置更新

#### 更新数据库URL格式
```env
# 从
DATABASE_URL=postgresql://user:pass@host:5432/db

# 改为
DATABASE_URL=mysql+pymysql://user:pass@host:3306/db
```

#### 更新数据库连接配置
```python
# backend/app/config/database.py
engine = create_engine(
    settings.DATABASE_URL,
    # MySQL特定配置
    connect_args={
        "charset": "utf8mb4",
        "sql_mode": "STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO",
        "autocommit": False
    }
)
```

### 3. 数据模型更新

#### UUID字段类型变更
```python
# 从
from sqlalchemy.dialects.postgresql import UUID
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

# 改为
id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
```

#### 时间字段默认值
```python
# 从
created_at = Column(DateTime(timezone=True), server_default=func.now())

# 改为
created_at = Column(DateTime(timezone=True), server_default=func.text('CURRENT_TIMESTAMP'))
```

### 4. 数据库迁移文件更新

#### 数据类型映射
```python
# PostgreSQL -> MySQL
postgresql.UUID(as_uuid=True) -> sa.String(36)
func.now() -> func.text('CURRENT_TIMESTAMP')
func.text('now()') -> func.text('CURRENT_TIMESTAMP')
```

#### 索引和约束
```python
# MySQL索引语法
op.create_index('ix_users_wechat_id', 'users', ['wechat_id'], unique=True)

# 外键约束
sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
```

### 5. 应用代码适配

#### 类型注解更新
```python
# 从
from typing import Optional
import uuid

user_id: uuid.UUID
user_id: Optional[uuid.UUID] = None

# 改为
user_id: str
user_id: Optional[str] = None
```

#### UUID处理
```python
# 从
user.id = uuid.uuid4()

# 改为
user.id = str(uuid.uuid4())
```

## 🗄️ 数据库创建

### 1. 腾讯云MySQL实例创建

```bash
# 通过控制台创建
# 规格: 1核2GB，20GB存储
# 版本: MySQL 8.0
# 字符集: utf8mb4
```

### 2. 数据库初始化

```sql
-- 连接到MySQL实例
mysql -h your-host -u root -p

-- 创建数据库
CREATE DATABASE targetmanage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE targetmanage_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建应用用户
CREATE USER 'targetmanage_app'@'%' IDENTIFIED BY 'app_secure_password_123!';

-- 授予权限
GRANT ALL PRIVILEGES ON targetmanage.* TO 'targetmanage_app'@'%';
GRANT ALL PRIVILEGES ON targetmanage_test.* TO 'targetmanage_app'@'%';

-- 刷新权限
FLUSH PRIVILEGES;
```

### 3. 环境变量配置

```env
# .env
DATABASE_URL=mysql+pymysql://targetmanage_app:app_secure_password_123!@your-host:3306/targetmanage
DATABASE_TEST_URL=mysql+pymysql://targetmanage_app:app_secure_password_123!@your-host:3306/targetmanage_test
```

## 🚀 部署和测试

### 1. 运行数据库迁移

```bash
cd backend

# 初始化Alembic（如果需要）
alembic init alembic

# 创建迁移文件
alembic revision --autogenerate -m "Initial MySQL migration"

# 执行迁移
alembic upgrade head
```

### 2. 启动服务

```bash
# 使用快速启动脚本
python scripts/quick_start.py

# 或手动启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 验证功能

```bash
# 健康检查
curl http://localhost:8000/health

# API文档
open http://localhost:8000/docs

# 测试登录接口
curl -X POST "http://localhost:8000/api/auth/wechat-login" \
  -H "Content-Type: application/json" \
  -d '{"code":"test","userInfo":{"nickName":"测试用户"}}'
```

## 🔍 常见问题

### 1. 字符集问题

**问题**: 中文显示乱码
**解决**: 确保使用utf8mb4字符集

```sql
-- 检查字符集
SHOW VARIABLES LIKE 'character_set%';

-- 设置字符集
SET NAMES utf8mb4;
```

### 2. 时区问题

**问题**: 时间显示不正确
**解决**: 设置正确的时区

```sql
-- 设置时区
SET time_zone = '+08:00';

-- 或在连接字符串中指定
DATABASE_URL=mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4&time_zone=+08:00
```

### 3. 连接超时

**问题**: 数据库连接超时
**解决**: 调整连接池配置

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_recycle=3600,      # 1小时回收连接
    pool_pre_ping=True,     # 连接前ping检查
    connect_args={
        "connect_timeout": 10,
        "read_timeout": 30,
        "write_timeout": 30
    }
)
```

## 📊 性能优化

### 1. 索引优化

```sql
-- 为常用查询字段创建索引
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_login_attempts_created_at ON login_attempts(created_at);
```

### 2. 查询优化

```sql
-- 使用EXPLAIN分析查询
EXPLAIN SELECT * FROM users WHERE wechat_id = 'test';

-- 避免SELECT *
SELECT id, nickname, avatar FROM users WHERE wechat_id = 'test';
```

### 3. 连接池优化

```python
# 根据并发量调整连接池大小
pool_size=20,           # 连接池大小
max_overflow=30,        # 最大溢出连接数
pool_timeout=30,        # 获取连接超时时间
```

## 🔒 安全配置

### 1. 网络访问控制

```sql
-- 限制用户访问来源
CREATE USER 'targetmanage_app'@'10.0.0.0/8' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON targetmanage.* TO 'targetmanage_app'@'10.0.0.0/8';
```

### 2. SSL连接

```env
# 启用SSL连接
DATABASE_URL=mysql+pymysql://user:pass@host:3306/db?ssl_ca=/path/to/ca.pem
```

### 3. 定期备份

```bash
#!/bin/bash
# 自动备份脚本
mysqldump -h host -u user -p database > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 📈 监控和维护

### 1. 性能监控

```sql
-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

-- 查看连接数
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Max_used_connections';
```

### 2. 日志管理

```sql
-- 启用查询日志
SET GLOBAL general_log = 'ON';
SET GLOBAL log_output = 'TABLE';

-- 查看查询日志
SELECT * FROM mysql.general_log ORDER BY event_time DESC LIMIT 10;
```

## ✅ 迁移完成检查清单

- [ ] 数据库连接正常
- [ ] 所有表创建成功
- [ ] 数据迁移完成
- [ ] 应用启动正常
- [ ] 核心功能测试通过
- [ ] 性能测试达标
- [ ] 监控配置完成
- [ ] 备份策略建立

---

通过以上步骤，您就可以成功将目标管理系统从PostgreSQL迁移到MySQL了。如果在迁移过程中遇到问题，请参考常见问题部分或联系技术支持。
