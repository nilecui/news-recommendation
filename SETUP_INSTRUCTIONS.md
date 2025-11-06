# 新闻推荐系统设置说明

## 当前状态

✅ **已完成的功能:**
- 完整的项目架构和目录结构
- FastAPI后端基础框架
- React前端基础框架
- JWT用户认证系统
- 数据库模型设计
- Docker配置文件

## 解决Docker权限问题的替代方案

由于Docker权限问题，我们提供了几种启动方案：

### 方案1：使用启动脚本（推荐）

```bash
# 1. 给脚本执行权限
chmod +x start-dev.sh stop-dev.sh

# 2. 启动服务
./start-dev.sh
```

这将自动处理：
- Python虚拟环境激活
- 后端依赖安装
- 数据库初始化（使用SQLite）
- FastAPI服务器启动（端口8000）
- React开发服务器启动（端口5173）

### 方案2：手动分步启动

#### 启动后端
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 创建数据库表
python -c "
from app.config.database import engine
from app.models import *
Base.metadata.create_all(bind=engine)
print('数据库表创建成功')
"

# 启动API服务器
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 启动前端（新终端）
```bash
# 安装依赖
cd frontend
npm install

# 启动开发服务器
npm run dev
```

### 方案3：仅前端演示（无需数据库）

如果想快速查看前端界面：

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 查看界面（API调用会失败，但可以看到UI）

## 环境配置

当前已配置的开发环境变量：

**后端 (.env):**
- 使用SQLite数据库（无需额外数据库服务）
- 开发模式调试已启用
- JWT令牌有效期设置为60分钟

**前端 (.env):**
- API地址设置为 http://localhost:8000/api/v1
- 开发模式已启用

## 访问地址

启动成功后，可以访问：

- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **交互式API**: http://localhost:8000/redoc

## 测试认证功能

1. 访问 http://localhost:5173/auth/register 注册新用户
2. 使用注册的邮箱和密码登录
3. 成功登录后会重定向到首页

## 故障排除

### 依赖安装失败
如果pip install失败，可以尝试：
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-deps
```

### 端口占用
如果端口被占用：
```bash
# 查看进程
lsof -i :8000  # 后端
lsof -i :5173  # 前端

# 杀死进程
kill -9 <PID>
```

### Python版本问题
确保使用Python 3.9+：
```bash
python --version  # 应该是3.9或更高版本
```

## 下一步开发计划

待实现的功能：
1. **新闻爬虫系统** - 自动采集新闻内容
2. **推荐算法** - 个性化新闻推荐
3. **前端组件完善** - 新闻卡片、搜索等
4. **用户行为追踪** - 阅读记录、偏好分析

当前基础架构已经完整，可以开始开发这些核心功能。