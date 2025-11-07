# CORS 配置修复说明

## 问题

前端访问后端 API 时出现 CORS 错误：
```
Access to XMLHttpRequest at 'http://192.168.12.225:8311/api/v1/auth/login' 
from origin 'http://192.168.12.225:3000' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## 原因

后端的 CORS 配置中 `ALLOWED_HOSTS` 只包含：
- `http://localhost:3000`
- `http://127.0.0.1:3000`

但前端实际运行在 `http://192.168.12.225:3000`，不在允许列表中。

## 修复

### 1. 更新 settings.py 默认值

已在 `backend/app/config/settings.py` 中添加：
```python
ALLOWED_HOSTS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.12.225:3000",  # Frontend Docker container
]
```

### 2. 更新 .env 文件

`.env` 文件中的 `ALLOWED_HOSTS` 已更新为：
```ini
ALLOWED_HOSTS=["http://localhost:3000","http://127.0.0.1:3000","http://192.168.12.225:3000"]
```

### 3. 重启后端服务

**重要**：需要重启后端服务才能使配置生效！

如果后端使用 `uvicorn` 运行：
```bash
# 找到进程 ID
ps aux | grep "uvicorn app.main:app"

# 停止服务（在运行 uvicorn 的终端按 Ctrl+C）
# 或者使用 kill 命令
kill <PID>

# 重新启动
cd backend
source ../venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8311 --reload
```

## 验证

重启后端后，在浏览器中测试登录功能，CORS 错误应该消失。

## 其他警告说明

以下警告是正常的，不影响功能：

1. **React DevTools 提示**：建议安装 React DevTools 浏览器扩展
2. **React Router 未来标志警告**：React Router v7 的兼容性提示，不影响当前功能
3. **Chrome 扩展错误**：浏览器扩展的问题，不影响应用
4. **Antd message 警告**：建议使用 `App` 组件包裹应用以支持动态主题

