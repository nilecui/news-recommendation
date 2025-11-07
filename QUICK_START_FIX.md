# 快速启动指南 - 修复版

## ⚠️ 如果遇到启动错误

如果看到以下错误：
```
pydantic_core._pydantic_core.ValidationError: 2 validation errors for Settings
SECRET_KEY
  Field required [type=missing, input_value={}, input_type=dict]
DATABASE_URL
  Field required [type=missing, input_value={}, input_type=dict]
```

**原因**：缺少环境配置文件 `.env`

---

## ✅ 解决方案（3步）

### 1️⃣ 确认.env文件存在

```bash
cd /bigdata/cuiweitie/claude_code_wk/reco_new_wk/news-recommendation/backend

# 检查.env文件是否存在
ls -la .env

# 如果不存在，复制示例文件
cp .env.example .env
```

### 2️⃣ 初始化数据库（SQLite版本，无需安装PostgreSQL）

```bash
# 创建数据库迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 3️⃣ 启动应用

```bash
# 激活虚拟环境（如果还没激活）
source ../venv/bin/activate

# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8311 --reload
```

---

## 🚀 正确的启动流程

### 后端启动

```bash
# 1. 进入后端目录
cd /bigdata/cuiweitie/claude_code_wk/reco_new_wk/news-recommendation/backend

# 2. 激活虚拟环境
source ../venv/bin/activate

# 3. 确保.env文件存在
test -f .env && echo "✅ .env exists" || echo "❌ .env missing - please create it"

# 4. 安装依赖（如果还没安装）
pip install -r requirements.txt

# 5. 初始化数据库（首次运行）
alembic upgrade head

# 6. 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8311 --reload
```

### 前端启动

```bash
# 1. 进入前端目录
cd /bigdata/cuiweitie/claude_code_wk/reco_new_wk/news-recommendation/frontend

# 2. 安装依赖（如果还没安装）
npm install
# 或
pnpm install

# 3. 启动开发服务器
npm run dev
# 或
pnpm dev
```

---

## 🔧 配置说明

### .env文件配置项

默认配置使用**SQLite**数据库，无需安装PostgreSQL：

```ini
# 数据库 - 默认使用SQLite（无需额外配置）
DATABASE_URL=sqlite:///./news_recommendation.db

# 如果要使用PostgreSQL，取消注释下面这行：
# DATABASE_URL=postgresql://postgres:password@localhost:5432/news_recommendation
```

### 可选服务

以下服务是**可选的**，应用可以在没有它们的情况下运行（会有警告）：

- **Redis**: 用于缓存和任务队列
- **Elasticsearch**: 用于全文搜索
- **Celery**: 用于后台任务

如果要完整体验，可以使用Docker启动这些服务：

```bash
# 使用docker-compose启动所有依赖服务
cd /bigdata/cuiweitie/claude_code_wk/reco_new_wk/news-recommendation
docker-compose up -d postgres redis elasticsearch
```

---

## 📝 验证安装

### 检查后端是否正常运行

```bash
# 访问API文档
curl http://localhost:8311/docs

# 或在浏览器打开
# http://localhost:8311/docs
```

### 检查前端是否正常运行

```bash
# 浏览器访问
# http://localhost:5173
```

---

## 🐛 常见问题

### 问题1: 端口被占用

```bash
# 错误信息: Address already in use
# 解决方法: 更换端口
uvicorn app.main:app --host 0.0.0.0 --port 8312 --reload
```

### 问题2: 数据库迁移失败

```bash
# 删除旧的迁移和数据库
rm -rf alembic/versions/*.py
rm news_recommendation.db

# 重新创建迁移
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 问题3: Redis连接失败

```bash
# 如果没有Redis，应用仍可运行（会有警告）
# 或者启动Redis:
docker run -d -p 6379:6379 redis:7-alpine
```

---

## 📚 完整文档

详细文档请参考：
- [完整安装说明](./SETUP_INSTRUCTIONS.md)
- [架构设计](./CLAUDE.md)
- [API文档](http://localhost:8311/docs) （启动后端后访问）

---

## ✅ 启动成功标志

后端启动成功后，你应该看到：

```
INFO:     Uvicorn running on http://0.0.0.0:8311 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

前端启动成功后，你应该看到：

```
  VITE vX.X.X  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```
