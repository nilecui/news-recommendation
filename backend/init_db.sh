#!/bin/bash
# 数据库初始化脚本

set -e

echo "🚀 开始初始化数据库..."

# 数据库连接信息
DB_HOST="192.168.12.222"
DB_PORT="5432"
DB_USER="root"
DB_PASSWORD="root"
DB_NAME="recommandation"

# 检查是否安装了 psql
if ! command -v psql &> /dev/null; then
    echo "⚠️  psql 未安装，尝试使用 Python 创建数据库..."
    
    # 使用 Python 创建数据库
    python3 << PYTHON_EOF
import sys
try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    # 连接到 PostgreSQL 服务器（使用默认的 postgres 数据库）
    conn = psycopg2.connect(
        host="${DB_HOST}",
        port=${DB_PORT},
        user="${DB_USER}",
        password="${DB_PASSWORD}",
        database="postgres"
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
        cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
        print(f"✅ 数据库 '{DB_NAME}' 创建成功")
    
    cursor.close()
    conn.close()
    
except ImportError:
    print("❌ psycopg2 未安装，请先安装: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"❌ 数据库操作失败: {e}")
    sys.exit(1)
PYTHON_EOF

else
    # 使用 psql 创建数据库
    echo "📝 使用 psql 创建数据库..."
    PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -c "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" | grep -q 1 && \
        echo "✅ 数据库 '${DB_NAME}' 已存在" || \
        PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres -c "CREATE DATABASE \"${DB_NAME}\"" && \
        echo "✅ 数据库 '${DB_NAME}' 创建成功"
fi

echo ""
echo "📊 运行数据库迁移..."
cd "$(dirname "$0")"

# 检查虚拟环境
if [ -f "../venv/bin/activate" ]; then
    source ../venv/bin/activate
fi

# 检查是否有迁移文件
if [ -z "$(ls -A alembic/versions/*.py 2>/dev/null | grep -v __init__)" ]; then
    echo "📝 创建初始迁移..."
    alembic revision --autogenerate -m "Initial migration"
fi

# 运行迁移
echo "🔄 执行数据库迁移..."
alembic upgrade head

echo ""
echo "✅ 数据库初始化完成！"
echo "📝 数据库名称: ${DB_NAME}"
echo "🌐 数据库地址: ${DB_HOST}:${DB_PORT}"

