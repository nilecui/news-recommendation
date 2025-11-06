#!/bin/bash

# 开发环境启动脚本

echo "=== 新闻推荐系统开发环境启动 ==="

# 检查Python环境
echo "1. 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 未安装，请先安装Python3"
    exit 1
fi

# 激活虚拟环境
echo "2. 激活Python虚拟环境..."
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "虚拟环境已激活"
else
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 安装后端依赖
echo "3. 安装后端依赖..."
cd backend
pip install -r requirements.txt

# 启动后端服务（在后台运行）
echo "4. 启动后端服务..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务已启动，PID: $BACKEND_PID"
cd ..

# 检查Node.js环境
echo "5. 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "Node.js 未安装，请先安装Node.js"
    kill $BACKEND_PID
    exit 1
fi

# 创建logs目录
mkdir -p logs

# 安装前端依赖
echo "6. 安装前端依赖..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

# 启动前端服务（在后台运行）
echo "7. 启动前端服务..."
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务已启动，PID: $FRONTEND_PID"
cd ..

# 保存PID到文件
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

echo ""
echo "=== 启动完成 ==="
echo "后端API: http://localhost:8000"
echo "前端应用: http://localhost:5173"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "查看日志:"
echo "  后端: tail -f logs/backend.log"
echo "  前端: tail -f logs/frontend.log"
echo ""
echo "停止服务:"
echo "  ./stop-dev.sh"
echo ""
echo "注意：此脚本假设PostgreSQL、Redis和Elasticsearch已在本机运行"
echo "如果没有，请使用Docker安装这些服务："
echo "docker run -d --name postgres -e POSTGRES_DB=news_recommendation -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15-alpine"
echo "docker run -d --name redis -p 6379:6379 redis:7-alpine"
echo "docker run -d --name elasticsearch -p 9200:9200 -e \"discovery.type=single-node\" -e \"xpack.security.enabled=false\" elasticsearch:8.11.0"