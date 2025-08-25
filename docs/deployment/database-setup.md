# 腾讯云数据库配置指南

本文档介绍如何在腾讯云上配置MySQL和Redis数据库，并在开发和生产环境中使用。

## 🗄️ MySQL数据库配置

### 1. 创建TencentDB for MySQL实例

#### 通过腾讯云控制台创建

1. 登录腾讯云控制台
2. 进入"云数据库 TencentDB for MySQL"
3. 点击"新建"，配置实例：

**基础配置**：
- 计费模式：按量计费（测试）/ 包年包月（生产）
- 地域：北京/上海/广州（选择离服务器最近的）
- 可用区：选择与CVM相同的可用区
- 网络：VPC网络（与CVM在同一VPC）

**实例规格**：
- 版本：MySQL 8.0（推荐）或 MySQL 5.7
- 架构：基础版（开发）/ 高可用版（生产）
- 规格：
  - 开发环境：1核2GB，20GB存储
  - 生产环境：2核4GB，100GB存储

**设置信息**：
- 实例名称：targetmanage-mysql
- 管理员用户名：root
- 密码：设置强密码
- 端口：3306

#### 通过腾讯云CLI创建

```bash
# 安装腾讯云CLI
pip install tccli

# 配置CLI
tccli configure set secretId your-secret-id
tccli configure set secretKey your-secret-key
tccli configure set region ap-beijing

# 创建MySQL实例
tccli cdb CreateDBInstance \
    --region ap-beijing \
    --zone ap-beijing-3 \
    --projectid 0 \
    --engineVersion 8.0 \
    --memory 2048 \
    --volume 20 \
    --instanceCount 1 \
    --period 1 \
    --charset utf8mb4 \
    --rootPassword "YourStrongPassword123!" \
    --vpcId "vpc-xxxxxxxx" \
    --subnetId "subnet-xxxxxxxx"
```

### 2. 配置数据库安全

#### 设置安全组规则

```bash
# 创建安全组
tccli cvm CreateSecurityGroup \
    --groupname targetmanage-mysql-sg \
    --groupdescription "Target Management MySQL Security Group"

# 添加入站规则（仅允许应用服务器访问）
tccli cvm CreateSecurityGroupPolicies \
    --securitygroupid sg-xxxxxxxx \
    --securitygrouppolicyset '{
        "Ingress": [
            {
                "Protocol": "TCP",
                "Port": "3306",
                "CidrBlock": "10.0.0.0/8",
                "Action": "ACCEPT",
                "PolicyDescription": "Allow MySQL access from VPC"
            }
        ]
    }'
```

#### 创建应用数据库和用户

连接到MySQL实例：

```sql
-- 创建应用数据库
CREATE DATABASE targetmanage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE targetmanage_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建应用用户
CREATE USER 'targetmanage_app'@'%' IDENTIFIED BY 'app_secure_password_123!';

-- 授予权限
GRANT ALL PRIVILEGES ON targetmanage.* TO 'targetmanage_app'@'%';
GRANT ALL PRIVILEGES ON targetmanage_test.* TO 'targetmanage_app'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 查看用户权限
SHOW GRANTS FOR 'targetmanage_app'@'%';
```

### 3. 数据库连接配置

更新应用配置文件：

```env
# 生产环境数据库配置
DATABASE_URL=mysql+pymysql://targetmanage_app:app_secure_password_123!@your-mysql-host.mysql.tencentcdb.com:3306/targetmanage
DATABASE_TEST_URL=mysql+pymysql://targetmanage_app:app_secure_password_123!@your-mysql-host.mysql.tencentcdb.com:3306/targetmanage_test

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
tccli cdb ModifyBackupConfig \
    --instanceId cdb-xxxxxxxx \
    --backupMethod "physical" \
    --backupTime "02:00-04:00" \
    --backupExpireDays 7
```

#### 手动备份脚本

```bash
#!/bin/bash
# backup-mysql.sh

DB_HOST="your-mysql-host.mysql.tencentcdb.com"
DB_NAME="targetmanage"
DB_USER="targetmanage_app"
DB_PASSWORD="app_secure_password_123!"
BACKUP_DIR="/opt/targetmanage/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
mysqldump \
    -h $DB_HOST \
    -u $DB_USER \
    -p$DB_PASSWORD \
    --single-transaction \
    --routines \
    --triggers \
    --hex-blob \
    $DB_NAME > "$BACKUP_DIR/targetmanage_$DATE.sql"

# 压缩备份文件
gzip "$BACKUP_DIR/targetmanage_$DATE.sql"

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "MySQL backup completed: targetmanage_$DATE.sql.gz"
```

## 📊 Redis缓存配置

### 1. 创建TencentDB for Redis实例

#### 通过控制台创建

1. 进入"云数据库 TencentDB for Redis"
2. 点击"新建"，配置实例：

**基础配置**：
- 计费模式：按量计费
- 地域：与MySQL相同
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
DATABASE_URL=mysql+pymysql://dev_user:dev_password@dev-mysql-host.mysql.tencentcdb.com:3306/targetmanage_dev
REDIS_URL=redis://:dev_redis_password@dev-redis-host.redis.tencentcdb.com:6379/0
```

### 2. 数据库迁移

```bash
# 安装依赖
pip install alembic pymysql

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
    # MySQL特定配置
    connect_args={
        "charset": "utf8mb4",
        "sql_mode": "STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO",
        "autocommit": False
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
                json.dumps(value, default=str, ensure_ascii=False)
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
# 使用SSL连接MySQL
DATABASE_URL=mysql+pymysql://user:pass@host:3306/db?ssl_ca=/path/to/ca.pem

# Redis使用TLS
REDIS_URL=rediss://user:pass@host:6380/0
```

### 3. 权限控制

- 应用使用专用数据库用户
- 最小权限原则
- 定期审查权限
- 监控异常访问

## 💰 成本优化建议

### 1. **开发环境**
- 使用按量计费，按需启动
- 选择最小规格：1核2GB，20GB存储
- 预估成本：约￥30-50/月

### 2. **生产环境**
- 使用包年包月，享受折扣
- 选择合适规格：2核4GB，100GB存储
- 预估成本：约￥100-150/月

### 3. **成本控制策略**
- 合理设置自动备份保留天数
- 监控数据库使用情况
- 根据业务需求调整规格
- 考虑使用预留实例获得更大折扣

## 🚀 快速部署步骤

### 1. **创建MySQL实例**
```bash
# 通过控制台创建MySQL实例
# 选择规格：1核2GB，20GB存储
# 设置密码：YourStrongPassword123!
```

### 2. **创建数据库和用户**
```sql
-- 连接到MySQL实例
mysql -h your-host -u root -p

-- 执行SQL脚本
CREATE DATABASE targetmanage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'targetmanage_app'@'%' IDENTIFIED BY 'app_secure_password_123!';
GRANT ALL PRIVILEGES ON targetmanage.* TO 'targetmanage_app'@'%';
FLUSH PRIVILEGES;
```

### 3. **更新应用配置**
```env
DATABASE_URL=mysql+pymysql://targetmanage_app:app_secure_password_123!@your-host:3306/targetmanage
```

### 4. **运行数据库迁移**
```bash
cd backend
alembic upgrade head
```

---

通过以上配置，你的应用就可以安全、高效地使用腾讯云MySQL数据库服务了。MySQL相比PostgreSQL在成本上更有优势，同时保持了良好的性能和稳定性。
