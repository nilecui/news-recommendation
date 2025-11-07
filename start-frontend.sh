#!/bin/bash
# 启动前端 Docker 容器脚本

echo "=========================================="
echo "启动前端 Docker 容器"
echo "=========================================="

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: docker-compose 未安装"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo "错误: Docker 未运行，请先启动 Docker"
    exit 1
fi

# 进入项目根目录（脚本所在目录的父目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 停止已存在的容器
echo "停止已存在的前端容器..."
docker-compose -f docker-compose-frontend.yml down 2>/dev/null

# 构建并启动前端容器
echo "构建并启动前端容器..."
docker-compose -f docker-compose-frontend.yml up --build -d

# 等待容器启动
echo "等待容器启动..."
sleep 5

# 检查容器状态
if docker ps | grep -q news_frontend; then
    echo ""
    echo "✅ 前端容器启动成功！"
    echo ""
    echo "前端访问地址: http://localhost:3000"
    echo "后端 API 地址: http://192.168.12.225:8311/api/v1"
    echo ""
    echo "查看日志: docker logs -f news_frontend"
    echo "停止容器: docker-compose -f docker-compose-frontend.yml down"
else
    echo ""
    echo "❌ 前端容器启动失败，请查看日志:"
    echo "docker logs news_frontend"
    exit 1
fi

