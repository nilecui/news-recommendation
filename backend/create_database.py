#!/usr/bin/env python3
"""
创建数据库脚本
"""
import sys

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("❌ 请先安装 psycopg2: pip install psycopg2-binary")
    sys.exit(1)

# 数据库连接信息
DB_HOST = "192.168.12.222"
DB_PORT = 5432
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "recommandation"

def create_database():
    """创建数据库"""
    try:
        # 连接到 PostgreSQL 服务器（使用默认的 postgres 数据库）
        print(f"📡 连接到 PostgreSQL 服务器 {DB_HOST}:{DB_PORT}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"  # 连接到默认数据库
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"✅ 数据库 '{DB_NAME}' 已存在")
        else:
            # 创建数据库
            print(f"📝 创建数据库 '{DB_NAME}'...")
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"✅ 数据库 '{DB_NAME}' 创建成功")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ 数据库操作失败: {e}")
        return False

if __name__ == "__main__":
    if create_database():
        print("\n✅ 数据库创建完成！")
        sys.exit(0)
    else:
        sys.exit(1)

