# 快速启动指南

## 方案1：使用简化脚本（推荐）

如果遇到Docker权限问题，可以使用我们的简化启动脚本：

### 步骤1：启动数据库服务（可选）

如果没有安装PostgreSQL、Redis和Elasticsearch，可以用Docker启动它们：

```bash
# 启动PostgreSQL
docker run -d --name news_postgres \
  -e POSTGRES_DB=news_recommendation \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine

# 启动Redis
docker run -d --name news_redis \
  -p 6379:6379 \
  redis:7-alpine

# 启动Elasticsearch
docker run -d --name news_elasticsearch \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -p 9200:9200 \
  elasticsearch:8.11.0
```

### 步骤2：启动应用程序

```bash
# 给脚本执行权限
chmod +x start-dev.sh stop-dev.sh

# 启动服务
./start-dev.sh
```

这将：
- 激活Python虚拟环境
- 安装后端依赖
- 启动FastAPI后端（端口8000）
- 安装前端依赖
- 启动React前端（端口5173）

### 访问应用

- 前端应用: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 停止服务

```bash
./stop-dev.sh
```

## 方案2：手动启动

### 启动后端

```bash
cd backend

# 激活虚拟环境
source ../venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 启动前端（新终端）

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 环境变量配置

复制并编辑环境变量文件：

```bash
# 后端环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库连接等

# 前端环境变量
cp frontend/.env.example frontend/.env.local
# 编辑 frontend/.env.local 文件
```

## 验证安装

1. 访问 http://localhost:5173 查看前端
2. 访问 http://localhost:8000/docs 查看API文档
3. 尝试注册新用户测试认证功能

## 故障排除

### Docker权限问题

如果遇到Docker权限错误：

```bash
# 将用户添加到docker组（需要重启终端）
sudo usermod -aG docker $USER
```

### 端口冲突

如果端口被占用：

```bash
# 查看端口占用
lsof -i :8000  # 后端端口
lsof -i :5173  # 前端端口
```

### 数据库连接问题

确保数据库服务正在运行，并且连接配置正确：

```bash
# 测试PostgreSQL连接
docker exec news_postgres psql -U postgres -d news_recommendation -c "SELECT version();"

# 测试Redis连接
docker exec news_redis redis-cli ping

# 测试Elasticsearch连接
curl http://localhost:9200/_cluster/health
```