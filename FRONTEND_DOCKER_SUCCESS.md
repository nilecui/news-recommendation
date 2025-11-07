# 前端 Docker 启动成功 ✅

## 启动状态

前端容器已成功启动并运行！

- **容器名称**: `news_frontend`
- **访问地址**: http://localhost:3000
- **后端 API**: http://192.168.12.225:8311/api/v1
- **开发模式**: ✅ 已启用（支持热重载）

## 快速启动命令

### 方式一：使用脚本（推荐）

```bash
./start-frontend.sh
```

### 方式二：使用 docker-compose

```bash
# 启动前端
docker-compose -f docker-compose-frontend.yml up --build -d

# 查看日志
docker logs -f news_frontend

# 停止前端
docker-compose -f docker-compose-frontend.yml down
```

## 已完成的配置

1. ✅ 创建了开发模式 Dockerfile (`frontend/Dockerfile.dev`)
2. ✅ 创建了独立的前端 docker-compose 文件 (`docker-compose-frontend.yml`)
3. ✅ 更新了 `package.json` 添加缺失的依赖 (`react-helmet-async`)
4. ✅ 配置了 API 地址环境变量
5. ✅ 更新了 Vite 配置支持 Docker 网络

## 访问前端

打开浏览器访问: **http://localhost:3000**

## 开发特性

- ✅ **热重载**: 修改代码自动刷新浏览器
- ✅ **源码映射**: 方便调试 TypeScript 代码
- ✅ **实时编译**: Vite 实时编译 React 代码
- ✅ **代理配置**: 自动代理 `/api` 请求到后端

## 修改 API 地址

如果需要修改后端 API 地址，编辑 `docker-compose-frontend.yml`:

```yaml
environment:
  - VITE_API_BASE_URL=http://你的后端地址:端口/api/v1
```

然后重启容器：
```bash
docker-compose -f docker-compose-frontend.yml restart
```

## 常用命令

```bash
# 查看日志
docker logs -f news_frontend

# 进入容器
docker exec -it news_frontend sh

# 重启容器
docker-compose -f docker-compose-frontend.yml restart

# 停止容器
docker-compose -f docker-compose-frontend.yml down

# 重新构建并启动
docker-compose -f docker-compose-frontend.yml up --build -d
```

## 故障排查

### 1. 无法访问前端

```bash
# 检查容器是否运行
docker ps | grep news_frontend

# 检查端口是否被占用
netstat -tuln | grep 3000

# 查看容器日志
docker logs news_frontend
```

### 2. 无法连接到后端 API

- 确保后端服务正在运行: `http://192.168.12.225:8311`
- 检查环境变量 `VITE_API_BASE_URL` 是否正确
- 在浏览器开发者工具中查看网络请求

### 3. 修改代码不生效

- 确保使用了 `Dockerfile.dev`（开发模式）
- 检查 volume 挂载是否正确
- 重启容器: `docker-compose -f docker-compose-frontend.yml restart`

## 下一步

1. 打开浏览器访问 http://localhost:3000
2. 测试登录功能（使用已注册的账号）
3. 测试各个页面和功能
4. 查看浏览器控制台和网络请求

## 注意事项

- 前端运行在开发模式，适合开发和调试
- 生产环境请使用 `Dockerfile`（构建 + Nginx）
- 确保后端服务已启动并可以访问
- Docker 容器内的前端可以访问宿主机上的后端服务

