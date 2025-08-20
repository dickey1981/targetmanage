# 腾讯云数据库配置指南

本文档介绍如何在腾讯云上配置PostgreSQL和Redis数据库，并在开发和生产环境中使用。

## 🗄️ PostgreSQL数据库配置

### 1. 创建TencentDB for PostgreSQL实例

#### 通过腾讯云控制台创建

1. 登录腾讯云控制台
2. 进入"云数据库 TencentDB for PostgreSQL"
3. 点击"新建"，配置实例：

**基础配置**：
- 计费模式：按量计费（测试）/ 包年包月（生产）
- 地域：北京/上海/广州（选择离服务器最近的）
- 可用区：选择与CVM相同的可用区
- 网络：VPC网络（与CVM在同一VPC）

**实例规格**：
- 版本：PostgreSQL 13.3
- 架构：基础版（开发）/ 高可用版（生产）
- 规格：
  - 开发环境：1核2GB，50GB存储
  - 生产环境：4核8GB，200GB存储

**设置信息**：
- 实例名称：targetmanage-db
- 管理员用户名：postgres
- 密码：设置强密码
- 端口：5432

#### 通过腾讯云CLI创建

```bash
# 安装腾讯云CLI
pip install tccli

# 配置CLI
tccli configure set secretId your-secret-id
tccli configure set secretKey your-secret-key
tccli configure set region ap-beijing

# 创建PostgreSQL实例
tccli postgres CreateInstances \
    --region ap-beijing \
    --zone ap-beijing-3 \
    --projectid 0 \
    --dbversion 13.3 \
    --storage 50 \
    --memory 2 \
    --instancecount 1 \
    --period 1 \
    --charset UTF8 \
    --adminname postgres \
    --adminpassword "YourStrongPassword123!" \
    --vpcid "vpc-xxxxxxxx" \
    --subnetid "subnet-xxxxxxxx"
```

### 2. 配置数据库安全

#### 设置安全组规则

```bash
# 创建安全组
tccli cvm CreateSecurityGroup \
    --groupname targetmanage-db-sg \
    --groupdescription "Target Management Database Security Group"

# 添加入站规则（仅允许应用服务器访问）
tccli cvm CreateSecurityGroupPolicies \
    --securitygroupid sg-xxxxxxxx \
    --securitygrouppolicyset '{
        "Ingress": [
            {
                "Protocol": "TCP",
                "Port": "5432",
                "CidrBlock": "10.0.0.0/8",
                "Action": "ACCEPT",
                "PolicyDescription": "Allow PostgreSQL access from VPC"
            }
        ]
    }'
```

#### 创建应用数据库和用户

连接到PostgreSQL实例：

```sql
-- 创建应用数据库
CREATE DATABASE targetmanage 
    WITH OWNER = postgres 
    ENCODING = 'UTF8' 
    LC_COLLATE = 'en_US.UTF-8' 
    LC_CTYPE = 'en_US.UTF-8';

CREATE DATABASE targetmanage_test 
    WITH OWNER = postgres 
    ENCODING = 'UTF8' 
    LC_COLLATE = 'en_US.UTF-8' 
    LC_CTYPE = 'en_US.UTF-8';

-- 创建应用用户
CREATE USER targetmanage_app WITH PASSWORD 'app_secure_password_123!';

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE targetmanage TO targetmanage_app;
GRANT ALL PRIVILEGES ON DATABASE targetmanage_test TO targetmanage_app;

-- 连接到应用数据库
\c targetmanage

-- 授予schema权限
GRANT ALL ON SCHEMA public TO targetmanage_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO targetmanage_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO targetmanage_app;

-- 设置默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO targetmanage_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO targetmanage_app;
```

### 3. 数据库连接配置

更新应用配置文件：

```env
# 生产环境数据库配置
DATABASE_URL=postgresql://targetmanage_app:app_secure_password_123!@your-db-host.postgres.tencentcdb.com:5432/targetmanage
DATABASE_TEST_URL=postgresql://targetmanage_app:app_secure_password_123!@your-db-host.postgres.tencentcdb.com:5432/targetmanage_test

# 连接池配置
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### 4. 数据库监控和备份

#### 自动备份配置

```bash
# 通过CLI配置自动备份
tccli postgres ModifyBackupConfig \
    --dbinstanceid postgres-xxxxxxxx \
    --minbackupstarttime "02:00:00" \
    --maxbackupstarttime "04:00:00" \
    --basebackupretentionperiod 7 \
    --backupperiod "monday,tuesday,wednesday,thursday,friday,saturday,sunday"
```

#### 手动备份脚本

```bash
#!/bin/bash
# backup-db.sh

DB_HOST="your-db-host.postgres.tencentcdb.com"
DB_NAME="targetmanage"
DB_USER="targetmanage_app"
DB_PASSWORD="app_secure_password_123!"
BACKUP_DIR="/opt/targetmanage/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
PGPASSWORD=$DB_PASSWORD pg_dump \
    -h $DB_HOST \
    -U $DB_USER \
    -d $DB_NAME \
    --verbose \
    --no-owner \
    --no-privileges \
    > "$BACKUP_DIR/targetmanage_$DATE.sql"

# 压缩备份文件
gzip "$BACKUP_DIR/targetmanage_$DATE.sql"

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Database backup completed: targetmanage_$DATE.sql.gz"
```

## 📊 Redis缓存配置

### 1. 创建TencentDB for Redis实例

#### 通过控制台创建

1. 进入"云数据库 TencentDB for Redis"
2. 点击"新建"，配置实例：

**基础配置**：
- 计费模式：按量计费
- 地域：与PostgreSQL相同
- 网络：VPC网络
- 可用区：与应用服务器相同

**实例规格**：
- 版本：Redis 6.0
- 架构：标准架构
- 规格：
  - 开发环境：1GB内存
  - 生产环境：4GB内存

#### 通过CLI创建

```bash
# 创建Redis实例
tccli redis CreateInstances \
    --zoneid 100003 \
    --typeid 7 \
    --memsize 1024 \
    --goodsnum 1 \
    --period 1 \
    --password "Redis_Password_123!" \
    --vpcid "vpc-xxxxxxxx" \
    --subnetid "subnet-xxxxxxxx" \
    --projectid 0
```

### 2. Redis配置和连接

```env
# Redis配置
REDIS_URL=redis://:Redis_Password_123!@your-redis-host.redis.tencentcdb.com:6379/0
REDIS_CACHE_TTL=3600

# Celery配置（使用Redis作为broker）
CELERY_BROKER_URL=redis://:Redis_Password_123!@your-redis-host.redis.tencentcdb.com:6379/1
CELERY_RESULT_BACKEND=redis://:Redis_Password_123!@your-redis-host.redis.tencentcdb.com:6379/2
```

### 3. Redis监控和优化

#### 性能监控

```python
# backend/app/utils/redis_monitor.py
import redis
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

class RedisMonitor:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
    
    def get_info(self):
        """获取Redis信息"""
        try:
            info = self.redis_client.info()
            return {
                "used_memory": info.get('used_memory_human'),
                "connected_clients": info.get('connected_clients'),
                "total_commands_processed": info.get('total_commands_processed'),
                "keyspace_hits": info.get('keyspace_hits'),
                "keyspace_misses": info.get('keyspace_misses')
            }
        except Exception as e:
            logger.error(f"Redis监控失败: {e}")
            return None
    
    def health_check(self):
        """Redis健康检查"""
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False
```

## 🔧 开发环境数据库配置

### 1. 本地开发使用云数据库

```env
# .env.development
# 直接连接腾讯云数据库（开发专用实例）
DATABASE_URL=postgresql://dev_user:dev_password@dev-db-host.postgres.tencentcdb.com:5432/targetmanage_dev
REDIS_URL=redis://:dev_redis_password@dev-redis-host.redis.tencentcdb.com:6379/0
```

### 2. 数据库迁移

```bash
# 安装依赖
pip install alembic psycopg2-binary

# 初始化Alembic（如果还没有）
alembic init alembic

# 创建迁移文件
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 3. 开发数据种子

```python
# scripts/seed_data.py
import asyncio
from sqlalchemy.orm import sessionmaker
from backend.app.config.database import engine
from backend.app.models.user import User
from backend.app.models.goal import Goal, GoalCategory, GoalPriority
from backend.app.utils.security import get_password_hash

async def create_seed_data():
    """创建种子数据"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 创建测试用户
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpassword"),
            nickname="测试用户",
            is_active=True
        )
        session.add(test_user)
        session.commit()
        
        # 创建测试目标
        test_goal = Goal(
            title="学习Python",
            description="深入学习Python编程",
            category=GoalCategory.STUDY,
            priority=GoalPriority.HIGH,
            user_id=test_user.id
        )
        session.add(test_goal)
        session.commit()
        
        print("种子数据创建成功")
        
    except Exception as e:
        session.rollback()
        print(f"创建种子数据失败: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(create_seed_data())
```

## 📈 性能优化

### 1. 数据库连接池优化

```python
# backend/app/config/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# 优化的数据库引擎配置
engine = create_engine(
    settings.DATABASE_URL,
    # 连接池配置
    poolclass=QueuePool,
    pool_size=20,           # 连接池大小
    max_overflow=30,        # 最大溢出连接数
    pool_timeout=30,        # 获取连接超时时间
    pool_recycle=3600,      # 连接回收时间
    pool_pre_ping=True,     # 连接前ping检查
    # 性能优化
    echo=False,             # 生产环境关闭SQL日志
    echo_pool=False,        # 关闭连接池日志
    # 连接参数
    connect_args={
        "connect_timeout": 10,
        "application_name": "targetmanage",
        "options": "-c timezone=Asia/Shanghai"
    }
)
```

### 2. Redis缓存策略

```python
# backend/app/utils/cache.py
import json
import redis
from typing import Any, Optional
from app.config.settings import settings

class CacheManager:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
        self.default_ttl = settings.REDIS_CACHE_TTL
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存"""
        try:
            ttl = ttl or self.default_ttl
            return self.redis.setex(
                key, 
                ttl, 
                json.dumps(value, default=str)
            )
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return bool(self.redis.delete(key))
        except Exception:
            return False
```

## 🔒 安全最佳实践

### 1. 数据库安全

- 使用强密码
- 限制网络访问（仅VPC内部）
- 定期更新密码
- 启用SSL连接
- 定期备份数据

### 2. 连接安全

```python
# 使用SSL连接
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Redis使用TLS
REDIS_URL=rediss://user:pass@host:6380/0
```

### 3. 权限控制

- 应用使用专用数据库用户
- 最小权限原则
- 定期审查权限
- 监控异常访问

---

通过以上配置，你的应用就可以安全、高效地使用腾讯云数据库服务了。
