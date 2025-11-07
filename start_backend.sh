#!/bin/bash
# 一键启动脚本 - 解决环境配置问题

set -e  # 遇到错误立即退出

echo "🚀 新闻推荐系统 - 启动脚本"
echo "================================"

# 进入backend目录
cd "$(dirname "$0")/backend"

# 检查.env文件
if [ ! -f .env ]; then
    echo "❌ 错误: .env文件不存在！"
    echo ""
    echo "解决方案："
    echo "1. 复制示例配置文件："
    echo "   cp .env.example .env"
    echo ""
    echo "2. 或者创建.env文件并添加以下内容："
    echo ""
    cat << 'EOF'
# 最小配置 - 复制以下内容到 backend/.env
SECRET_KEY=dev-secret-key-please-change-in-production-at-least-32-characters-long
DATABASE_URL=sqlite:///./news_recommendation.db
DEBUG=True
EOF
    echo ""

    # 询问是否自动创建
    read -p "是否自动创建.env文件？[y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✅ .env文件已创建"
    else
        echo "请手动创建.env文件后重新运行此脚本"
        exit 1
    fi
fi

echo "✅ .env文件存在"

# 检查虚拟环境
if [ ! -d "venv" ] && [ ! -d "../venv" ]; then
    echo "⚠️  虚拟环境不存在，正在创建..."
    python3 -m venv ../venv
    echo "✅ 虚拟环境已创建"
fi

# 激活虚拟环境
if [ -d "../venv" ]; then
    source ../venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "✅ 虚拟环境已激活"

# 检查依赖
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 安装依赖..."
    pip install -r requirements.txt
    echo "✅ 依赖安装完成"
fi

# 检查数据库
if [ ! -f "news_recommendation.db" ]; then
    echo "🗄️  初始化数据库..."
    if command -v alembic &> /dev/null; then
        alembic upgrade head
        echo "✅ 数据库初始化完成"
    else
        echo "⚠️  Alembic未安装，跳过数据库迁移"
    fi
fi

# 启动服务
echo ""
echo "🎉 启动后端服务..."
echo "================================"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
