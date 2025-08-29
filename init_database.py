# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建用户管理相关的所有表
"""
import pymysql
import uuid
from datetime import datetime

def init_database():
    """初始化数据库"""
    try:
        print('开始初始化数据库...')
        
        # 连接数据库
        conn = pymysql.connect(
            host='sh-cynosdbmysql-grp-hocwbafo.sql.tencentcdb.com',
            port=26153,
            user='root',
            password='targetM123',
            database='targetmanage',
            charset='utf8mb4'
        )
        print('✅ 数据库连接成功')
        
        cursor = conn.cursor()
        
        # 1. 创建用户表
        create_user_table = """
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(36) PRIMARY KEY,
            wechat_id VARCHAR(100) UNIQUE NOT NULL,
            nickname VARCHAR(100) NOT NULL,
            avatar VARCHAR(500),
            phone_number VARCHAR(20),
            email VARCHAR(100),
            notification_enabled BOOLEAN DEFAULT TRUE,
            privacy_level VARCHAR(20) DEFAULT 'public',
            total_goals VARCHAR(10) DEFAULT '0',
            completed_goals VARCHAR(10) DEFAULT '0',
            streak_days VARCHAR(10) DEFAULT '0',
            is_verified BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            is_locked BOOLEAN DEFAULT FALSE,
            locked_until TIMESTAMP NULL,
            failed_login_attempts VARCHAR(10) DEFAULT '0',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            last_login_at TIMESTAMP NULL,
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at TIMESTAMP NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_user_table)
        print('✅ 用户表创建成功')
        
        # 2. 创建会话表
        create_session_table = """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            session_token VARCHAR(500) UNIQUE NOT NULL,
            refresh_token VARCHAR(500) UNIQUE NOT NULL,
            device_info TEXT,
            ip_address VARCHAR(45),
            user_agent TEXT,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_session_table)
        print('✅ 会话表创建成功')
        
        # 3. 创建登录尝试记录表
        create_login_attempt_table = """
        CREATE TABLE IF NOT EXISTS login_attempts (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36),
            ip_address VARCHAR(45) NOT NULL,
            user_agent TEXT,
            success BOOLEAN NOT NULL,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_login_attempt_table)
        print('✅ 登录尝试记录表创建成功')
        
        # 4. 创建目标表（基础结构）
        create_goals_table = """
        CREATE TABLE IF NOT EXISTS goals (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            category VARCHAR(50),
            priority VARCHAR(20) DEFAULT 'medium',
            status VARCHAR(20) DEFAULT 'active',
            target_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            completed_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_goals_table)
        print('✅ 目标表创建成功')
        
        # 5. 创建过程记录表
        create_process_record_table = """
        CREATE TABLE IF NOT EXISTS process_records (
            id VARCHAR(36) PRIMARY KEY,
            goal_id VARCHAR(36) NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            content TEXT NOT NULL,
            record_type VARCHAR(20) DEFAULT 'text',
            media_url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_process_record_table)
        print('✅ 过程记录表创建成功')
        
        # 提交所有更改
        conn.commit()
        print('✅ 所有表创建完成，更改已提交')
        
        # 验证表创建
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()
        print(' 现有数据库表:', [table[0] for table in tables])
        
        # 显示表结构
        for table in tables:
            table_name = table[0]
            print(f'\n 表 {table_name} 结构:')
            cursor.execute(f'DESCRIBE {table_name}')
            columns = cursor.fetchall()
            for col in columns:
                print(f'  - {col[0]}: {col[1]} ({col[2]})')
        
        print('\n✅ 数据库初始化完成！')
        
    except Exception as e:
        print(f'❌ 数据库初始化失败: {e}')
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()
            print('✅ 数据库连接已关闭')
    
    return True

if __name__ == "__main__":
    init_database()