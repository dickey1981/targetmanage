# -*- coding: utf-8 -*-
import pymysql

print('开始检查数据库...')

try:
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
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    print(' 现有数据库表:', [table[0] for table in tables])
    
    conn.close()
    print('✅ 检查完成')
    
except Exception as e:
    print(f'❌ 错误: {e}')