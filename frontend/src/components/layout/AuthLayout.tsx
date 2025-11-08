import React from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Layout, Typography } from 'antd'

const { Content } = Layout
const { Title, Text } = Typography

const AuthLayout: React.FC = () => {
  const location = useLocation()
  const isLoginPage = location.pathname === '/auth/login'
  
  // For login page, render without layout wrapper to allow full-page styling
  if (isLoginPage) {
    return <Outlet />
  }

  return (
    <Layout className="min-h-screen bg-gray-50">
      <Content className="flex flex-col">
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <Title level={3} className="!mb-0 text-blue-600">
                  新闻推荐系统
                </Title>
              </div>
            </div>
          </div>
        </header>

        <main className="flex-grow">
          <Outlet />
        </main>

        <footer className="bg-white border-t border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="text-center text-gray-500 text-sm">
              <Text type="secondary">
                © 2024 新闻推荐系统. 保留所有权利.
              </Text>
            </div>
          </div>
        </footer>
      </Content>
    </Layout>
  )
}

export default AuthLayout