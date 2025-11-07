# 测试模块说明

## 测试结构

```
backend/tests/
├── __init__.py          # 测试包初始化
├── conftest.py          # pytest 配置和 fixtures
├── test_utils.py        # 测试工具函数（SQLite 兼容性）
├── test_basic.py        # 基础端点测试（健康检查、根路径）
├── test_auth.py         # 认证相关测试
├── test_users.py        # 用户管理测试
├── test_news.py         # 新闻相关测试
├── test_recommendations.py  # 推荐系统测试
└── test_tracking.py     # 行为追踪测试
```

## 运行测试

```bash
cd backend
source ../venv/bin/activate

# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_auth.py -v

# 运行特定测试类
pytest tests/test_auth.py::TestAuth -v

# 运行特定测试方法
pytest tests/test_auth.py::TestAuth::test_register_user_success -v

# 生成覆盖率报告（需要安装 pytest-cov）
pytest tests/ --cov=app --cov-report=html
```

## 测试配置

- **测试数据库**: SQLite 内存数据库（`:memory:`）
- **ARRAY 类型兼容**: 使用 `JSONList` 类型装饰器将 PostgreSQL ARRAY 转换为 JSON 字符串
- **Fixtures**: 
  - `db_session`: 数据库会话
  - `client`: 测试客户端
  - `test_user`: 测试用户
  - `test_user_token`: 用户访问令牌
  - `authenticated_client`: 已认证的测试客户端
  - `test_category`: 测试新闻分类
  - `test_news`: 测试新闻

## 测试覆盖

### ✅ 已测试的接口

1. **基础端点**
   - `/health` - 健康检查
   - `/` - 根路径

2. **认证接口**
   - `POST /api/v1/auth/register` - 用户注册
   - `POST /api/v1/auth/login` - 用户登录
   - `GET /api/v1/users/me` - 获取当前用户信息

3. **用户接口**
   - `GET /api/v1/users/me` - 获取当前用户
   - `PUT /api/v1/users/me` - 更新用户信息
   - `GET /api/v1/users/me/profile` - 获取用户资料
   - `PUT /api/v1/users/me/profile` - 更新用户资料

### ⚠️ 需要修复的测试

部分测试失败是因为：
1. 服务方法名称或签名与实际实现不匹配
2. 需要根据实际的服务接口调整测试用例
3. 某些功能可能尚未实现

## 注意事项

1. **SQLite 兼容性**: 测试使用 SQLite 内存数据库，某些 PostgreSQL 特性（如 ARRAY）已通过 `JSONList` 类型装饰器处理
2. **依赖注入**: 测试通过 `app.dependency_overrides` 覆盖数据库依赖
3. **异步支持**: 使用 `pytest-asyncio` 支持异步测试
4. **测试隔离**: 每个测试使用独立的数据库会话，确保测试之间不相互影响

## 下一步

1. 根据实际的服务接口调整测试用例
2. 添加更多边界情况测试
3. 添加集成测试
4. 设置 CI/CD 自动运行测试

