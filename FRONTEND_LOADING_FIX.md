# 前端页面加载问题修复说明

## 问题分析

页面一直转圈的原因：

1. **Auth 初始化问题**：`App.tsx` 中检查 `isInitialized`，但 `initialize` 方法只在 `ProtectedRoute` 中调用。如果用户未登录，`isInitialized` 会一直为 `false`，导致一直显示加载屏幕。

2. **WebSocket 连接**：Vite 的 HMR WebSocket 连接正常（状态码 101），但这不是导致页面加载问题的原因。

3. **控制台警告**：
   - React DevTools 提示：正常，不影响功能
   - React Router 未来标志警告：正常，不影响功能
   - Chrome 扩展错误：浏览器扩展问题，不影响应用

## 修复方案

### 1. 在应用启动时初始化 Auth

修改 `frontend/src/main.tsx`，在应用启动时调用 `initialize`：

```typescript
const AppWithAuth = () => {
  const initialize = useAuthStore((state) => state.initialize)

  useEffect(() => {
    initialize()
  }, [initialize])

  return <App />
}
```

### 2. 改进 Auth Store 的错误处理

更新 `frontend/src/store/authStore.ts` 中的 `initialize` 方法：
- 添加重复初始化检查
- 改进错误处理，401 错误时静默清除 token
- 确保 `isInitialized` 始终会被设置为 `true`

### 3. 修复 Vite WebSocket 配置

更新 `frontend/vite.config.ts`，配置 HMR WebSocket：

```typescript
server: {
  host: '0.0.0.0',
  port: 3000,
  hmr: {
    host: 'localhost',
    port: 3000,
  },
  // ...
}
```

## 测试

修复后，页面应该能够正常加载：

1. **未登录用户**：会显示登录页面
2. **已登录用户**：会显示主页
3. **Token 过期**：会自动清除 token 并跳转到登录页

## 验证步骤

1. 清除浏览器缓存和 localStorage（可选）
2. 刷新页面 `http://localhost:3000`
3. 应该能看到登录页面，而不是一直转圈

## 如果问题仍然存在

检查浏览器控制台：
- 查看 Network 标签，检查 API 请求是否成功
- 查看 Console 标签，检查是否有错误信息
- 检查后端服务是否正常运行：`http://192.168.12.225:8311/api/v1/health`

## 关于 WebSocket 连接

WebSocket 连接 `ws://192.168.12.225:3000/?token=...` 是 Vite 的 HMR（热模块替换）功能，用于开发时的热重载。状态码 101 表示连接成功，这是正常的。如果 WebSocket 连接失败，只会影响热重载功能，不会影响页面加载。

