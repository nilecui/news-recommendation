#!/bin/bash
# 重启后端服务脚本

echo "=========================================="
echo "重启后端服务"
echo "=========================================="

# 查找 uvicorn 进程
PID=$(ps aux | grep "uvicorn app.main:app" | grep -v grep | awk '{print $2}' | head -1)

if [ -z "$PID" ]; then
    echo "⚠️  未找到运行中的后端服务"
    echo ""
    echo "请手动启动后端服务："
    echo "  cd backend"
    echo "  source ../venv/bin/activate"
    echo "  uvicorn app.main:app --host 0.0.0.0 --port 8311 --reload"
    exit 1
fi

echo "找到后端进程 PID: $PID"
echo "正在停止后端服务..."

# 停止服务
kill $PID

# 等待进程停止
sleep 2

# 检查是否还在运行
if ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  进程仍在运行，强制停止..."
    kill -9 $PID
    sleep 1
fi

echo "✅ 后端服务已停止"
echo ""
echo "请手动重新启动后端服务："
echo "  cd backend"
echo "  source ../venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8311 --reload"
echo ""
echo "或者使用后台运行："
echo "  nohup uvicorn app.main:app --host 0.0.0.0 --port 8311 --reload > /tmp/uvicorn.log 2>&1 &"

