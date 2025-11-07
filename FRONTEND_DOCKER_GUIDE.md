# 前端 Docker 启动指南

## 方式一：使用独立的前端 docker-compose 文件（推荐）

如果你只想启动前端，后端已经在宿主机上运行（如 `uvicorn app.main:app --host 0.0.0.0 --port 8311`），可以使用：

```bash
# 启动前端
docker-compose -f docker-compose-frontend.yml up --build -d

# 查看日志
docker logs -f news_frontend

# 停止前端
docker-compose -f docker-compose-frontend.yml down
```

或者使用脚本：
```bash
./start-frontend.sh
```

## 方式二：使用完整 docker-compose.yml

如果你想同时启动所有服务（包括后端、数据库等），可以使用：

```bash
# 启动所有服务
docker-compose up --build -d

# 只启动前端服务
docker-compose up frontend --build -d

# 查看前端日志
docker logs -f news_frontend

# 停止所有服务
docker-compose down
```

## 配置说明

### API 地址配置

前端通过环境变量 `VITE_API_BASE_URL` 配置后端 API 地址：

- **后端在 Docker 网络中**: `http://backend:8000/api/v1`
- **后端在宿主机上**: `http://192.168.12.225:8311/api/v1`（当前配置）

### 修改 API 地址

编辑 `docker-compose-frontend.yml` 文件，修改环境变量：

```yaml
environment:
  - VITE_API_BASE_URL=http://你的后端地址:端口/api/v1
  - VITE_API_URL=http://你的后端地址:端口/api/v1
```

### 端口配置

- 前端开发服务器端口: `3000`
- 访问地址: `http://localhost:3000`

## 开发模式特性

- ✅ 热重载：修改代码自动刷新
- ✅ 源码映射：方便调试
- ✅ 实时编译：TypeScript 和 React 代码实时编译
- ✅ 代理配置：自动代理 `/api` 请求到后端

## 故障排查

### 1. 容器无法启动

```bash
# 查看容器日志
docker logs news_frontend

# 检查端口是否被占用
netstat -tuln | grep 3000
```

### 2. 无法连接到后端 API

- 检查后端是否正在运行
- 检查 `VITE_API_BASE_URL` 环境变量是否正确
- 检查网络连接（如果后端在宿主机上，确保 Docker 可以访问宿主机网络）

### 3. 修改代码不生效

- 确保使用了开发模式的 Dockerfile (`Dockerfile.dev`)
- 检查 volume 挂载是否正确
- 重启容器：`docker-compose -f docker-compose-frontend.yml restart`

## 生产环境部署

生产环境使用 `Dockerfile`（构建 + Nginx），而不是 `Dockerfile.dev`：

```bash
# 构建生产镜像
docker build -f frontend/Dockerfile -t news-frontend:prod ./frontend

# 运行生产容器
docker run -d -p 80:80 news-frontend:prod
```

