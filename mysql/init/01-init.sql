-- MySQL数据库初始化脚本
-- 创建应用数据库和用户

-- 创建应用数据库
CREATE DATABASE IF NOT EXISTS targetmanage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS targetmanage_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建应用用户
CREATE USER IF NOT EXISTS 'targetmanage_app'@'%' IDENTIFIED BY 'app_password';

-- 授予权限
GRANT ALL PRIVILEGES ON targetmanage.* TO 'targetmanage_app'@'%';
GRANT ALL PRIVILEGES ON targetmanage_test.* TO 'targetmanage_app'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 使用应用数据库
USE targetmanage;

-- 创建基础表结构（如果需要）
-- 这些表会通过Alembic迁移自动创建，这里只是示例

-- 显示数据库信息
SHOW DATABASES;
SHOW GRANTS FOR 'targetmanage_app'@'%';
