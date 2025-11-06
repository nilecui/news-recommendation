import React, { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, Typography, message, Divider } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { Helmet } from 'react-helmet-async'

import { useAuthStore } from '@/store/authStore'
import { LoginCredentials } from '@/types'
import { handleApiError } from '@/utils/errorHandling'

const { Title, Text } = Typography

const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const { login, isAuthenticated, isLoading, error, clearError } = useAuthStore()

  useEffect(() => {
    // Redirect if already authenticated
    if (isAuthenticated) {
      navigate('/', { replace: true })
    }

    // Clear any previous errors when component mounts
    clearError()
  }, [isAuthenticated, navigate, clearError])

  useEffect(() => {
    if (error) {
      message.error(error)
      clearError()
    }
  }, [error, clearError])

  const onFinish = async (values: LoginCredentials) => {
    try {
      await login(values)
      message.success('登录成功！')
      navigate('/', { replace: true })
    } catch (error) {
      handleApiError(error, '登录失败，请检查用户名和密码')
    }
  }

  return (
    <>
      <Helmet>
        <title>登录 - 新闻推荐系统</title>
        <meta name="description" content="登录新闻推荐系统，获取个性化新闻推荐" />
      </Helmet>

      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <Title level={2}>欢迎回来</Title>
            <Text type="secondary">登录到您的账户</Text>
          </div>

          <Card className="shadow-lg">
            <Form
              name="login"
              onFinish={onFinish}
              layout="vertical"
              size="large"
              autoComplete="off"
            >
              <Form.Item
                label="邮箱"
                name="email"
                rules={[
                  { required: true, message: '请输入邮箱地址' },
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input
                  prefix={<UserOutlined className="text-gray-400" />}
                  placeholder="请输入邮箱地址"
                  autoComplete="email"
                />
              </Form.Item>

              <Form.Item
                label="密码"
                name="password"
                rules={[
                  { required: true, message: '请输入密码' },
                  { min: 6, message: '密码至少6个字符' }
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined className="text-gray-400" />}
                  placeholder="请输入密码"
                  autoComplete="current-password"
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={isLoading}
                  block
                  className="h-12 text-base"
                >
                  {isLoading ? '登录中...' : '登录'}
                </Button>
              </Form.Item>
            </Form>

            <Divider>或</Divider>

            <div className="text-center space-y-4">
              <div>
                <Text type="secondary">
                  还没有账户？{' '}
                  <Link to="/auth/register" className="text-blue-600 hover:text-blue-500">
                    立即注册
                  </Link>
                </Text>
              </div>

              <div>
                <Link to="/auth/forgot-password" className="text-sm text-blue-600 hover:text-blue-500">
                  忘记密码？
                </Link>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </>
  )
}

export default LoginPage