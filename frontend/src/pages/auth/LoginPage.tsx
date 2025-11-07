import React, { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, Typography, message, Divider, Space } from 'antd'
import { UserOutlined, LockOutlined, RightOutlined } from '@ant-design/icons'
import { Helmet } from 'react-helmet-async'

import { useAuthStore } from '@/store/authStore'
import { LoginCredentials } from '@/types'
import { handleApiError } from '@/utils/errorHandling'
import './LoginPage.css'

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

      <div className="login-page">
        {/* Background with animated gradient */}
        <div className="login-background">
          <div className="gradient-blob blob-1"></div>
          <div className="gradient-blob blob-2"></div>
          <div className="gradient-blob blob-3"></div>
        </div>

        <div className="login-container">
          <div className="login-content fade-in-scale">
            {/* Logo and Header */}
            <div className="login-header">
              <div className="logo-container">
                <div className="logo-circle gradient-bg">
                  <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                    <path d="M20 5L25 15H35L27 22L30 32L20 26L10 32L13 22L5 15H15L20 5Z" fill="white"/>
                  </svg>
                </div>
                <Title level={3} className="logo-text">
                  新闻推荐系统
                </Title>
              </div>
              <Title level={2} className="welcome-title">
                欢迎回来
              </Title>
              <Text className="welcome-subtitle">
                登录到您的账户，发现精彩内容
              </Text>
            </div>

            {/* Login Card */}
            <Card className="login-card glass-effect" bordered={false}>
              <Form
                name="login"
                onFinish={onFinish}
                layout="vertical"
                size="large"
                autoComplete="off"
              >
                <Form.Item
                  label={<span className="form-label">邮箱</span>}
                  name="email"
                  rules={[
                    { required: true, message: '请输入邮箱地址' },
                    { type: 'email', message: '请输入有效的邮箱地址' }
                  ]}
                >
                  <Input
                    prefix={<UserOutlined className="input-icon" />}
                    placeholder="请输入邮箱地址"
                    autoComplete="email"
                    className="modern-input"
                  />
                </Form.Item>

                <Form.Item
                  label={<span className="form-label">密码</span>}
                  name="password"
                  rules={[
                    { required: true, message: '请输入密码' },
                    { min: 6, message: '密码至少6个字符' }
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined className="input-icon" />}
                    placeholder="请输入密码"
                    autoComplete="current-password"
                    className="modern-input"
                  />
                </Form.Item>

                <Form.Item style={{ marginBottom: 16 }}>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={isLoading}
                    block
                    className="login-button gradient-bg"
                    icon={!isLoading && <RightOutlined />}
                    iconPosition="end"
                  >
                    {isLoading ? '登录中...' : '登录'}
                  </Button>
                </Form.Item>
              </Form>

              <Divider className="divider-text">或</Divider>

              <div className="login-footer">
                <Space direction="vertical" size="middle" className="w-full">
                  <div className="text-center">
                    <Text type="secondary">
                      还没有账户？{' '}
                      <Link to="/auth/register" className="link-gradient">
                        立即注册
                      </Link>
                    </Text>
                  </div>

                  <div className="text-center">
                    <Link to="/auth/forgot-password" className="forgot-link">
                      忘记密码？
                    </Link>
                  </div>
                </Space>
              </div>
            </Card>

            {/* Features */}
            <div className="features-container">
              <Space size="large" wrap>
                <div className="feature-item">
                  <div className="feature-icon">✨</div>
                  <Text className="feature-text">智能推荐</Text>
                </div>
                <div className="feature-item">
                  <div className="feature-icon">📱</div>
                  <Text className="feature-text">实时更新</Text>
                </div>
                <div className="feature-item">
                  <div className="feature-icon">🔐</div>
                  <Text className="feature-text">安全可靠</Text>
                </div>
              </Space>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="login-page-footer">
          <Text type="secondary" className="footer-text">
            © 2024 新闻推荐系统. 保留所有权利.
          </Text>
        </div>
      </div>
    </>
  )
}

export default LoginPage
