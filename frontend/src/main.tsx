import React, { useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { ConfigProvider } from 'antd'
import { HelmetProvider } from 'react-helmet-async'
import zhCN from 'antd/locale/zh_CN'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

import App from './App.tsx'
import './index.css'
import { useAuthStore } from './store/authStore'

// Configure dayjs for Chinese locale
dayjs.locale('zh-cn')

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
    mutations: {
      retry: 1,
    },
  },
})

// Initialize auth before rendering app
const AppWithAuth = () => {
  const initialize = useAuthStore((state) => state.initialize)

  useEffect(() => {
    initialize()
  }, [initialize])

  return <App />
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <ConfigProvider locale={zhCN}>
          <BrowserRouter>
            <AppWithAuth />
          </BrowserRouter>
        </ConfigProvider>
      </QueryClientProvider>
    </HelmetProvider>
  </React.StrictMode>,
)