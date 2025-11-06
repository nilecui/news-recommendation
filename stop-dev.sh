#!/bin/bash

# 开发环境停止脚本

echo "=== 停止开发环境服务 ==="

# 停止后端服务
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    echo "停止后端服务 (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "后端服务已停止"
    rm -f logs/backend.pid
else
    echo "未找到后端服务PID文件"
fi

# 停止前端服务
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    echo "停止前端服务 (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || echo "前端服务已停止"
    rm -f logs/frontend.pid
else
    echo "未找到前端服务PID文件"
fi

# 杀死可能残留的uvicorn进程
echo "清理残留进程..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

echo "=== 所有服务已停止 ==="