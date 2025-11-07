#!/usr/bin/env python3
"""
数据库初始化脚本 - 使用 SQLAlchemy 创建所有表
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from sqlalchemy import create_engine, text
    from app.config.database import Base, engine
    from app.models import User, News, NewsCategory, UserBehavior, UserProfile, UserPreference
    from app.config.settings import settings
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)


def create_database_if_not_exists():
    """如果数据库不存在则创建"""
    try:
        # 从 DATABASE_URL 解析数据库名
        db_url = settings.DATABASE_URL
        if db_url.startswith('postgresql://'):
            # 解析数据库名
            parts = db_url.split('/')
            db_name = parts[-1].split('?')[0]
            
            # 连接到 postgres 数据库
            admin_url = '/'.join(parts[:-1]) + '/postgres'
            
            import psycopg2
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            
            # 解析连接信息
            conn_str = admin_url.replace('postgresql://', '')
            if '@' in conn_str:
                auth, host_part = conn_str.split('@')
                user, password = auth.split(':')
                if ':' in host_part:
                    host, port = host_part.split(':')
                else:
                    host = host_part
                    port = 5432
            else:
                print("无法解析数据库连接信息")
                return False
            
            print(f"📡 连接到 PostgreSQL 服务器 {host}:{port}...")
            conn = psycopg2.connect(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database="postgres"
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = conn.cursor()
            
            # 检查数据库是否存在
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            exists = cursor.fetchone()
            
            if exists:
                print(f"✅ 数据库 '{db_name}' 已存在")
            else:
                print(f"📝 创建数据库 '{db_name}'...")
                cursor.execute(f'CREATE DATABASE "{db_name}"')
                print(f"✅ 数据库 '{db_name}' 创建成功")
            
            cursor.close()
            conn.close()
            return True
            
    except Exception as e:
        print(f"⚠️  数据库创建检查失败: {e}")
        print("继续尝试创建表结构...")
        return False


def create_tables():
    """创建所有表"""
    try:
        print("\n📊 开始创建数据库表结构...")
        print(f"数据库连接: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'N/A'}")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        print("\n✅ 所有表创建成功！")
        
        # 显示创建的表
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY tablename
            """))
            tables = [row[0] for row in result]
            
            print("\n📋 已创建的表:")
            for table in tables:
                print(f"   - {table}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 创建表失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def insert_initial_data():
    """插入初始数据"""
    try:
        print("\n📝 插入初始数据...")
        
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # 插入默认新闻分类
            categories = [
                {'name': 'technology', 'name_zh': '科技', 'description': '科技类新闻', 'sort_order': 1},
                {'name': 'politics', 'name_zh': '政治', 'description': '政治类新闻', 'sort_order': 2},
                {'name': 'economy', 'name_zh': '经济', 'description': '经济类新闻', 'sort_order': 3},
                {'name': 'sports', 'name_zh': '体育', 'description': '体育类新闻', 'sort_order': 4},
                {'name': 'entertainment', 'name_zh': '娱乐', 'description': '娱乐类新闻', 'sort_order': 5},
                {'name': 'health', 'name_zh': '健康', 'description': '健康类新闻', 'sort_order': 6},
                {'name': 'education', 'name_zh': '教育', 'description': '教育类新闻', 'sort_order': 7},
                {'name': 'society', 'name_zh': '社会', 'description': '社会类新闻', 'sort_order': 8},
            ]
            
            for cat_data in categories:
                existing = db.query(NewsCategory).filter(NewsCategory.name == cat_data['name']).first()
                if not existing:
                    category = NewsCategory(**cat_data)
                    db.add(category)
            
            db.commit()
            print("✅ 初始数据插入成功！")
            
        except Exception as e:
            db.rollback()
            print(f"⚠️  插入初始数据失败: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"⚠️  插入初始数据时出错: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 新闻推荐系统数据库初始化")
    print("=" * 60)
    
    # 1. 创建数据库（如果需要）
    create_database_if_not_exists()
    
    # 2. 创建所有表
    if not create_tables():
        print("\n❌ 数据库初始化失败！")
        sys.exit(1)
    
    # 3. 插入初始数据
    insert_initial_data()
    
    print("\n" + "=" * 60)
    print("✅ 数据库初始化完成！")
    print("=" * 60)
    print("\n现在可以启动应用了:")
    print("  uvicorn app.main:app --host 0.0.0.0 --port 8311 --reload")


if __name__ == "__main__":
    main()

